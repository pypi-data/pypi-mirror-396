from __future__ import annotations

import base64
import json
import os
import random
import re
import time
import uuid

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, Iterable, Optional
import pandas as pd

from .agent_config import AgentConfig
from .agent_tools import (DEFAULT_TOOL_NAMES, ToolExecutionPolicy, ToolExecutionResult, build_tool_schemas,
                          execute_tool_with_policy, exec_tool, get_builtin_tools)
from .helpers import log_msg, ToolContext, ToolFn, render_file_as_content_blocks, create_working_folder
from .rag.sql_repository import SqlRepository
from .converters import convert_markdown_to_html_block, convert_json_to_csv


def _approx_token_count(text: str) -> int:
    """Estimate token usage based on word count heuristics.

    Args:
        text (str): Conteúdo textual cujo total aproximado de tokens será calculado.

    Returns:
        int: Estimativa de tokens, assumindo média de 0,75 palavra por token.
    """
    words = len(re.findall(r"\S+", text))
    return max(1, int(words / 0.75))


def get_base_url() -> str | None:
    """Read the OpenAI base URL from the repository-level `keys.yaml`.

    Returns:
        str | None: URL configurada ou `None` quando não encontrada.
    """
    try:
        root = Path(__file__).resolve().parent.parent  # project root
        keys_path = root / "keys.yaml"
        if not keys_path.exists():
            return None
        for raw in keys_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or not line.startswith("OPENAI_BASE_URL"):
                continue
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue
            val = parts[1].strip().strip("'\"")
            return val or None
        return None
    except Exception:
        return None


@dataclass(slots=True)
class ResiliencePolicy:
    """Políticas de resiliência aplicadas nas chamadas ao LLM e ferramentas (ver docs/ADR-setup-agent-refactor.md)."""

    max_llm_attempts: int = 3
    llm_timeout_seconds: float = 120.0
    backoff_base_seconds: float = 2.0
    backoff_jitter_seconds: float = 1.0
    max_tool_iterations: int = 3
    tool_timeout_seconds: float = 20.0
    tool_timeouts: dict[str, float] | None = None


class Oskar:
    def __init__(self,
                 agent_config: AgentConfig | None = None,
                 input_data: dict | None = None,
                 session_id: str | None = None,
                 session_name: str | None = None,
                 session_created_at: datetime | None = None,
                 session_updated_at: datetime | None = None,
                 working_folder: str | None = None,
                 is_verbose: bool = False,
                 response_callback: Callable[[dict[str, Any]], None] | None = None,
                 get_builtin_custom_tools_fn: Callable[..., dict[str, ToolFn]] | None = None,
                 build_custom_tool_schemas_fn: Callable[
                                                   [Iterable[str], Optional[dict]], list[dict[str, Any]]] | None = None,
                 exec_custom_tool_fn: Callable[[str, Callable[..., Any], dict[str, Any], ToolContext,
                                                Optional[dict]], Any] | None = None,
                 openai_client: Any | None = None,
                 clock: Callable[[], datetime] | None = None,
                 rng: random.Random | None = None,
                 resilience_policy: ResiliencePolicy | None = None):
        """Instantiate the oskaragent agent with configuration, session, and tooling data.

        Args:
            agent_config (AgentConfig | None, optional): Configuração específica do agente. Defaults to None.
            input_data (dict | None, optional): Dados auxiliares repassados aos prompts. Defaults to None.
            session_id (str | None, optional): Identificador único da sessão corrente. Defaults to None.
            session_name (str | None, optional): Nome amigável associado à sessão. Defaults to None.
            session_created_at (datetime | None, optional): Data/hora de criação da sessão. Defaults to now().
            session_updated_at (datetime | None, optional): Última atualização registrada para a sessão. Defaults to now().
            working_folder (str | None, optional): Diretório base para arquivos temporários/output. Defaults to None.
            is_verbose (bool, optional): Indica se logs detalhados devem ser emitidos. Defaults to False.
            response_callback (Callable[[dict[str, Any]], None] | None, optional): Callback executado após gerar respostas. Defaults to None.
            get_builtin_custom_tools_fn (Callable[..., dict[str, ToolFn]] | None, optional): Função de fábrica para carregar ferramentas CG personalizadas. Defaults to None.
            build_custom_tool_schemas_fn (Callable[[Iterable[str], Optional[dict]], list[dict[str, Any]]] | None, optional): Construtor alternativo para schemas de ferramentas personalizados. Defaults to None.
            exec_custom_tool_fn (Callable[[str, Callable[..., Any], dict[str, Any], ToolContext, Optional[dict]], Any] | None, optional): Executor customizado para ferramentas CG. Defaults to None.
            openai_client (Any | None, optional): Cliente OpenAI injetado para facilitar testes. Defaults to None.
            clock (Callable[[], datetime] | None, optional): Função usada para capturar o tempo atual. Defaults to datetime.now.
            rng (random.Random | None, optional): Gerador aleatório injetável para jitter e nomes. Defaults to random.Random().
            resilience_policy (ResiliencePolicy | None, optional): Política de resiliência aplicada ao agente. Defaults to valores padrão.

        Returns:
            None: O construtor apenas inicializa o estado interno.
        """
        # Dependencies
        self._clock: Callable[[], datetime] = clock or datetime.now
        self._rng: random.Random = rng or random.Random()

        # Config & session
        self.agent_config: AgentConfig = agent_config or AgentConfig()
        self.input_data: dict[str, Any] = input_data or {}
        self.session_id: str = session_id or str(uuid.uuid4())
        self.session_name: str | None = session_name
        self.session_created_at: datetime = session_created_at or self._clock()
        self.session_updated_at: datetime = session_updated_at or self._clock()
        self.working_folder: str | None = working_folder
        self._base_path: Path = Path(self.working_folder).resolve() if self.working_folder else Path.cwd().resolve()
        self.is_verbose: bool = is_verbose
        self._reasoning_effort: str | None = None
        self._resilience: ResiliencePolicy = resilience_policy or self._build_resilience_policy()

        # Tools
        self.tools: dict[str, Callable[..., Any]] = {}

        # History (structured records)
        self.message_history: list[dict[str, Any]] = []
        self.history_window_size: int = int((self.agent_config.model_settings or {}).get("history_window_size", 5))

        # RAG / retrieval
        self.retrievers: list[dict[str, Any]] = []

        # Client
        self._openai_client: Any | None = openai_client
        self._init_error_reason: str | None = None

        # Subordinate agents (for multi-agent)
        self.subordinated_agents = []

        # Callback and others functions
        self.response_callback = response_callback
        self._get_builtin_custom_tools_fn = get_builtin_custom_tools_fn
        self._build_custom_tool_schemas_fn = build_custom_tool_schemas_fn
        self._exec_custom_tool_fn = exec_custom_tool_fn
        self._custom_tools_names: set[str] = set()

        # system prompt prepared to be sent to LLM
        self._my_system_prompt = None

        # attached files
        self._attached_files = []

        # setup de agent
        self._setup_agent()

    def _build_resilience_policy(self) -> ResiliencePolicy:
        """Monta política de resiliência a partir das configurações do agente.

        Returns:
            ResiliencePolicy: Política consolidada para LLM e ferramentas, mantendo paridade com docs/ADR-setup-agent-refactor.md e os defaults seguros.
        """
        cfg = (self.agent_config.model_settings or {}).get("resilience", {})

        def _coerce_timeout_map(value: Any) -> dict[str, float]:
            """Normaliza os timeouts específicos por ferramenta.

            Args:
                value (Any): Estrutura de timeouts recebida via configuração do agente.

            Returns:
                dict[str, float]: Mapa normalizado de `nome_da_ferramenta -> timeout_em_segundos`.
            """
            if not isinstance(value, dict):
                return {}

            timeouts: dict[str, float] = {}
            for name, raw_timeout in value.items():
                try:
                    timeouts[str(name)] = float(raw_timeout)
                except Exception:
                    continue

            return timeouts

        def _coerce_int(value: Any, default: int) -> int:
            try:
                return int(value)
            except Exception:
                return default

        def _coerce_float(value: Any, default: float) -> float:
            try:
                return float(value)
            except Exception:
                return default

        # Permite que consultas mais pesadas do Salesforce concluam sem falso positivo de timeout.
        default_tool_timeouts = {"get_salesforce_opportunity_info_tool": 45.0}
        configured_timeouts = _coerce_timeout_map(cfg.get("tool_timeouts"))
        merged_tool_timeouts = {**default_tool_timeouts, **configured_timeouts}

        return ResiliencePolicy(
            max_llm_attempts=_coerce_int(cfg.get("max_llm_attempts"), 3),
            llm_timeout_seconds=_coerce_float(cfg.get("llm_timeout_seconds"), 120.0),
            backoff_base_seconds=_coerce_float(cfg.get("backoff_base_seconds"), 2.0),
            backoff_jitter_seconds=_coerce_float(cfg.get("backoff_jitter_seconds"), 1.0),
            max_tool_iterations=_coerce_int(cfg.get("max_tool_iterations"), 3),
            tool_timeout_seconds=_coerce_float(cfg.get("tool_timeout_seconds"), 20.0),
            tool_timeouts=merged_tool_timeouts,
        )

    def _now(self) -> datetime:
        """Retorna o tempo atual usando a fonte de tempo injetada.

        Returns:
            datetime: Momento capturado com a função de relógio configurada (permite testes determinísticos).
        """
        return self._clock()

    def _ensure_session_working_folder(self) -> Path:
        """
        Garante que o diretório de trabalho da sessão exista e retorna seu caminho.

        Returns:
            
            Path: path to the session working folder
        """
        self.working_folder = create_working_folder(self.session_id)
        return Path(self.working_folder)

    def _remove_empty_session_working_folder(self):
        """
        Removes empty files and directories within the session working folder.

        This method ensures that the session working folder is cleaned up by
        removing any empty files and directories present within it. If the session
        directory itself becomes empty after the cleanup, it is also removed.

        Raises:
            FileNotFoundError: If the session working folder does not exist.

        """
        if not self.working_folder:
            return

        session_dir = Path(self.working_folder)
        for entry in session_dir.iterdir():
            if entry.is_file() and entry.stat().st_size == 0:
                entry.unlink()
        if not any(session_dir.iterdir()):
            session_dir.rmdir()

    @property
    def id(self) -> str:
        """str: Identificador atual do agente (alias para `agent_config.agent_name`)."""
        return self.agent_config.agent_name

    @property
    def name(self) -> str:
        """str: Nome exposto do agente."""
        return self.agent_config.agent_name

    @property
    def description(self) -> str:
        """str: Descrição textual do agente."""
        return self.agent_config.description

    @description.setter
    def description(self, value: str):
        """Atualiza a descrição pública do agente."""
        self.agent_config.description = value

    @property
    def model(self) -> str:
        """str: Nome do modelo configurado para o agente."""
        return self.agent_config.model

    @property
    def reasoning_effort(self):
        """str: Modo de raciocínio atual do agente."""
        return self._reasoning_effort

    @reasoning_effort.setter
    def reasoning_effort(self, value: str):
        """Define o modo de raciocínio do agente."""
        if value is not None:
            if value not in ["none", "low", "medium", "high"]:
                raise ValueError(f"Invalid mode: {value}. Valid modes are: none, low, medium, high")
            if value == "none":
                value = None
        self._reasoning_effort = value

    def to_json(self) -> dict[str, Any]:
        """Export the agent state to a JSON-serializable structure.

        Returns:
            dict[str, Any]: Dicionário contendo configuração, sessão, estado e histórico do agente.
        """
        return {
            "agent_config": self.agent_config.to_json(),
            "session": {
                "id": self.session_id,
                "name": self.session_name,
                "created_at": self.session_created_at.isoformat(),
                "updated_at": self.session_updated_at.isoformat(),
                "working_folder": self.working_folder,
                "is_verbose": self.is_verbose,
                "history_window_size": self.history_window_size,
                "reasoning_effort": self.reasoning_effort,
            },
            "state": {
                "tools_available": sorted(self.tools.keys()),
                "rag_enabled": len(self.retrievers) > 0,
                "openai_ready": self._openai_client is not None,
                "model_name": self.agent_config.model,
            },
            "message_history": self.message_history,
            "subordinated_agents": [a.to_json() for a in self.subordinated_agents or []],
            "attached_files": self._attached_files,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any], working_folder: str) -> "oskaragent":
        """Rehydrate an agent instance from serialized state.

        Args:
            data (dict[str, Any]): Estrutura previamente gerada por `to_json`.
            working_folder: pasta de trabalho.

        Returns:
            Oskar: Nova instância com configuração, sessão e histórico restaurados.
        """
        cfg_json = (data or {}).get("agent_config") or {}
        agent_cfg = AgentConfig(json_config=cfg_json)

        sess = (data or {}).get("session") or {}

        def _parse_dt(val: Any, default: datetime) -> datetime:
            """Parse ISO-8601 strings into datetime objects, falling back to a default.

            Args:
                val (Any): Valor potencialmente representando uma data/hora.
                default (datetime): Data padrão utilizada em caso de falha.

            Returns:
                datetime: Data convertida ou o valor padrão.
            """
            if isinstance(val, datetime):
                return val
            if isinstance(val, str) and val:
                try:
                    # Accept 'Z' suffix as UTC
                    v = val.replace("Z", "+00:00") if val.endswith("Z") else val
                    return datetime.fromisoformat(v)
                except Exception:
                    return default
            return default

        created_at = _parse_dt(sess.get("created_at"), datetime.now())
        updated_at = _parse_dt(sess.get("updated_at"), datetime.now())

        inst = cls(
            agent_config=agent_cfg,
            input_data={},
            session_id=sess.get("id"),
            session_name=sess.get("name"),
            session_created_at=created_at,
            session_updated_at=updated_at,
            working_folder=working_folder,
        )

        # Keep the original window size if present
        try:
            inst.history_window_size = int(sess.get("history_window_size", inst.history_window_size))
        except Exception:
            pass

        # Restore message history as-is
        mh = (data or {}).get("message_history")
        if isinstance(mh, list):
            inst.message_history = mh

        # Restore subordinated agents
        subordinated_agents = []
        for a in (data or {}).get("subordinated_agents", []):
            if isinstance(a, dict):
                # Recover from JSON
                subordinated_agents.append(cls.from_json(a, working_folder))
            else:
                # Recover from dict
                subordinated_agents.append(cls(
                    agent_config=AgentConfig(json_config=a.get("agent_config", {})), working_folder=working_folder),
                )

        # restore reasoning_effort
        inst.reasoning_effort = sess.get("reasoning_effort", None)

        # restore attached files
        inst._attached_files = sess.get("attached_files", [])

        return inst

    def add_subordinated_agent(self, subordinate_agent: Oskar, role: str = None) -> None:
        """Associate another oskaragent agent as a subordinate collaborator.

        Args:
            subordinate_agent (Oskar): Instância do agente subordinado a ser anexado.
            role (str, optional): Papel ou descrição do subordinado. Defaults to None.

        Returns:
            None: Atualiza a lista interna de agentes subordinados.
        """
        found_agent = next(
            (agent for agent in self.subordinated_agents if agent.name == subordinate_agent.name),
            None)

        if found_agent:
            # o agente já está associado
            return

        if role:
            subordinate_agent.description = role

        subordinate_agent.working_folder = self.working_folder
        subordinate_agent.is_verbose = self.is_verbose

        # adiciona o agente na lista de agentes subordinados
        self.subordinated_agents.append(subordinate_agent)

        # atualiza o system prompt para fazer referência ao novo agente
        self._my_system_prompt = self._prepare_system_prompt()


    def _setup_agent(self):
        """Prepare OpenAI client, retrieval stack, and tool registry.

        Returns:
            None: Todos os efeitos são aplicados diretamente no estado interno do agente.
        """
        self._configure_openai_client()
        self.retrievers = self._load_retrievers()
        self._prepare_working_databases()
        self.tools = self._build_tools_registry()

        self._my_system_prompt = self._prepare_system_prompt()

    def _configure_openai_client(self) -> None:
        """Inicializa o cliente OpenAI respeitando dependências injetadas.

        Returns:
            None: Configura `_openai_client` ou registra o motivo de falha para modo offline.
        """
        if self._openai_client is not None:
            return

        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # noqa: BLE001
            self._openai_client = None
            self._init_error_reason = f"Falha ao importar SDK OpenAI: {exc}"
            return

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or get_base_url()
        if not api_key:
            self._openai_client = None
            self._init_error_reason = "Variável de ambiente OPENAI_API_KEY não definida."
            return

        try:
            self._openai_client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        except Exception as exc:  # noqa: BLE001
            self._openai_client = None
            self._init_error_reason = f"Falha ao inicializar cliente OpenAI: {exc}"

    def _load_retrievers(self) -> list[dict[str, Any]]:
        """Carrega metadados de fontes RAG configuradas.

        Returns:
            list[dict[str, Any]]: Coleção de retrievers prontos para habilitar o RAG conforme agent_config.
        """
        retrievers: list[dict[str, Any]] = []
        for knowledge_base in self.agent_config.knowledge_base or []:
            kb_path = knowledge_base["folder"]
            kb_name = knowledge_base["name"]
            kb_collection = knowledge_base.get("collection", kb_name)

            try:
                retrievers.append(
                    {
                        "name": kb_name,
                        "details": {
                            "kb_path": kb_path,
                            "kb_collection": kb_collection
                        }
                    })
            except Exception as exc:  # noqa: BLE001
                log_msg(
                    f"Falha ao inicializar o RAG: '{kb_name}': {exc}",
                    func="_load_retrievers",
                    action="vectorstore",
                    color="YELLOW",
                )
        return retrievers

    def _prepare_working_databases(self) -> None:
        """Gera arquivos de apoio para bases relacionais declaradas no agente.

        Returns:
            None: Converte consultas declarativas em CSVs prontos para as ferramentas de análise em pandas.
        """
        working_dbs = self.agent_config.working_databases or []
        if not working_dbs:
            return

        folder = self._ensure_session_working_folder()
        for working_database in working_dbs:
            filename = (folder / f"{working_database['name']}.csv").resolve()

            if not filename.exists():
                log_msg(
                    f"Criando CSV a partir do banco de dados: {working_database['name']}",
                    func="_prepare_working_databases",
                    action="",
                    color="BLUE",
                )
                try:
                    rep = SqlRepository(working_database["connection_string"])
                    doc_data = rep.read(working_database["query"])
                    convert_json_to_csv(doc_data, str(filename))
                except Exception as exc:  # noqa: BLE001
                    log_msg(
                        f"Falha ao gerar CSV da base '{working_database['name']}': {exc}",
                        func="_prepare_working_databases",
                        action="",
                        color="RED",
                    )
                    continue

            if self.agent_config.working_files is None:
                self.agent_config.working_files = []

            self.agent_config.working_files.append({
                "name": working_database["name"],
                "description": working_database["description"],
                "pathname": str(filename)
            })

        python_repl_tool = 'execute_python_code_tool'
        if python_repl_tool not in self.agent_config.tools_names:
            self.agent_config.tools_names.append(python_repl_tool)

    def _build_tools_registry(self) -> dict[str, Callable[..., Any]]:
        """Combina ferramentas built-in, customizadas e filtradas por allowlist.

        Returns:
            dict[str, Callable[..., Any]]: Registro final de ferramentas habilitadas, respeitando allowlist e RAG (docs/ADR-setup-agent-refactor.md).
        """
        builtin = get_builtin_tools(working_folder=self.working_folder)
        custom_registry: dict[str, ToolFn] = {}

        if self._get_builtin_custom_tools_fn:
            try:
                custom_registry = self._get_builtin_custom_tools_fn(
                    working_folder=self.working_folder,
                    custom_tools=self.agent_config.custom_tools,
                )
                builtin.update(custom_registry)
            except Exception as exc:  # noqa: BLE001
                if self.is_verbose:
                    log_msg(f"Falha ao carregar ferramentas personalizadas da empresa: {exc}",
                            func="_build_tools_registry", action="tools", color="RED")

        tools_names = self.agent_config.tools_names or []
        if len(self.subordinated_agents) > 0 and "ask_to_agent_tool" not in tools_names:
            tools_names.append("ask_to_agent_tool")

        tools = {**builtin}
        allow = set(tools_names)
        if allow:
            allow.update(DEFAULT_TOOL_NAMES)
            if len(self.retrievers) > 0:
                allow.add("retriever_tool")
            tools = {k: v for k, v in tools.items() if k in allow}

        if len(self.retrievers) > 0 and "retriever_tool" not in tools and "retriever_tool" in builtin:
            tools["retriever_tool"] = builtin["retriever_tool"]
            log_msg("Ferramenta 'retriever_tool' habilitada (RAG ativo)", func="_build_tools_registry",
                    action="tools",
                    color="BLUE")

        if self._get_builtin_custom_tools_fn or self.agent_config.custom_tools:
            builtin_custom_tools = list(custom_registry.keys())
            if self.agent_config.custom_tools:
                builtin_custom_tools.extend((self.agent_config.custom_tools or {}).keys())
            self._custom_tools_names = {tool_name
                                        for tool_name in tools
                                        if tool_name in builtin_custom_tools}

        return tools

    def _make_tool_context(self, message_id: str) -> ToolContext:
        """Build the context object passed to tool executions.

        Args:
            message_id (str): Identificador da mensagem corrente.

        Returns:
            ToolContext: Estrutura com metadados de sessão, arquivos e agentes subordinados.
        """
        return ToolContext(
            agent_id=self.id,
            session_id=self.session_id,
            message_id=message_id,
            is_verbose=self.is_verbose,
            input_data=self.input_data or {},
            subordinate_agents=self.subordinated_agents,
            custom_tools_info=self.agent_config.custom_tools,
            retrievers=self.retrievers,
            working_folder=self.working_folder,
            knowledge_base=self.agent_config.knowledge_base
        )

    def _prepare_system_prompt(self) -> str:
        """Compose the system prompt enriched with contextual instructions.

        Returns:
            str: Texto final utilizado como mensagem de sistema para o modelo.
        """
        system_prompt = ""

        if len(self.subordinated_agents) > 0:
            # prompt adicional para interagir com outros agentes
            subordinate_agents_in_system_prompt = (
                "Você pode fazer perguntas e pedidos para outros agentes, quando necessário, usando o tool 'ask_to_agent_tool'.\n"
                "Segue a lista de agentes disponíveis:\n")

            for subordinate_agent in self.subordinated_agents:
                subordinate_agents_in_system_prompt += f"- {subordinate_agent.name}: {subordinate_agent.description}\n"

            system_prompt += subordinate_agents_in_system_prompt + '\n\n---\n\n'
        # endif --

        # prompts adicionais conforme o contexto de trabalho do agente
        if len(self.agent_config.working_files or []) > 0:
            # prompt para fazer o agente de comportar como analista de BI
            system_prompt += "Vamos analisar algumas fontes de dados CSV, cada um com um nome e um conjunto de colunas. Seguem as fontes de dados disponíveis:\n\n"

            for working_file in self.agent_config.working_files:
                system_prompt += ("**Fonte de dados**\n"
                                  f"Nome: {working_file['name']}\n"
                                  f"Descrição: {working_file['description']}\n"
                                  f"Pathname: {working_file['pathname']}\n"
                                  f"Colunas:\n")

                # monta uma lista com os nomes das colunas do CSV cujo nome está em self._dataframe
                df = pd.read_csv(working_file['pathname'], nrows=0)  # Read just the first line to get column names
                dataframe_fields = '\n- '.join(df.columns.tolist())

                system_prompt += f"- {dataframe_fields}\n\n"

            system_prompt += dedent("""
            Para responder perguntas e pedidos sobre os dados de um CSV gere e execute código Python para extrair as informações seguindo esses passos:

            1. Carregar o CSV em um `pandas dataframe`.
            2. Converter os campos que contém valores do tipo data (em inglês 'date') para dados do tipo 'datetime'.
            3. Criar os comandos para extrair as informações.
            4. Executar o script Python.
            5. Analisar a resposta e sugerir algum insight.
            6. Quando for solicitado um gráfico então grave a imagem do gráfico no arquivo informado.

            ---\n\n""")
        # endif --

        if len(self.retrievers or []) > 0:
            # prompt para fazer o agente trabalhar com documentos vetorizados
            system_prompt += "RAG está habilitado, você deve usar a ferramenta retriever_tool para obter o contexto relevante e gerar a resposta com base no contexto recuperado.\n"
            system_prompt += "As seguintes fontes de dados estão disponíveis:\n"

            for retriever in self.retrievers:
                system_prompt += f"- {retriever['name']}\n"

            system_prompt += "\n---\n\n"
        # endif --

        if 'execute_python_code_tool' in self.agent_config.tools_names:
            # prompt para executar código Python
            system_prompt += dedent("""
            Quando gerar comandos em Python para responder perguntas e solicitações, siga estes critérios:

            1. Ao usar pandas, siga estas regras:
               - Configure o pandas para suprimir avisos sobre *chained assignments* e para exibir todas as linhas e colunas do *dataframe*.
               - Ao agrupar e filtrar dados em um *dataframe* do pandas, armazene resultados intermediários em variáveis e use essas variáveis nas operações subsequentes.

            2. Ao carregar arquivos CSV em pandas dataframes, siga estas regras:
                - Use o comando `pd.read_csv()` para carregar arquivos CSV em dataframes pandas.
                - Use o parâmetro `encoding='utf-8'` para garantir a correta leitura de caracteres especiais.
                - Use o parâmetro `low_memory=False` para evitar problemas de memória com arquivos grandes.
                - Use o parâmetro `dtype=str` para garantir que todas as colunas sejam tratadas como strings.
                - Converta as colunas do tipo data (em inglês) para o formato datetime usando o comando `pd.to_datetime()`, usand o seginte código:

                ```python
                # Consider columns whose names contain 'data' or 'date' (case-insensitive)
                date_like_cols = [c for c in df.columns if ('data' in c.lower()) or ('date' in c.lower())]
                for c in date_like_cols:
                    # Clean common invisible characters and surrounding spaces before parsing
                    series_clean = (
                        df[c]
                        .astype(str)
                        .str.replace('\u00A0', '', regex=False)  # non-breaking space
                        .str.strip()
                    )
                    # Convert to datetime; format may vary (e.g., 'YYYY-MM-DD HH:MM:SS'), so let pandas infer
                    df[c] = pd.to_datetime(series_clean, errors='coerce')
                ```

            3. Ao criar gráficos, siga estas regras:
               - Crie o gráfico usando `matplotlib.pyplot`.
               - Defina o tamanho do gráfico como `figsize=(14,5)`.
               - Configure o gráfico para incluir um título, legenda e linhas de grade. As linhas de grade devem ser cinza claro.
               - Posicione a legenda com base na quantidade de séries de dados:            
                   * Se a contagem ≤ 15, use: `plt.legend(bbox_to_anchor=(1.44,-0.10), loc='lower right')` e `plt.tight_layout()`.
                   * Se 15 < contagem ≤ 30, use: `plt.legend(bbox_to_anchor=(1.44,-0.10), loc='lower right', ncol=2)` e `plt.tight_layout()`.
                   * Se 30 < contagem ≤ 45, use: `plt.legend(bbox_to_anchor=(1.44,-0.10), loc='lower right', ncol=3)` e `plt.tight_layout()`.
                   * Se contagem > 45, use: `plt.legend(bbox_to_anchor=(1.44,-0.10), loc='lower right', ncol=4)` e `plt.tight_layout()`.
               - **Não** execute o comando `plt.show()`, pois o ambiente de execução não oferece suporte à exibição gráfica.
               - Inclua um comando para salvar o gráfico como um arquivo PNG na pasta `{working_folder}`, com o nome do arquivo especificado no prompt do usuário.

            4. Ao exibir tabelas, siga estas regras:
               - Coloque o resultado em um *dataframe*.
               - Limpe valores de string usando o comando:

               ```python
               result = result.transform(lambda value: '...' if isinstance(value, str) and (chr(92) + chr(110)) in value else value)
               ```

               - Exiba o resultado usando o comando:

               ```python
               print(result.head(50).to_csv(index=False, quoting=1, quotechar='"'))
               ```

            5. Se o resultado for um conjunto de dados em formato CSV:
               - Se tiver mais de 3 linhas, converta os dados em uma tabela markdown com todas as linhas.
               - Se tiver 0 linhas, responda com o texto "No records".
               - Caso contrário, apresente o resultado como uma lista.

            6. Ao gerar a resposta siga essas regras:
               - **Não** mencione o nome do arquivo CSV na resposta.
               - **Não** mencione o local do arquivo CSV na resposta.
               - **Não** retorne o código-fonte do script Python na resposta.

            ---\n\n""")
        # endif --

        if self.tools or system_prompt:
            tools_names = list(self.tools.keys())
            custom_tools_names = list((self.agent_config.custom_tools or {}).keys())
            if len(custom_tools_names) > 0:
                tools_names += custom_tools_names
            tool_hint = "Ferramentas/funções disponíveis para uso: " + ", ".join(sorted(tools_names))

            system_prompt += tool_hint + "\n\n---\n\n"

        # process vars in the prompt, like agent input data
        system_prompt = self._prepare_prompt(prompt=system_prompt + dedent(self.agent_config.system_prompt))

        return system_prompt

    def _prepare_prompt(self, prompt: str, message_id: str | None = None) -> str:
        """Resolve template variables and inject contextual hints.

        Args:
            prompt (str): Texto original que será enriquecido.
            message_id (str | None, optional): Identificador usado em instruções dependentes da mensagem. Defaults to None.

        Returns:
            str: Prompt final com substituições e orientações adicionais.
        """
        if message_id:
            temp_prompt = prompt.lower()
            if (
                    ("gerar" in temp_prompt or "gere" in temp_prompt or "criar" in temp_prompt or "crie" in temp_prompt) and
                    "diagrama" in temp_prompt
            ):
                # orientações para fazer o agente gerar diagramas Plantuml
                hint = (
                    "Quando solicitado para criar um diagrama ou fluxo grama, siga essas instruções:\n"
                    "- Crie o diagrama em formato 'Mermaid' quando solicitado, senão use o formato 'PlantUML'\n."
                    "- Ao dar nomes aos objetos do diagrama use o padrão CamelCase.\n"
                    "- `Activity Diagram` em PlantUML: loops do tipo 'repeat' devem terminar com 'repeat while'\n"
                    "- `Activity Diagram` em PlantUML: todos laços 'if' devem ter um 'endif' correspondente.\n"
                    "\n---\n\n"
                )
                prompt = hint + prompt
            # endif --

            # prompt of a question
            if len(self.agent_config.working_files or []) > 0:
                # prompt para fazer o agente trabalhar com arquivos CSV/BI
                folder = self._ensure_session_working_folder()
                hint = f"Quando precisar salvar imagens de gráficos em arquivos, salve na pasta '{folder.as_posix()}' com o nome '{message_id}-' seguido de um número aleatório entre 1 e 10000.\n\n---\n\n"
                prompt = hint + prompt
            # endif --

        # process variables inside the prompt
        mapping: dict[str, str] = {
            "session_id": self.session_id,
            "session_name": self.session_name or "",
            "message_id": message_id or "",
            "now": self._now().isoformat(timespec="seconds"),
            'working_folder': self.working_folder or ""
        }
        for k, v in (self.input_data or {}).items():
            if isinstance(v, (str, int, float)):
                mapping[str(k)] = str(v)

        def repl(m: re.Match[str]) -> str:
            """Replace template variables found within curly braces.

            Args:
                m (re.Match[str]): Resultado da expressão regular contendo o nome da variável.

            Returns:
                str: Valor substituto presente em `mapping` ou o token original quando ausente.
            """
            key = m.group(1)
            return mapping.get(key, m.group(0))

        # Replace {var}
        prompt = dedent(re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", repl, prompt))
        return prompt

    @staticmethod
    def _summarize_history(messages: list[dict[str, Any]], limit_chars: int = 800) -> str:
        """Condense prior message history into a short textual summary.

        Args:
            messages (list[dict[str, Any]]): Histórico de mensagens estruturadas.
            limit_chars (int, optional): Quantidade máxima aproximada de caracteres. Defaults to 800.

        Returns:
            str: Resumo textual das interações anteriores.
        """
        if not messages:
            return ""
        # Concise heuristic summarization: keep early context and last line
        text_parts: list[str] = []
        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "")
            if isinstance(content, list):
                content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
            text_parts.append(f"[{role}] {str(content)[:200]}")

        summary = " \n".join(text_parts)
        if len(summary) > limit_chars:
            summary = summary[: limit_chars - 3] + "..."
        return f"Resumo das interações anteriores (condensado):\n{summary}"

    def _build_input_messages(self, question: str, *,
                              attached_files: list[str] | None = None,
                              include_history: bool = True, ) -> list[dict[str, Any]]:
        """Compose the payload sent to the OpenAI Responses API.

        Args:
            question (str): Prompt principal fornecido pelo usuário.
            attached_files (list[str] | None, optional): Caminhos de arquivos anexados. Defaults to None.
            include_history (bool): Indica se deve enviar o histórico de conversas com o prompt.

        Returns:
            list[dict[str, Any]]: Lista de mensagens formatadas conforme o protocolo da API.
        """
        # System message
        system_msg = {"role": "system", "content": self._my_system_prompt}

        messages: list[dict[str, Any]] = [system_msg]

        if include_history:
            # Build history: last K pairs + summary of older
            k = max(0, int(self.history_window_size))
            prior_struct = self.message_history[-(2 * k):] if k > 0 else []
            older_struct = self.message_history[: max(0, len(self.message_history) - len(prior_struct))]

            # Map structured history into API messages
            if older_struct:
                messages.append({"role": "system", "content": self._summarize_history(older_struct)})

            for m in prior_struct:
                role = m.get("role")
                content = m.get("content", "")
                if role == "agent":
                    api_role = "assistant"
                elif role == "user":
                    api_role = "user"
                else:
                    # Skip stored system messages; we already inject system content above
                    continue
                messages.append({"role": api_role, "content": content})

        # Build multimodal user content. If there are image files, use structured blocks
        content_blocks: list[dict[str, Any]] = [{"type": "input_text", "text": question}]   # prompt
        for file_path in attached_files or []:
            try:
                if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
                    # arquivos suportados pela API da OpenAI
                    uploaded_file = self._openai_client.files.create(
                        file=open(file_path, "rb"),
                        purpose="assistants"
                    )
                    if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                        file_block = {"type": "input_image", "file_id": uploaded_file.id}
                        self._attached_files.append(file_block)

                    elif file_path.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm")):
                        file_block = {"type": "input_audio", "audio_file_id": uploaded_file.id}
                        self._attached_files.append(file_block)

                    else:
                        file_block = {"type": "input_file", "file_id": uploaded_file.id}
                        self._attached_files.append(file_block)

                elif file_path.lower().endswith((".md", ".markdown", ".txt", ".text", ".puml", ".json", ".yaml", ".xml")):
                    # arquivos texto enviados com o prompt
                    blocks = render_file_as_content_blocks(file_path)
                    content_blocks.extend(blocks)
                else:
                    # outros tipos de arquivo
                    raise ValueError(f"Unsupported file type: {file_path}")

            except ValueError as exc:
                name = os.path.basename(file_path)
                content_blocks.append({
                    "type": "input_text",
                    "text": f"[erro ao processar arquivo: {name}] {exc}",
                })
            except Exception as exc:
                name = os.path.basename(file_path)
                content_blocks.append({
                    "type": "input_text",
                    "text": f"[falha inesperada ao processar arquivo: {name}] {exc}",
                })

            # Remove the processed file if it is a temporary file stored in the working folder
            if self.session_id in file_path:
                try:
                    os.remove(file_path)
                except OSError as e:
                    log_msg(f"Error removing file {file_path}: {e}", func="render_file_as_content_blocks", color="RED")

        # If we only had text (no files), keep content as a simple string for minimal payload
        content_blocks.extend(self._attached_files)

        if len(content_blocks) > 1:
            # When files are present (esp. images), send structured content blocks
            messages.append({"role": "user", "content": content_blocks})
        else:
            messages.append({"role": "user", "content": question})

        return messages

    def _compose_tool_schemas(self, tools_names: list[str]) -> list[dict[str, Any]]:
        """Constrói schemas de ferramentas padrão e customizadas.

        Args:
            tools_names (list[str]): Lista de ferramentas solicitadas para a chamada.

        Returns:
            list[dict[str, Any]]: Schemas OpenAI unificados, incluindo overrides corporativos quando declarados.
        """
        schemas = build_tool_schemas(tools_names)

        if self._build_custom_tool_schemas_fn:
            try:
                custom_schemas = self._build_custom_tool_schemas_fn(tools_names, self.agent_config.custom_tools)
            except Exception as exc:  # noqa: BLE001
                custom_schemas = []
                if self.is_verbose:
                    log_msg(f"Falha ao construir schemas personalizados de ferramentas: {exc}",
                            func="_compose_tool_schemas", action="schemas", color="RED")
            schemas.extend(custom_schemas or [])

        return schemas

    @staticmethod
    def _parse_response_outputs(outputs: list[dict[str, Any]] | None) -> tuple[str, list[dict[str, Any]]]:
        """Separa texto final e chamadas de ferramentas a partir da resposta da API.

        Args:
            outputs (list[dict[str, Any]] | None): Blocos retornados pela API de respostas.

        Returns:
            tuple[str, list[dict[str, Any]]]: Texto consolidado do assistente e a lista de tool-calls para execução.
        """
        if not outputs:
            return "", []
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for out in outputs:
            out_type = out.get("type")
            if out_type == "message" and out.get("role") == "assistant":
                for msg_content in out.get("content", []) or []:
                    if msg_content.get("type") == "output_text":
                        text_parts.append(msg_content.get("text", ""))
            elif out_type == "function_call":
                tool_calls.append(out)
        return "".join(text_parts), tool_calls

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        """Determina se o erro permite retentativa.

        Args:
            exc (Exception): Erro capturado durante a chamada ao LLM.

        Returns:
            bool: True quando há sinais de falha transitória que justificam nova tentativa.
        """
        transient_markers = ("timeout", "temporarily", "rate limit", "overload", "connection", "unavailable")
        text = str(exc).lower()
        return any(marker in text for marker in transient_markers)

    @staticmethod
    def _normalize_tool_args(call: dict[str, Any]) -> dict[str, Any]:
        """Normaliza argumentos recebidos em chamadas de ferramentas.

        Args:
            call (dict[str, Any]): Estrutura da chamada de função vinda do modelo.

        Returns:
            dict[str, Any]: Argumentos convertidos em dicionário, preservando chaves originais sempre que possível.
        """
        args_obj: Any = call.get("arguments") or call.get("parameters") or call.get("function", {}).get("arguments")
        if isinstance(args_obj, str):
            try:
                args_obj = json.loads(args_obj)
            except Exception:
                args_obj = {"code": args_obj, "expression": args_obj, "query": args_obj}
        if not isinstance(args_obj, dict):
            return {}
        return args_obj

    def _call_llm_with_resilience(self,
                                  model_name: str,
                                  messages_for_model: list[dict[str, Any]],
                                  tools_schema: list[dict[str, Any]]) -> Any:
        """Executa chamadas ao LLM com retentativas, backoff e timeout.

        Args:
            model_name (str): Identificador do modelo configurado.
            messages_for_model (list[dict[str, Any]]): Payload serializado no formato esperado pela API.
            tools_schema (list[dict[str, Any]]): Schemas de ferramentas liberadas para a execução.

        Returns:
            Any: Resposta bruta do cliente OpenAI.
        """
        attempts = 0
        last_error: Exception | None = None
        while attempts < max(1, self._resilience.max_llm_attempts):
            attempts += 1
            try:
                return self._openai_client.responses.create(
                    model=model_name,
                    input=messages_for_model,
                    reasoning={"effort": self.reasoning_effort},
                    tools=tools_schema or None,
                    timeout=self._resilience.llm_timeout_seconds,
                )
            except Exception as exc:
                last_error = exc
                if not self._is_retryable_error(exc):
                    break
                if attempts >= self._resilience.max_llm_attempts:
                    break
                backoff = self._resilience.backoff_base_seconds * (2 ** (attempts - 1))
                jitter = self._rng.uniform(0, self._resilience.backoff_jitter_seconds)
                time.sleep(backoff + jitter)

        raise last_error or RuntimeError("Falha ao contatar o modelo LLM.")

    def get_pretty_messages_history(self, message_format: str = 'raw',
                                    list_subordinated_agents_history: bool = False) -> list:
        """Return the conversation history formatted for presentation.

        Args:
            message_format (str, optional): Formato desejado para o conteúdo (`raw` ou `html`). Defaults to 'raw'.
            list_subordinated_agents_history (bool, optional): Indica se deve incluir respostas de agentes subordinados. Defaults to False.

        Returns:
            list[dict[str, Any]]: Lista de mensagens formatadas, incluindo agrupamentos de pergunta e resposta.
        """
        if self.is_verbose:
            log_msg(f"list_all={list_subordinated_agents_history}", func="get_messages_history", color="BLUE")

        def format_message(message_content: str) -> tuple[str, list[str]]:
            """Formata o texto da mensagem conforme o formato solicitado.

            Args:
                message_content (str): Conteúdo bruto registrado no histórico.

            Returns:
                tuple[str, list[str]]: Texto transformado e lista de idiomas identificados.
            """
            if message_format == 'html':
                return convert_markdown_to_html_block(message_content, flag_insert_copy_to_clipboard_command=False)

            return message_content, []

        def create_message(message_id, message_kind, sent_at, content, languages=None, model_name=None, usage=None):
            """Cria um registro de mensagem normalizado para camadas de visualização.

            Args:
                message_id (str): Identificador único da mensagem.
                message_kind (str): Tipo categórico (`UserPrompt`, `Answer`, etc.).
                sent_at (str): Timestamp no formato ISO apontando quando a mensagem foi enviada.
                content (str | tuple[str, list[str]]): Conteúdo já formatado conforme a visualização.
                languages (list[str] | None, optional): Idiomas detectados no conteúdo. Defaults to None.
                model_name (str | None, optional): Nome do modelo utilizado na resposta. Defaults to None.
                usage (dict | None, optional): Estatísticas de uso associadas à mensagem. Defaults to None.

            Returns:
                dict[str, Any]: Estrutura padronizada representando a mensagem e metadados associados.
            """
            return {
                "kind": message_kind,
                "message_id": message_id,
                "agent_name": self.name if message_kind == 'Answer' else None,
                "sent_at": sent_at,
                "content": content,
                "files": message["files"],
                "format": message_format,
                "languages": languages,
                "model_name": model_name,
                "usage": usage,
            }

        messages_list = []
        for message in self.message_history:
            if message["role"] == 'user':
                kind = "UserPrompt"
                formated_content, content_languages = format_message(message["content"])

            elif message["role"] == 'agent':
                kind = "Answer"
                formated_content, content_languages = format_message(
                    message["content"].replace(self.session_id, "").replace(message["message_id"], ""))

            else:
                if self.is_verbose:
                    log_msg(f"Discarded message.role='{message['role']}'", func="get_messages_history", color="BLUE")

                kind = formated_content = content_languages = None
            # endif --

            if kind:
                message_usage = {
                    "request_tokens": message["usage"]["input_tokens"],
                    "response_tokens": message["usage"]["output_tokens"],
                    "total_tokens": message["usage"]["total_tokens"],
                    "elapsed_time_in_seconds": message["elapsed_time_in_seconds"],
                }
                messages_list.append(create_message(message_id=message["message_id"],
                                                    message_kind=kind,
                                                    sent_at=message["timestamp"],
                                                    content=formated_content,
                                                    languages=content_languages,
                                                    model_name=message.get("model_name"),
                                                    usage=message_usage))
            # endif --
        # endfor --

        # agrupa perguntas e respostas
        grouped_message_list = []
        for message in messages_list:
            if message['kind'] == "SystemPrompt":
                grouped_message_list.append(message)

            elif message['kind'] == "UserPrompt":
                message["answers"] = []
                grouped_message_list.append(message)

            else:
                grouped_message_list[-1]["answers"].append(message)

        # junta as mensagens dos agentes subordinados
        if list_subordinated_agents_history:
            for agent in self.subordinated_agents:
                grouped_message_list += agent.get_messages_history(message_format=message_format,
                                                                   list_all=list_subordinated_agents_history)

        return grouped_message_list

    def _exec_tool(self, tool_name: str, message_id: str, args_obj: dict) -> ToolExecutionResult:
        """Executa uma ferramenta registrada aplicando política de resiliência.

        Args:
            tool_name (str): Nome da ferramenta solicitada.
            message_id (str): Identificador da mensagem corrente (para isolamento de artefatos).
            args_obj (dict): Argumentos serializados para a chamada.

        Returns:
            ToolExecutionResult: Resultado padronizado, já incluindo métricas de execução.
        """
        tool_fn = self.tools.get(tool_name or "")
        if tool_fn is None:
            err = f"Tool '{tool_name}' não disponível."
            return ToolExecutionResult(value={"error": err}, elapsed_seconds=0, error=err)

        ctx = self._make_tool_context(message_id)
        policy = self._select_tool_policy(tool_name)

        def _runner() -> Any:
            if tool_name in self._custom_tools_names and self._exec_custom_tool_fn:
                try:
                    return self._exec_custom_tool_fn(tool_name,
                                                     tool_fn,
                                                     args_obj,
                                                     ctx,
                                                     self.agent_config.custom_tools)
                except Exception as exec_error:  # noqa: BLE001
                    if self.is_verbose:
                        log_msg(
                            f"id={message_id} tool_name={tool_name} cg_exec_fallback error={exec_error}",
                            func="_exec_tool",
                            action="tools",
                            color="YELLOW",
                        )
            return exec_tool(tool_name, tool_fn, args_obj, ctx)

        return execute_tool_with_policy(tool_name, tool_fn, args_obj, ctx, policy=policy, runner=_runner)

    def _select_tool_policy(self, tool_name: str) -> ToolExecutionPolicy:
        """Resolve o timeout aplicado a uma ferramenta específica.

        Args:
            tool_name (str): Nome da ferramenta solicitada pelo modelo.

        Returns:
            ToolExecutionPolicy: Política com timeout já ajustado para a ferramenta.
        """
        timeouts = self._resilience.tool_timeouts or {}
        timeout_seconds = timeouts.get(tool_name, self._resilience.tool_timeout_seconds)

        if timeout_seconds <= 0:
            # Evita timeouts inválidos vindos de configurações externas.
            timeout_seconds = self._resilience.tool_timeout_seconds

        return ToolExecutionPolicy(timeout_seconds=timeout_seconds)

    def _run_tool_calls(self, tool_calls: list[dict[str, Any]], message_id: str) -> list[dict[str, Any]]:
        """Executa chamadas de ferramentas e devolve outputs no formato da API.

        Args:
            tool_calls (list[dict[str, Any]]): Chamadas solicitadas pelo modelo.
            message_id (str): Identificador usado para rastrear artefatos da execução.

        Returns:
            list[dict[str, Any]]: Lista de blocos `function_call_output` prontos para reenvio ao LLM.
        """
        next_inputs: list[dict[str, Any]] = []
        for call in tool_calls:
            call_id = call.get("call_id")
            tool_name = call.get("name") or ""
            args_obj = self._normalize_tool_args(call)
            tool_result = self._exec_tool(tool_name, message_id, args_obj)

            if self.is_verbose:
                preview = str(tool_result.value).replace("\n", " ") if tool_result else ""
                if len(preview) > 120:
                    preview = preview[:117] + "..."
                log_msg(
                    f"id={message_id} tool_end name={tool_name} result='{preview}'",
                    func="_run_tool_calls",
                    action="tool_call",
                    color="BLUE",
                )

            try:
                value = tool_result.to_model_payload() if tool_result else {}
                result_text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            except Exception:
                result_text = str(tool_result.value if tool_result else "")

            next_inputs.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": result_text,
            })
        return next_inputs

    @staticmethod
    def _compute_usage(input_msgs: list[dict[str, Any]],
                       output_text: str,
                       usage: dict[str, Any] | None) -> tuple[int, int, int]:
        """Calcula tokens de entrada/saída usando dados oficiais ou heurística."""
        if usage and all(k in usage for k in ("input_tokens", "output_tokens")):
            input_tokens = int(usage.get("input_tokens", 0))
            output_tokens = int(usage.get("output_tokens", 0))
            total_tokens = input_tokens + output_tokens
            return input_tokens, output_tokens, total_tokens

        input_text = "\n".join([str(m.get("content", "")) for m in input_msgs])
        input_tokens = _approx_token_count(input_text)
        output_tokens = _approx_token_count(output_text)
        total_tokens = input_tokens + output_tokens
        return input_tokens, output_tokens, total_tokens

    @staticmethod
    def _sanitize_artifact_name(name: str, message_id: str, session_id: str | None = None) -> str:
        """Remove prefixes de sessão e mensagem para evitar exposição de paths.

        Args:
            name (str): Nome bruto do arquivo gerado.
            message_id (str): Identificador da mensagem que originou o artefato.
            session_id (str | None, optional): Identificador de sessão para higienização adicional. Defaults to None.

        Returns:
            str: Nome seguro, sem IDs sensíveis.
        """
        safe_name = name
        if session_id:
            for sep in ("_", "-"):
                pref = f"{session_id}{sep}"
                if safe_name.startswith(pref):
                    safe_name = safe_name[len(pref):]
                    break
        for sep in ("_", "-"):
            pref = f"{message_id}{sep}"
            if safe_name.startswith(pref):
                safe_name = safe_name[len(pref):]
                break
        return safe_name

    def _collect_session_artifacts(self, message_id: str) -> list[dict[str, str]]:
        """Coleta arquivos gerados na pasta segura da sessão.

        Args:
            message_id (str): Identificador usado como prefixo dos artefatos criados.

        Returns:
            list[dict[str, str]]: Arquivos codificados em base64, prontos para anexar no histórico.
        """
        artifacts: list[dict[str, str]] = []
        try:
            session_dir = self._ensure_session_working_folder().resolve()
            for entry in session_dir.iterdir():
                if not entry.is_file() or not str(entry.name).startswith(message_id):
                    continue
                try:
                    data = entry.read_bytes()
                except Exception:
                    data = b""
                try:
                    entry.unlink()
                except Exception:
                    pass

                safe_name = self._sanitize_artifact_name(entry.name, message_id, str(self.session_id))
                content = base64.b64encode(data).decode("ascii") if data else ""
                artifacts.append({"filename": safe_name, "content": content})
        except Exception:
            pass
        return artifacts

    def _execute_conversation_loop(self,
                                   model_name: str,
                                   input_msgs: list[dict[str, Any]],
                                   tools_schema: list[dict[str, Any]],
                                   message_id: str) -> tuple[str, dict[str, Any] | None]:
        """Executa o ciclo LLM + ferramentas respeitando limites de iteração.

        Args:
            model_name (str): Nome do modelo a ser chamado.
            input_msgs (list[dict[str, Any]]): Mensagens de entrada já preparadas.
            tools_schema (list[dict[str, Any]]): Schemas de ferramentas liberadas.
            message_id (str): Identificador da interação (para rastreamento e artefatos).

        Returns:
            tuple[str, dict[str, Any] | None]: Texto final do assistente e metadados de uso retornados pela API.
        """
        output_text = ""
        usage: dict[str, Any] | None = None
        messages_for_model = input_msgs

        for _ in range(max(1, self._resilience.max_tool_iterations)):
            resp = self._call_llm_with_resilience(model_name, messages_for_model, tools_schema)
            raw = resp.to_dict() if hasattr(resp, "to_dict") else json.loads(
                json.dumps(resp, default=lambda o: getattr(o, "__dict__", str(o))))

            usage = raw.get("usage") or usage
            output_blocks = raw.get("output") or []
            assistant_text, tool_calls = self._parse_response_outputs(output_blocks)

            if tool_calls:
                base_outputs = getattr(resp, "output", None) or output_blocks
                next_inputs = list(base_outputs) if isinstance(base_outputs, list) else []
                tool_outputs = self._run_tool_calls(tool_calls, message_id)
                messages_for_model = messages_for_model + next_inputs + tool_outputs
                continue

            output_text = assistant_text
            break

        return output_text, usage

    @staticmethod
    def _encode_user_files(files: list[str] | None) -> list[dict[str, str]]:
        """Codifica anexos do usuário em base64 para persistência no histórico.

        Args:
            files (list[str] | None): Caminhos dos arquivos anexados pelo usuário.

        Returns:
            list[dict[str, str]]: Estruturas contendo nome seguro e conteúdo codificado (ou vazio em caso de erro).
        """
        user_files_struct: list[dict[str, str]] = []
        for file_path in files or []:
            try:
                name = os.path.basename(file_path)
                data = Path(file_path).read_bytes()
                b64 = base64.b64encode(data).decode("ascii")
                user_files_struct.append({"name": name, "content": b64})
            except Exception:
                user_files_struct.append({"name": file_path, "content": ""})
        return user_files_struct

    def answer(self,
               question: str,
               message_format: str = 'raw',
               attached_files: str | list[str] | None = None,
               model: str | None = None,
               reasoning_effort: str = None,
               action: str = 'chat',
               include_history: bool = True,
               is_consult_prompt: bool = False) -> dict:
        """Gera uma resposta usando o modelo configurado, incluindo ferramentas e anexos (ver docs/ADR-setup-agent-refactor.md — Atualização 2025-02-19).

        Args:
            question (str): Pergunta ou instrução original do usuário.
            message_format (str, optional): Formato da resposta (`raw` ou `html`). Defaults to 'raw'.
            attached_files (str | list[str] | None, optional): Caminho ou lista de caminhos para anexos enviados ao prompt. Defaults to None.
            model (str | None, optional): Nome do modelo a ser utilizado; se ausente, usa o modelo configurado no agente. Defaults to None.
            reasoning_effort (str | None, optional): Esforço de raciocínio ("none", "low", "medium", "high"); padrão "none" prioriza latência/custo e pode ser sobrescrito por chamadas que exijam mais contexto. Defaults to None.
            action (str, optional): Rótulo funcional usado para logs e relatórios de telemetria. Defaults to 'chat'.
            include_history (bool, optional): Define se o histórico recente deve ser enviado com o prompt. Defaults to True.
            is_consult_prompt (bool, optional): Indica se a mensagem é uma consulta para outro agente, ajustando logs e roteamento. Defaults to False.

        Returns:
            dict[str, Any]: Estrutura contendo resposta, metadados, anexos retornados e estatísticas de uso.
        """
        self.reasoning_effort = reasoning_effort if reasoning_effort else "none"

        msg_timestamp = self._now()
        self._ensure_session_working_folder()
        message_id = str(uuid.uuid4())
        prepared_q = self._prepare_prompt(question, message_id=message_id)

        if self.is_verbose:
            _q = prepared_q.replace("\n", " ")
            if len(_q) > 120:
                _q = _q[:117] + "..."
            log_msg(f"id={message_id} consult={is_consult_prompt} q='{_q}'", func="answer", action=str(action),
                    color="BLUE")

        files: list[str] | None = [attached_files] if isinstance(attached_files, str) else attached_files
        input_msgs = self._build_input_messages(prepared_q,
                                                attached_files=files,
                                                include_history=include_history)

        user_files_struct = self._encode_user_files(files)
        approx_tokens = _approx_token_count(prepared_q)
        now_ts = self._now().isoformat(timespec="seconds")

        user_message_struct = {
            "role": "user",
            "message_id": message_id,
            "agent_name": "user",
            "timestamp": now_ts,
            "sent_at": now_ts,
            "elapsed_time_in_seconds": 0,
            "content": prepared_q,
            "files": user_files_struct,
            "format": message_format or "raw",
            "languages": [],
            "model_name": "",
            "usage": {
                "input_tokens": approx_tokens,
                "output_tokens": 0,
                "total_tokens": approx_tokens,
            },
        }
        self.message_history.append(user_message_struct)

        tools_names = list(self.tools.keys())
        tools_schema = self._compose_tool_schemas(tools_names)
        model_name = self.agent_config.model if model is None else model

        output_text = ""
        usage: dict[str, Any] | None = None

        if self._openai_client is None:
            reason = self._init_error_reason or "motivo não identificado"
            output_text = f"[modo offline] Não foi possível contactar a API. Motivo: {reason}"
        else:
            try:
                output_text, usage = self._execute_conversation_loop(model_name, input_msgs, tools_schema, message_id)
            except Exception as exc:  # noqa: BLE001
                output_text = f"Falha ao submeter o prompt: {exc}"

        input_tokens, output_tokens, total_tokens = self._compute_usage(input_msgs, output_text, usage)
        assistant_files_struct2 = self._collect_session_artifacts(message_id)

        assistant_message_struct = {
            "role": "agent",
            "message_id": message_id,
            "agent_name": self.agent_config.agent_name,
            "timestamp": msg_timestamp.replace(microsecond=0).isoformat(timespec="seconds"),
            "sent_at": self._now().replace(microsecond=0).isoformat(timespec="seconds"),
            "elapsed_time_in_seconds": int((self._now() - msg_timestamp).total_seconds()),
            "content": output_text,
            "files": assistant_files_struct2,
            "format": message_format or "raw",
            "languages": [],
            "model_name": model_name,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            },
        }
        self.message_history.append(assistant_message_struct)
        self.session_updated_at = self._now()

        if self.response_callback:
            try:
                self.response_callback(assistant_message_struct)
            except Exception:
                pass

        if self.is_verbose:
            usage2n = assistant_message_struct.get("usage", {}) or {}
            log_msg(
                (
                    f"id={message_id} finalized tokens"
                    f"{{'input': {usage2n.get('input_tokens')}, 'output': {usage2n.get('output_tokens')}, 'total': {usage2n.get('total_tokens')}}}"
                ),
                func="answer",
                action=str(action),
                color="BLUE",
            )

        # elimina a pasta de trabalho se estiver vazia
        self._remove_empty_session_working_folder()

        return assistant_message_struct

    def delete_old_files(self, max_age_days: int=30) -> list:
        """Remove arquivos antigos do storage remoto do OpenAI.

        Intent:
            Garantir limpeza periódica de anexos e saídas alinhada ao ciclo de retenção descrito em docs/ADR-setup-agent-refactor.md.

        Args:
            max_age_days (int, optional): Janela de retenção em dias; arquivos anteriores ao limite serão apagados. Defaults to 30.

        Returns:
            list: Tuplas contendo ID, nome do arquivo e data de criação para cada item removido.
        """
        # Quantidade de dias para expiração
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)

        # 1. Listar todos os arquivos
        files = self._openai_client.files.list()

        deleted_files = []

        # 2. Filtrar arquivos antigos
        for f in files.data:
            created_at = datetime.fromtimestamp(f.created_at, tz=timezone.utc)

            if created_at < cutoff_date:
                # 3. Excluir
                self._openai_client.files.delete(f.id)
                deleted_files.append((f.id, f.filename, created_at))

        # 4. retorna os nomes dos arquivos removidos
        return deleted_files
