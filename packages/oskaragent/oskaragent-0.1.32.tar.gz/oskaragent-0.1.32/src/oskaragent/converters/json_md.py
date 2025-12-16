from __future__ import annotations

import re


def convert_dict_to_markdown(data: dict, md_path: str) -> str:
    """Serialize a dictionary structure to a Markdown document.

    Args:
        data (dict): Dados estruturados que serão convertidos.
        md_path (str): Caminho de destino para o arquivo Markdown.

    Returns:
        str: Caminho do arquivo Markdown gravado.
    """
    text = convert_json_to_markdown(data)

    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(text)

    return md_path


def convert_json_to_markdown(json_data: dict | list, doc_title: str = "Documento") -> str:
    """Serialize dictionaries or lists into a Markdown document.

    Args:
        json_data (dict | list): Estrutura de dados que será convertida.
        doc_title (str, optional): Título principal do documento. Defaults to "Documento".

    Returns:
        str: Representação em Markdown do conteúdo fornecido.
    """

    def _dump_value(value) -> str:
        """Convert primitive values to string literals for Markdown output."""
        if isinstance(value, bool):
            return 'True' if value else 'False'

        return f"{value}"

    def _get_label_from_camel_case_text(label_text: str):
        """Split camelCase strings into space-separated words."""
        words = re.sub(r'(?<!^)(?=[A-Z])', ' ', label_text)
        return words

    def _dump_json_to_md(data: dict, title: str, prefix_tit: str, level: int) -> str:
        """Build the Markdown representation for a dictionary node."""

        txt = "" if level == 1 else "\n\n\n"

        if prefix_tit:
            txt += f"{'#' * level} {prefix_tit}. {title}\n\n"
        else:
            txt += f"{'#' * level} {title}\n\n"
        # endif --

        for key, value in data.items():
            key_label = _get_label_from_camel_case_text(key)

            if isinstance(value, list):
                if len(value) > 0 and not isinstance(value[0], dict):
                    txt += f"**{key_label}**:\n"
                    for i, item in enumerate(value):
                        txt += f"{i}. {_dump_value(item)}\n"
                    # endfor --
                    txt += "\n"
                # endif --

            elif isinstance(value, str) and '\n' in value:
                txt += f"**{key_label}**:\n{value}\n\n\n"

            elif not isinstance(value, dict):
                txt += f"**{key_label}**: {_dump_value(value)}\n"
            # endif --
        # endfor --

        seq = 0
        for key, value in data.items():
            key_label = _get_label_from_camel_case_text(key)

            if isinstance(value, dict):
                seq += 1
                tit = key_label if level == 1 else f"{title} - {key_label}"
                nested_prefix = (f"{prefix_tit}." if prefix_tit else "") + f"{seq}"
                txt += _dump_json_to_md(value, title=tit, prefix_tit=nested_prefix, level=level + 1)
                txt += "\n\n"

            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    seq += 1
                    tit = key_label if level == 1 else f"{title} - {key_label}"

                    nested_prefix = f"{prefix_tit}.{seq}" if prefix_tit else f"{seq}"

                    txt += f"\n{'#' * (level + 1)} {nested_prefix}. {tit}\n\n\n"
                    tit_item = f"{key_label} - Item" if level == 1 else f"{title} - {key_label} - Item"

                    for i, item in enumerate(value):
                        txt += _dump_json_to_md(item, title=f"{tit_item} {i + 1}", prefix_tit=f"{nested_prefix}.{i + 1}", level=level + 2)
                    # endfor --

                    txt += "\n\n"
                # endif --
        # endfor --

        return txt

    if isinstance(json_data, dict):
        return _dump_json_to_md(json_data, title=doc_title, prefix_tit="", level=1)
    # endif --

    text = ""
    for element in json_data:
        text += _dump_json_to_md(element, title=doc_title, prefix_tit="", level=1)
        text += "\n\n\n"
    # endfor --

    return text
