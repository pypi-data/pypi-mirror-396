from __future__ import annotations

from dataclasses import dataclass, field, asdict, InitVar
from typing import Any, Optional


@dataclass(slots=True)
class AgentConfig:
    # region Public configuration fields
    agent_id: Optional[str] = None
    agent_name: str = "oskaragent"
    model: str = "gpt-5.1"
    model_settings: Optional[dict[str, Any]] = None
    system_prompt: Optional[str] = None
    description: Optional[str] = 'Esse é um agente de Inteligência Artificial.'
    tools_names: list[str] = field(default_factory=list)
    custom_tools: Optional[dict[str, Any]] = None
    knowledge_base: Optional[list[dict[str, Any]]] = None
    working_files: Optional[list[dict[str, Any]]] = None
    working_databases: Optional[list[dict[str, Any]]] = None

    # json_config is accepted during initialization but not stored
    json_config: InitVar[Optional[dict[str, Any]]] = None
    # endregion

    def __post_init__(self, json_config: Optional[dict[str, Any]]):
        """Finalize dataclass initialization by resolving defaults and validation.

        Args:
            json_config (Optional[dict[str, Any]]): Configuração em formato dict usada para hidratar o agente.

        Returns:
            None: O método ajusta atributos internos sem produzir valor de retorno.
        """
        # If a JSON config was provided, apply it first
        if json_config:
            self.restore_from_json(json_config)

        # Fill sensible defaults consistent with previous behavior
        if not self.agent_name:
            self.agent_name = "oskaragent"

        if not self.model:
            self.model = "gpt-5"

        if self.system_prompt is None:
            self.system_prompt = f"Você é um assistente prestativo. Seu nome é {self.agent_name}."

        if self.tools_names is None:
            # Keep a list even if None was explicitly provided
            self.tools_names = []

        if self.agent_id is None:
            # Default agent_id to agent_name
            self.agent_id = self.agent_name

        # Final type and value checks
        self._validate()


    def to_json(self) -> dict[str, Any]:
        """Serialize configuration values into a JSON-friendly dictionary.

        Returns:
            dict[str, Any]: Dicionário contendo os campos públicos da configuração do agente.
        """
        data = asdict(self)
        # `json_config` is an InitVar and not present; ensure consistency
        return data


    def restore_from_json(self, agent_config: dict[str, Any]) -> None:
        """Load configuration values from a plain dictionary.

        Args:
            agent_config (dict[str, Any]): Dados serializados utilizados para atualizar a configuração.

        Returns:
            None: O método modifica a instância atual in-place.
        """
        if not isinstance(agent_config, dict):
            return

        # Apply values only if present in the dict (do not clear existing ones)
        if (v := agent_config.get("agent_id")) is not None:
            self.agent_id = v
        if (v := agent_config.get("agent_name")) is not None:
            self.agent_name = v
        if (v := agent_config.get("model")) is not None:
            self.model = v
        if (v := agent_config.get("model_settings")) is not None:
            self.model_settings = v
        if (v := agent_config.get("system_prompt")) is not None:
            self.system_prompt = v
        if (v := agent_config.get("description")) is not None:
            self.description = v
        if (v := agent_config.get("tools_names")) is not None:
            self.tools_names = v
        if (v := agent_config.get("custom_tools")) is not None:
            self.custom_tools = v
        if (v := agent_config.get("rag")) is not None:
            self.knowledge_base = v
        if (v := agent_config.get("working_files")) is not None:
            self.working_files = v
        if (v := agent_config.get("working_dbs")) is not None:
            self.working_databases = v
    # endregion


def _coerce_list_of_str(value: Any) -> Optional[list[str]]:
    """Normalize arbitrary input into a list of strings when possible.

    Args:
        value (Any): Valor original que pode representar uma lista ou elemento único.

    Returns:
        Optional[list[str]]: Lista de strings convertidas ou `None` se a conversão não for viável.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [str(v) for v in value]
    # Single string -> list
    if isinstance(value, str):
        return [value]
    # Fallback: try to iterate
    try:
        return [str(v) for v in value]
    except Exception:
        return None


def _default_system_prompt(agent_name: str) -> str:
    """Generate the default system prompt text for the agent.

    Args:
        agent_name (str): Nome do agente usado na saudação.

    Returns:
        str: Texto de prompt padrão a ser usado pelo agente.
    """
    return f"Você é um assistente prestativo. Seu nome é {agent_name}."


def _ensure_list(value: Optional[list[str]]) -> list[str]:
    """Ensure the provided value is a list, returning an empty list otherwise.

    Args:
        value (Optional[list[str]]): Lista opcional de strings.

    Returns:
        list[str]: Lista original ou uma nova lista vazia.
    """
    return value if isinstance(value, list) else []


def _ensure_str_or_none(value: Any) -> Optional[str]:
    """Convert a value to string when available, preserving `None`.

    Args:
        value (Any): Valor a ser convertido.

    Returns:
        Optional[str]: String convertida ou `None` quando o valor é nulo.
    """
    if value is None:
        return None
    return str(value)


def _ensure_dict_or_none(value: Any) -> Optional[dict[str, Any]]:
    """Attempt to coerce input to a dictionary, preserving `None`.

    Args:
        value (Any): Estrutura a ser convertida para `dict`.

    Returns:
        Optional[dict[str, Any]]: Dicionário convertido ou `None` quando indisponível.
    """
    if value is None:
        return None
    return dict(value)


def _ensure_int(value: Any, default: int) -> int:
    """Cast a value to integer, returning a fallback when conversion fails.

    Args:
        value (Any): Valor potencialmente numérico.
        default (int): Valor padrão utilizado em caso de falha.

    Returns:
        int: Inteiro convertido ou o valor padrão.
    """
    try:
        return int(value)
    except Exception:
        return default


def _validate_model_settings(value: Any) -> Optional[dict[str, Any]]:
    """Validate that model settings are dictionary-like.

    Args:
        value (Any): Estrutura de configuração fornecida.

    Returns:
        Optional[dict[str, Any]]: Dicionário com as configurações ou `None` quando inválido.
    """
    if value is None:
        return None
    try:
        return dict(value)
    except Exception:
        return None


def _validate_working_lists(cfg: AgentConfig) -> None:
    """Normalize list-based fields for the provided configuration object.

    Args:
        cfg (AgentConfig): Instância que será atualizada in-place.

    Returns:
        None: Apenas ajusta os atributos `tools_names`, `working_files` e `working_dbs`.
    """
    cfg.tools_names = _ensure_list(_coerce_list_of_str(cfg.tools_names))


def _validate_strings(cfg: AgentConfig) -> None:
    """Guarantee that string-based fields are populated with coherent defaults.

    Args:
        cfg (AgentConfig): Instância de configuração a ser ajustada.

    Returns:
        None: Atualiza atributos de forma destrutiva na instância recebida.
    """
    cfg.agent_name = str(cfg.agent_name or "oskaragent")
    cfg.agent_id = str(cfg.agent_id or cfg.agent_name)
    cfg.model = str(cfg.model or "gpt-5")
    cfg.system_prompt = _ensure_str_or_none(cfg.system_prompt) or _default_system_prompt(cfg.agent_name)
    cfg.description = _ensure_str_or_none(cfg.description) or 'Esse é um agente de Inteligência Artificial.'


def _validate_misc(cfg: AgentConfig) -> None:
    """Handle validation of heterogeneous configuration attributes.

    Args:
        cfg (AgentConfig): Configuração a ser saneada.

    Returns:
        None: Apenas normaliza `model_settings` e `custom_tools`.
    """
    cfg.model_settings = _validate_model_settings(cfg.model_settings)
    cfg.custom_tools = _ensure_dict_or_none(cfg.custom_tools)


def _validate_dataclass(cfg: AgentConfig) -> None:
    """Run the full validation pipeline on the dataclass instance.

    Args:
        cfg (AgentConfig): Instância alvo da validação.

    Returns:
        None: O procedimento atualiza os campos existentes sem retorno.
    """
    _validate_strings(cfg)
    _validate_working_lists(cfg)
    _validate_misc(cfg)


def _validate(self: AgentConfig) -> None:
    """Invoke the standalone validation routine bound to the dataclass.

    Returns:
        None: Encaminha a chamada para `_validate_dataclass` sem retorno explícito.
    """
    _validate_dataclass(self)


AgentConfig._validate = _validate  # type: ignore[attr-defined]
