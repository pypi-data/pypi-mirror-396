from __future__ import annotations

import base64
import secrets
import string
import zlib
from pathlib import Path


def encode_file(pathname: str, compress: bool = True) -> str:
    """Encode binary file contents into a JSON-safe string.

    Args:
        pathname (str): Caminho do arquivo que será codificado.
        compress (bool, optional): Indica se os bytes devem ser comprimidos com zlib antes do base64. Defaults to True.

    Returns:
        str: String codificada com prefixo `b64:` ou `b64+zlib:` suitable para persistência em JSON.
    """
    data = Path(pathname).read_bytes()
    if compress:
        data = zlib.compress(data, level=9)
        prefix = "b64+zlib:"
    else:
        prefix = "b64:"

    encoded = base64.b64encode(data).decode("ascii")
    return prefix + encoded


def decode_file_from_str(encoded_data: str, out_path: str):
    """Decode base64/zlib encoded file contents to disk.

    Args:
        encoded_data (str): String codificada com prefixo `b64:` ou `b64+zlib:`.
        out_path (str): Caminho de saída onde o arquivo decodificado será gravado.

    Returns:
        None: O conteúdo decodificado é escrito diretamente no caminho indicado.

    Raises:
        ValueError: Quando o prefixo da string não é reconhecido.
    """
    if encoded_data.startswith("b64+zlib:"):
        raw = base64.b64decode(encoded_data[len("b64+zlib:"):])
        data = zlib.decompress(raw)
    elif encoded_data.startswith("b64:"):
        data = base64.b64decode(encoded_data[len("b64:"):])
    else:
        raise ValueError("Prefixo desconhecido (esperado 'b64:' ou 'b64+zlib:').")

    Path(out_path).write_bytes(data)


def create_randon_filename(name_length: int = 10, prefix: str = "") -> str:
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