from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import secrets
import string
from datetime import datetime
from typing import Optional, Callable
from colorama import Fore, Style, init as colorama_init
from dataclasses import dataclass, field


# Initialize colorama once
colorama_init(autoreset=True)


_COLOR_MAP = {
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "RED": Fore.RED,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE,
    "RESET": Style.RESET_ALL,
}

# Types
ToolFn = Callable[..., Any]


def log_msg(message: str, *, func: str = "", action: str = "", color: str = "BLUE") -> None:
    """Log a colorized message with contextual metadata.

    Args:
        message (str): Texto principal que será impresso no log.
        func (str, optional): Nome da função que originou o log. Defaults to "".
        action (str, optional): Identificador adicional para a ação relacionada. Defaults to "".
        color (str, optional): Código de cor aceito por `colorama` para o texto. Defaults to "BLUE".

    Returns:
        None: Esta função não retorna valor; apenas escreve na saída padrão.
    """
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        col = _COLOR_MAP.get(color.upper(), Fore.BLUE)
        reset = Style.RESET_ALL
        func_part = f" [func={func}]" if func else ""
        action_part = f" [action={action}]" if action else ""
        print(f"{col}[{ts}]{func_part}{action_part} {message}{reset}")

    except Exception:
        # Fallback to plain print if anything goes wrong
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {message}")


def gen_randon_filename(name_length: int = 10, prefix: str = "") -> str:
    """Generate a random filename composed of ASCII letters and digits.

    Args:
        name_length (int, optional): Quantidade de caracteres aleatórios desejada. Defaults to 10.
        prefix (str, optional): Texto opcional a ser prefixado ao nome gerado. Defaults to "".

    Returns:
        str: Nome de arquivo construído a partir do prefixo (quando fornecido) seguido dos caracteres randômicos.
    """
    chars = string.ascii_letters + string.digits
    base_name = ''.join(secrets.choice(chars) for _ in range(name_length))
    return prefix + base_name


@dataclass
class ToolContext:
    session_id: str
    message_id: str
    agent_id: str
    is_verbose: bool = False
    input_data: dict[str, Any] = field(default_factory=dict)
    subordinate_agents: list[Any] = field(default_factory=list)
    custom_tools_info: dict[str, Any] = field(default_factory=dict)
    retrievers: list[Any] = field(default_factory=list)
    working_folder: Optional[str] = None
    knowledge_base: Optional[list[dict[str, Any]]] = None


def vlog(ctx: "ToolContext | None", message: str, *, func: str = "") -> None:
    """Print verbose diagnostic logs when the tool context requires it.

    Args:
        ctx (ToolContext | None): Contexto da execução da ferramenta, contendo flag `is_verbose`.
        message (str): Texto que será emitido no log.
        func (str, optional): Nome da função geradora da mensagem. Defaults to "".

    Returns:
        None: Apenas encaminha mensagens para `log_msg` quando habilitado.
    """
    if ctx and getattr(ctx, "is_verbose", False):
        log_msg(message, func=func or "tool", action="tool", color="MAGENTA")


def render_file_as_content_blocks(file_path: str) -> list[dict[str, Any]]:
    """Converte um arquivo em blocos compatíveis com a Responses API.

    Args:
        file_path (str): Caminho absoluto ou relativo para o arquivo de entrada.

    Returns:
        list[dict[str, Any]]: Coleção de blocos estruturados (`input_text` ou `input_image`).

    Raises:
        ValueError: Quando o arquivo não pode ser lido, excede limites ou possui tipo não suportado.
    """
    # Extract filename from path
    filename = os.path.basename(file_path)

    # 1. Carregar o JSON como texto puro
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 2. Definir tamanho dos pedaços (chunks)
    CHUNK_SIZE = 50_000

    chunks = [
        text[i:i + CHUNK_SIZE]
        for i in range(0, len(text), CHUNK_SIZE)
    ]

    # 3. Construir as mensagens a serem enviadas
    messages = [
        {
            "type": "input_text",
            "text": (
                f"Vou enviar o conteúdo de do arquivo '{filename}' em múltiplas partes. "
                "Não responda ainda. Apenas armazene cada parte. "
                "Quando eu enviar a mensagem FINAL, você terá o arquivo inteiro."
            )
        }
    ]

    # Inserir cada pedaço como mensagem separada
    for i, chunk in enumerate(chunks):
        messages.append(
            {
                "type": "input_text",
                "text": f"[PARTE {i + 1}/{len(chunks)}]\n{chunk}"
            }
        )
    # Mensagem final instruindo o modelo a analisar os dados
    messages.append({
        "type": "input_text",
        "text": (
            f"FINAL. Agora que você recebeu todas as partes do arquivo {filename}, "
            "analise o conteúdo completo e produza a resposta solicitada."
        )
    })

    return messages


def get_working_folder_path(session_id: str) -> Path:
    # cria o nome da pasta de trabalho se uma sessão
    base = Path("_oskar_working_folder") / session_id
    return Path(base)

def create_working_folder(session_id: str) -> str:
    # cria uma pasta de trabalho para manter os arquivos temporários, se a pasta não existir
    session_dir = get_working_folder_path(session_id)
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir.resolve().as_posix()
