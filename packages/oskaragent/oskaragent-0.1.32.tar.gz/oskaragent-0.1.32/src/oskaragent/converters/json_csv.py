from __future__ import annotations

import csv


def convert_json_to_csv(recs_json: list, filename: str):
    """Persist a list of dictionaries as a CSV file with sanitized content.

    Args:
        recs_json (list): Conjunto de registros (dicionários) que serão exportados.
        filename (str): Caminho do arquivo CSV a ser gerado.

    Returns:
        None: O resultado é gravado diretamente no arquivo especificado.
    """
    for row in recs_json:
        for key, value in row.items():
            if isinstance(value, str):
                if len(value) > 1000:
                    value = value[:1000]
                row[key] = value.replace('\n', '\\n').replace('\\r', '')
            # endif --
        # endfor --
    # endfor --

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=recs_json[0].keys(), quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(recs_json)

