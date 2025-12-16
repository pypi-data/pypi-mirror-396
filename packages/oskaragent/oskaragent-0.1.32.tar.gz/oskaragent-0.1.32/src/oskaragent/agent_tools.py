from __future__ import annotations

import asyncio
import ast
import base64
import datetime as dt
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Optional

from .helpers import ToolContext, ToolFn, log_msg, vlog
from .rag.knowledgebase import query_knowledge_base, search_web
from .helpers import create_working_folder

# Default tools available in every agent (always allowed)
DEFAULT_TOOL_NAMES: tuple[str, ...] = (
    "calculator_tool",
    "get_current_date_tool",
    "get_current_time_tool",
)


@dataclass(slots=True)
class ToolExecutionPolicy:
    """Define parâmetros de resiliência aplicados às ferramentas."""

    timeout_seconds: float = 20.0


@dataclass(slots=True)
class ToolExecutionResult:
    """Representa o resultado de uma ferramenta com metadados de execução."""

    value: Any | None
    elapsed_seconds: float
    error: str | None = None

    def to_model_payload(self) -> Any:
        """Normaliza o resultado para ser devolvido ao modelo."""
        if self.error:
            return {"error": self.error}
        return self.value


def _execute_tool_with_policy(tool_name: str,
                              tool_fn: ToolFn,
                              args_obj: dict[str, Any],
                              ctx: ToolContext,
                              policy: ToolExecutionPolicy,
                              runner: Callable[[], Any] | None = None) -> ToolExecutionResult:
    """Executa uma ferramenta aplicando timeout e logging estruturado."""
    start = time.perf_counter()
    msg_id = getattr(ctx, "message_id", "-")
    if getattr(ctx, "is_verbose", False):
        log_msg(f"id={msg_id} tool_start name={tool_name}", func="tool_runner", action="tools", color="MAGENTA")

    with ThreadPoolExecutor(max_workers=1) as executor:
        callable_to_run = runner or (lambda: exec_tool(tool_name, tool_fn, args_obj, ctx))
        future = executor.submit(callable_to_run)
        try:
            value = future.result(timeout=max(policy.timeout_seconds, 0.1))
            elapsed = time.perf_counter() - start
            if getattr(ctx, "is_verbose", False):
                log_msg(
                    f"id={msg_id} tool_end name={tool_name} elapsed={elapsed:.2f}s",
                    func="tool_runner",
                    action="tools",
                    color="MAGENTA",
                )
            return ToolExecutionResult(value=value, elapsed_seconds=elapsed)
        except TimeoutError:
            future.cancel()
            elapsed = time.perf_counter() - start
            err = f"Tempo excedido após {policy.timeout_seconds}s."
            log_msg(f"id={msg_id} tool_timeout name={tool_name} {err}", func="tool_runner", action="tools", color="RED")
            return ToolExecutionResult(value=None, elapsed_seconds=elapsed, error=err)
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - start
            err = f"Erro ao executar ferramenta {tool_name}: {exc}"
            log_msg(f"id={msg_id} tool_error name={tool_name} {err}", func="tool_runner", action="tools", color="RED")
            return ToolExecutionResult(value=None, elapsed_seconds=elapsed, error=err)


def calculator_tool(expression: str, *, ctx: ToolContext | None = None) -> Any:
    """Evaluate arithmetic expressions using a restricted math namespace.

    Args:
        expression (str): Expressão Python focada em operações matemáticas.
        ctx (ToolContext | None, optional): Contexto opcional usado para logs verbosos. Defaults to None.

    Returns:
        Any: Resultado numérico da expressão avaliada.

    Raises:
        ValueError: Quando a expressão contém construções não permitidas ou apresenta erro de sintaxe.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="calculator_tool")

    # Whitelist public attributes from math
    allowed_math = {k: v for k, v in vars(math).items() if not k.startswith("_")}
    # Expose as bare names and under a `math` namespace
    allowed_names: dict[str, Any] = dict(allowed_math)
    allowed_names["math"] = SimpleNamespace(**allowed_math)
    # A few safe builtins commonly used in numeric expressions
    allowed_names.update({
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "round": round,
        "pow": pow,
    })

    # Validate AST to allow only arithmetic expressions and math calls
    allowed_builtin_names = {"abs", "min", "max", "sum", "round", "pow"}
    allowed_math_names = set(allowed_math.keys())

    def _is_safe(node: ast.AST) -> bool:
        """Check whether the AST node uses only whitelisted constructs.

        Args:
            node (ast.AST): Nó produzido pelo parse da expressão fornecida.

        Returns:
            bool: `True` quando o nó é considerado seguro, caso contrário `False`.
        """
        # Expression root
        if isinstance(node, ast.Expression):
            return _is_safe(node.body)

        # Literals
        if isinstance(node, (ast.Num, ast.Constant)):
            return isinstance(getattr(node, "value", None), (int, float)) or isinstance(node, ast.Num)

        # Names (variables/constants): must be in allowed (math names or allowed builtins or 'math')
        if isinstance(node, ast.Name):
            return node.id in allowed_math_names or node.id in allowed_builtin_names or node.id == "math"

        # Attribute access: only math.<public_name>
        if isinstance(node, ast.Attribute):
            return isinstance(node.value, ast.Name) and node.value.id == "math" and node.attr in allowed_math_names

        # Unary operations: +x, -x
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return _is_safe(node.operand)

        # Binary operations: + - * / // % **
        if isinstance(node, ast.BinOp) and isinstance(node.op,
                                                      (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
                                                       ast.Pow)):
            return _is_safe(node.left) and _is_safe(node.right)

        # Calls: function(...) where function is allowed
        if isinstance(node, ast.Call):
            func_ok = False
            if isinstance(node.func, ast.Name):
                func_ok = node.func.id in allowed_math_names or node.func.id in allowed_builtin_names
            elif isinstance(node.func, ast.Attribute):
                func_ok = isinstance(node.func.value,
                                     ast.Name) and node.func.value.id == "math" and node.func.attr in allowed_math_names
            if not func_ok:
                return False
            # Validate args and keywords values only (no starargs/kwargs nodes in py3.12 AST here)
            return all(_is_safe(a) for a in node.args) and all(_is_safe(kw.value) for kw in node.keywords)

        # Parentheses/grouping is represented implicitly; tuples can appear only if used in args
        if isinstance(node, ast.Tuple):
            return all(_is_safe(elt) for elt in node.elts)

        # Disallow everything else
        return False

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Expressão inválida: {e}")
    if not _is_safe(tree):
        raise ValueError("Expressão contém construções não permitidas para cálculo seguro.")

    code = compile(tree, "<calc>", "eval")
    result = eval(code, {"__builtins__": {}}, allowed_names)
    return result


def get_current_date_tool(*, ctx: ToolContext | None = None) -> str:
    """Retrieve the current system date.

    Args:
        ctx (ToolContext | None, optional): Contexto do agente usado apenas para logging. Defaults to None.

    Returns:
        str: Data atual formatada como `YYYY-MM-DD`.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="get_current_date_tool")

    return dt.date.today().isoformat()


def get_current_time_tool(*, ctx: ToolContext | None = None) -> str:
    """Retrieve the current system time.

    Args:
        ctx (ToolContext | None, optional): Contexto do agente usado apenas para logging. Defaults to None.

    Returns:
        str: Hora atual formatada como `HH:MM:SS`.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="get_current_time_tool")

    return dt.datetime.now().time().replace(microsecond=0).isoformat()


async def _run_code_async(code: str, output_dir: Path, *, message_id: str | None = None) -> Any:
    """Execute user-provided Python code inside a constrained async sandbox.

    Args:
        code (str): Script Python sincronizado/assíncrono a ser executado.
        output_dir (Path | None, optional): Diretório onde artefatos (logs, imagens) serão gravados. Defaults to None.
        message_id (str | None, optional): Identificador da mensagem usado para nomear arquivos de saída. Defaults to None.

    Returns:
        Any: Valor produzido pelo script, incluindo estruturas com imagens em base64 quando aplicável.

    Raises:
        ImportError: Quando o script tenta importar módulos não autorizados explicitamente.
        Exception: Propaga exceções geradas durante a execução do código do usuário.
    """
    local_vars: dict[str, Any] = {}
    captured_paths: list[str] = []
    # Minimal, sandboxed execution context with restricted imports
    import builtins as _py_builtins  # defer until here
    import random as _rand

    allowed_top_imports = {
        "math",
        "json",
        "re",
        "random",
        "statistics",
        "datetime",
        "time",
        "asyncio",
        "matplotlib",
        "numpy",
        "os",
        "pandas",
        "base64",
        "seaborn",
        "unicodedata",
        # submodules like 'matplotlib.pyplot' are permitted via top-level 'matplotlib'
    }

    def _patched_show(*args, **kwargs):  # type: ignore[no-untyped-def]
        """Persist matplotlib figures to disk instead of displaying them.

        Args:
            *args: Argumentos posicionais encaminhados para `matplotlib.pyplot.show`.
            **kwargs: Argumentos nomeados encaminhados para `matplotlib.pyplot.show`.

        Returns:
            None: A função intercepta a chamada padrão e salva as figuras como arquivos PNG.
        """
        try:
            from matplotlib import pyplot as plt  # type: ignore
            nums = plt.get_fignums()
            saved: list[str] = []
            for number in nums:
                figure = plt.figure(number)
                # File name must follow: "<message_id>-<X>.png" where X is [1..100]
                msg_id = str(message_id) if message_id else "default"
                for _ in range(5):
                    x = _rand.randint(1, 100)
                    fname = f"{msg_id}-{x}.png"
                    path = output_dir / fname
                    if not path.exists():
                        break
                else:
                    # Fallback (very unlikely) after retries
                    x = _rand.randint(101, 1000)
                    fname = f"{msg_id}-{x}.png"

                path = output_dir / fname
                figure.savefig(path)
                saved.append(str(path))
            captured_paths.extend(saved)
        except Exception as _e:  # noqa: F841
            pass
        return None

    def _safe_import(name, func_globals=None, func_locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        """Restrict imports to a curated allowlist during code execution.

        Args:
            name: Nome do módulo solicitado.
            func_globals: Dicionário de globais herdado da chamada original.
            func_locals: Espaço local repassado pela função `__import__`.
            fromlist: Lista de objetos a serem importados do módulo alvo.
            level: Nível de importação relativa.

        Returns:
            Any: Módulo importado conforme requerido.

        Raises:
            ImportError: Quando o módulo solicitado não está na lista permitida.
        """
        top = name.split(".", 1)[0]
        if top not in allowed_top_imports:
            raise ImportError(f"Importação não permitida: {name}")
        mod = _py_builtins.__import__(name, func_globals, func_locals, fromlist, level)

        # Monkeypatch pyplot.show on demand
        try:
            if name == "matplotlib.pyplot" or (
                    top == "matplotlib" and isinstance(fromlist, (list, tuple)) and "pyplot" in fromlist):
                import matplotlib.pyplot as plt  # type: ignore
                plt.show = _patched_show  # type: ignore[attr-defined]
        except Exception:
            pass

        return mod

    # Prefer a headless backend for matplotlib operations
    try:
        os.environ.setdefault("MPLBACKEND", "Agg")
    except Exception:
        pass

    # Proactively patch pyplot.show before user code runs
    try:
        import matplotlib  # type: ignore
        # Ensure non-interactive backend if not already set
        try:
            import matplotlib.pyplot as _plt  # type: ignore
            _plt.show = _patched_show  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception:
        pass

    safe_builtins: dict[str, Any] = {
        "__import__": _safe_import,
        "print": print,
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
        "round": round,
        "Exception": Exception,
        "ValueError": ValueError,
        "isinstance": isinstance,
        "str": str,
        "int": int,
        "float": float,
        "set": set,
        "list": list,
        "zip": zip,
    }
    # Expose optional modules (pandas may be missing in some environments)
    try:
        import pandas as _pd  # type: ignore
    except ImportError:
        _pd = None
    import unicodedata as _unicodedata
    import re as _re
    try:
        import seaborn as _sns  # type: ignore
    except ImportError:
        _sns = None

    # Capture stdout/stderr produced by the executed code
    import io
    from contextlib import redirect_stdout, redirect_stderr

    exec_globals: dict[str, Any] = {"__builtins__": safe_builtins, "asyncio": asyncio, "os": os, "unicodedata": _unicodedata, "base64": base64, "re": _re}
    if _pd is not None:
        exec_globals["pandas"] = _pd
        exec_globals["pd"] = _pd
    if _sns is not None:
        exec_globals["seaborn"] = _sns
        exec_globals["sns"] = _sns
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        exec(code, exec_globals, local_vars)

    # If no images were captured via patched show, try to save any open figures
    if not captured_paths:
        try:
            from matplotlib import pyplot as _plt2  # type: ignore
            nums2 = _plt2.get_fignums()
            if nums2:
                for num in nums2:
                    fig = _plt2.figure(num)
                    mid2 = str(message_id) if message_id else "default"
                    base_dir2 = output_dir
                    for _ in range(5):
                        x2 = _rand.randint(1, 100)
                        fname2 = f"{mid2}-{x2}.png"
                        path2 = base_dir2 / fname2
                        if not path2.exists():
                            break
                    else:
                        x2 = _rand.randint(1, 100)
                        fname2 = f"{mid2}-{x2}.png"
                        path2 = base_dir2 / fname2
                    path2.parent.mkdir(parents=True, exist_ok=True)
                    fig.savefig(path2)
                    captured_paths.append(str(path2))
        except Exception:
            pass

    # Build result structure
    result_val = local_vars.get("result")

    # Persist script output to file (always). Filename must be prefixed by `message_id`.
    try:
        base_dir = output_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        mid = str(message_id) if message_id else "default"
        out_file = base_dir / f"{mid}_python_output.json"
        payload: dict[str, Any] = {
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "result": result_val,
            "images": captured_paths[:],
        }
        try:
            import json as _json
            out_file.write_text(_json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            # Fallback to a plain-text serialization
            text = (
                "# Script output (stdout)\n" + payload["stdout"] +
                "\n# Errors (stderr)\n" + payload["stderr"] +
                "\n# Result\n" + str(payload["result"]) +
                "\n# Images\n" + "\n".join(payload["images"])
            )
            out_file.write_text(text, encoding="utf-8")
    except Exception:
        pass

    if captured_paths:
        images: list[dict[str, str]] = []
        for p in captured_paths:
            try:
                data = Path(p).read_bytes()
                images.append({"path": p, "base64": base64.b64encode(data).decode("ascii")})
            except Exception:
                images.append({"path": p, "base64": ""})
        if result_val is None:
            return {"images": images}
        return {"result": result_val, "images": images}
    return result_val


def _run_coro_in_thread(coro):  # type: ignore[no-untyped-def]
    """Execute an async coroutine inside a dedicated worker thread.

    Args:
        coro: Coroutine que será executada utilizando `asyncio.run`.

    Returns:
        Any: Resultado produzido pela coroutine após a conclusão.

    Raises:
        BaseException: Repropaga exceções levantadas pela coroutine.
    """
    result_holder: dict[str, Any] = {}
    error_holder: dict[str, BaseException] = {}

    def _target():
        """Wrapper responsável por executar a coroutine e capturar resultados.

        Returns:
            None: Apenas atualiza `result_holder` ou `error_holder`.
        """
        try:
            result_holder["value"] = asyncio.run(coro)
        except BaseException as e:  # capture to re-raise in caller thread
            error_holder["error"] = e

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join()
    if "error" in error_holder:
        raise error_holder["error"]
    return result_holder.get("value")


def execute_python_code_tool(code: str, *, ctx: ToolContext | None = None) -> Any:
    """Execute Python code in a sandbox honoring the agent session context.

    Args:
        code (str): Script Python a ser executado, preferencialmente atribuindo saídas à variável `result`.
        ctx (ToolContext | None, optional): Contexto da ferramenta contendo diretórios de trabalho e ids. Defaults to None.

    Returns:
        Any: Resultado retornado pela execução (_stdout_, _stderr_ e possíveis imagens).

    Raises:
        ImportError: Quando o script tenta importar módulos não permitidos.
        BaseException: Propaga quaisquer erros levantados durante a execução do código do usuário.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="ao")

    out_dir = Path(create_working_folder(getattr(ctx, "session_id", "default_session_id")))
    message_id = getattr(ctx, "message_id", None) if ctx else None

    try:
        loop = asyncio.get_running_loop()
        # If a loop exists and is running (e.g., notebooks), avoid run_until_complete
        if getattr(loop, "is_running", lambda: False)():
            return _run_coro_in_thread(_run_code_async(code, output_dir=out_dir, message_id=message_id))
        # No running loop in this thread; safe to use run_until_complete
        return loop.run_until_complete(_run_code_async(code, output_dir=out_dir, message_id=message_id))  # type: ignore[func-returns-value]
    except RuntimeError:
        # No current loop; use asyncio.run
        return asyncio.run(_run_code_async(code, output_dir=out_dir, message_id=message_id))
    except Exception:
        # As a last resort, run in a fresh thread loop
        return _run_coro_in_thread(_run_code_async(code, output_dir=out_dir, message_id=message_id))


def retriever_tool(source_name: str, query: str, *, top_k: int = 5,
                   ctx: ToolContext | None = None) -> list[str]:
    """Retrieve relevant documents via the configured vector store.

    Args:
        source_name (str): Nome da fonte de dados.
        query (str): Texto usado como chave de busca semântica.
        top_k (int, optional): Quantidade de documentos que devem ser retornados. Defaults to 4.
        ctx (ToolContext | None, optional): Contexto utilizado para logs verbosos. Defaults to None.

    Returns:
        list[str]: Lista de conteúdos/documentos similares ou vazia quando não há resultados.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="retriever_tool")

    retrievers = getattr(ctx, "retrievers")
    if retrievers is None:
        return []

    for retriever_info in retrievers:
        if retriever_info["name"] != source_name:
            continue

        try:
            results = query_knowledge_base(query=query,
                                           knowledge_base_name=retriever_info['name'],
                                           knowledge_base_folder=retriever_info["details"]['kb_path'],
                                           num_of_itens=top_k)
            return results
        except Exception as e:
            # Log error with details and return a structured error item to surface the issue
            vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func=f"retriever_tool ==> ERROR: {str(e)}")

    return []


def search_web_tool(query: str, *, ctx: ToolContext | None = None) -> str | None:
    """Proxy to perform web searches when allowed by the environment.

    Args:
        query (str): Termo que será consultado externamente.
        ctx (ToolContext | None, optional): Contexto do agente usado para logging. Defaults to None.

    Returns:
        list[dict[str, Any]]: Lista de resultados estruturados; vazia quando a funcionalidade não está disponível.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"session={getattr(ctx, 'session_id', '-')}", func="search_web_tool")

    return search_web(query)


def read_file_tool(filename: str, *, as_base64: bool = False,
                   ctx: ToolContext | None = None) -> str:
    """Read file contents relative to the agent workspace.

    Args:
        filename (str): nome do arquivo que será lido (sem caminho relativo)..
        as_base64 (bool, optional): Quando `True`, retorna o conteúdo codificado em base64. Defaults to False.
        ctx (ToolContext | None, optional): Contexto usado para identificar sessão e diretórios. Defaults to None.

    Returns:
        str: Conteúdo textual (ou base64) do arquivo solicitado.

    Raises:
        FileNotFoundError: Se o arquivo não puder ser localizado.
        OSError: Para erros de leitura de arquivo.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"filename={filename}", func="read_file_tool")

    file_path = Path(create_working_folder(getattr(ctx, "session_id", "default_session_id"))) / filename

    data = file_path.read_bytes()
    if as_base64:
        return base64.b64encode(data).decode("ascii")
    # Heuristic: decode as utf-8 with fallback replacement
    return data.decode("utf-8", errors="replace")


def write_file_tool(filename: str, content: str, *,
                    ctx: ToolContext | None = None) -> str:
    """Persist textual content to disk within the agent session scope.

    Args:
        filename (str): Nome ou caminho desejado para o arquivo final.
        content (str): Conteúdo textual a ser gravado.
        ctx (ToolContext | None, optional): Contexto de execução contendo `session_id` e `message_id`. Defaults to None.

    Returns:
        str: Mensagem de status sobre a gravação do arquivo.

    Raises:
        OSError: Caso ocorra erro ao criar diretórios ou gravar o conteúdo.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"[tool] write_file_tool() called; path={filename}")

    message_id = getattr(ctx, "message_id", None) if ctx else None
    safe_filename = f"{message_id}_{filename}" if message_id else filename
    file_path = Path(create_working_folder(getattr(ctx, "session_id", "default_session_id"))) / safe_filename
    file_path.write_text(content, encoding="utf-8")
    return "Arquivo salvo com sucesso."


def ask_to_agent_tool(agent_id: str, question: str, *, ctx: ToolContext | None = None) -> str:
    """Forward a prompt to a subordinate agent registered in the context.

    Args:
        agent_id (str): Identificador único do agente que receberá a pergunta.
        question (str): Texto da consulta a ser encaminhada.
        ctx (ToolContext | None, optional): Contexto contendo a lista de agentes subordinados. Defaults to None.

    Returns:
        str: Resposta formatada do agente consultado ou mensagem informando que não foi encontrado.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        vlog(ctx, f"[tool] ask_to_agent_tool() called; session={getattr(ctx, 'session_id', '-')}")

    subordinate_agents = getattr(ctx, "subordinate_agents", [])
    agent = next((a for a in subordinate_agents if a.id == agent_id), None)

    if agent is None:
        vlog(ctx, f"[tool] ask_to_agent_tool() called; session={getattr(ctx, 'session_id', '-')}; agent {agent_id} not found")
        return f"O agente {agent_id} não foi encontrado"

    result: dict[str, Any] = agent.answer(
        question=question,
        action="consult",
        message_format="raw",
        is_consult_prompt=True,
    )

    # submete a pergunta/pedido para o agente
    answer = (result or {}).get("content") or ""
    return f"Segue a resposta do agente:\n {answer}"


def get_builtin_tools(*,
                      working_folder: Optional[str] = None) -> dict[str, ToolFn]:
    """Return the registry of builtin tools available to oskaragent.

    Args:
        working_folder (Optional[str], optional): Diretório raiz utilizado para tool de arquivo. Defaults to None.

    Returns:
        dict[str, ToolFn]: Mapeamento entre nomes de ferramentas e funções executáveis.
    """
    base = working_folder
    tools = {
        "calculator_tool": calculator_tool,
        "get_current_date_tool": get_current_date_tool,
        "get_current_time_tool": get_current_time_tool,
        "execute_python_code_tool": execute_python_code_tool,
        "retriever_tool": (
            lambda source_name, query, top_k=4, *, ctx=None: retriever_tool(source_name, query, top_k=top_k, ctx=ctx)),
        "search_web_tool": search_web_tool,
        "read_file_tool": (
            lambda filename, as_base64=False, *, ctx=None: read_file_tool(filename, as_base64=as_base64, ctx=ctx)),
        "write_file_tool": (lambda filename, content, *, ctx=None: write_file_tool(filename, content, ctx=ctx)),
        "ask_to_agent_tool": (lambda agent_id, question, *, ctx=None: ask_to_agent_tool(agent_id, question, ctx=ctx)),
    }

    return tools


def build_tool_schemas(tool_names: Iterable[str]) -> list[dict[str, Any]]:
    """Generate minimal JSON schema definitions for API-exposed tools.

    Args:
        tool_names (Iterable[str]): Conjunto de nomes de ferramentas permitidos na sessão.

    Returns:
        list[dict[str, Any]]: Lista de esquemas no formato esperado pela OpenAI Responses API.
    """
    schemas: list[dict[str, Any]] = []
    for name in tool_names:
        if name == "calculator_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Avalia uma expressão matemática Python segura. Essa função precisa receber como argumento uma expressão matemática Python segura.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Expressão matemática Python segura"},
                    },
                    "required": ["expression"],
                    "additionalProperties": False,
                },
            })

        elif name in ("get_current_date_tool", "get_current_time_tool"):
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Retorna a data/horário atual.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            })

        elif name == "retriever_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Busca dados relevantes no índice local (RAG). Essa função precisa receber dois argumentos: nome da fonte de dados e 'query'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_name": {"type": "string", "description": "Nome da fonte de dados"},
                        "query": {"type": "string", "description": "Texto para pesquisa"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                    "required": ["source_name", "query"],
                    "additionalProperties": False,
                },
            })

        elif name == "search_web_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Faz busca na web. Essa função precisa receber como argumento o texto para pesquisa.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Texto para pesquisa"},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            })

        elif name == "execute_python_code_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Executa código Python assíncrono controlado (retorna variável 'result'). Essa função precisa receber como argumento o script a ser executado.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Código Python a ser executado"},
                    },
                    "required": ["code"],
                    "additionalProperties": False,
                },
            })

        elif name == "read_file_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Use essa ferramenta para ler dados de um arquivo. Essa função precisa receber como argumento o nome do arquivo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Nome do arquivo"},
                        "as_base64": {"type": "boolean", "default": False},
                    },
                    "required": ["filename"],
                    "additionalProperties": False,
                },

            })

        elif name == "write_file_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Use essa ferramenta para salvar/gravar dados num arquivo. Essa função precisa receber dois argumentos do tipo string: nome do arquivo e conteúdo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Nome do arquivo"},
                        "content": {"type": "string", "description": "Conteúdo do arquivo"},
                    },
                    "required": ["filename", "content"],
                    "additionalProperties": False,
                },
            })

        elif name == "ask_to_agent_tool":
            schemas.append({
                "type": "function",
                "name": name,
                "description": "Use essa ferramenta para fazer perguntas/pedidos para outros agentes. Essa função precisa receber dois argumentos do tipo string: nome do agente e pergunta/pedido.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Identificação do agente que será consultado"},
                        "question": {"type": "string", "description": "Pergunta ou pedido para o agente"},
                    },
                    "required": ["agent_id", "question"],
                    "additionalProperties": False,
                },
            })

    return schemas

def exec_tool(tool_name: str, tool_fn, args_obj: dict[str, Any], ctx: ToolContext) -> Any:
    """Execute a tool by name and arguments."""
    tool_result = None
    match tool_name:
        case "calculator_tool":
            expr = args_obj.get("expression") or args_obj.get("expr") or args_obj.get(
                    "code") or ""
            tool_result = tool_fn(expression=str(expr), ctx=ctx)

        case "search_web_tool":
            q = args_obj.get("query") or args_obj.get("q") or args_obj.get("text") or ""
            tool_result = tool_fn(query=str(q), ctx=ctx)

        case "retriever_tool":
            source_name = args_obj.get("source_name") or args_obj.get("source") or args_obj.get("name") or ""
            q = args_obj.get("query") or args_obj.get("q") or args_obj.get("text") or ""
            top_k = args_obj.get("top_k") or 4
            tool_result = tool_fn(source_name=str(source_name), query=str(q), top_k=int(top_k), ctx=ctx)

        case "execute_python_code_tool":
            code = args_obj.get("code") or args_obj.get("source") or args_obj.get(
                    "python") or ""
            tool_result = tool_fn(code=str(code), ctx=ctx)

        case "read_file_tool":
            filename = args_obj.get("filename") or args_obj.get("file") or ""
            as_b64 = bool(args_obj.get("as_base64", False))
            tool_result = tool_fn(filename=str(filename), ctx=ctx) if not as_b64 else tool_fn(filename=str(filename), as_base64=True, ctx=ctx)

        case "write_file_tool":
            filename = args_obj.get("filename") or args_obj.get("file") or ""
            content = args_obj.get("content") or args_obj.get("text") or ""
            tool_result = tool_fn(filename=str(filename), content=str(content), ctx=ctx)

        case "ask_to_agent_tool":
            agent_id = args_obj.get("agent_id") or ""
            question = args_obj.get("question") or args_obj.get("prompt") or ""
            tool_result = tool_fn(agent_id=str(agent_id), question=str(question), ctx=ctx)

        case _:
            # custom tool
            tool_result = None

    return tool_result


def execute_tool_with_policy(tool_name: str,
                             tool_fn: ToolFn,
                             args_obj: dict[str, Any],
                             ctx: ToolContext,
                             policy: ToolExecutionPolicy | None = None,
                             runner: Callable[[], Any] | None = None) -> ToolExecutionResult:
    """Roda uma ferramenta com timeout e logs consistentes."""
    selected_policy = policy or ToolExecutionPolicy()
    return _execute_tool_with_policy(tool_name, tool_fn, args_obj, ctx, selected_policy, runner=runner)
