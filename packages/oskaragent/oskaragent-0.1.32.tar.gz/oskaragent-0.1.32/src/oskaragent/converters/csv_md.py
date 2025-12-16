from __future__ import annotations

from io import StringIO

import pandas as pd


def convert_csv_to_markdown_table(csv_data: str) -> str:
    """Convert CSV text into a Markdown table representation.

    Args:
        csv_data (str): Conteúdo CSV bruto, incluindo cabeçalho.

    Returns:
        str: Tabela em formato Markdown sem índice.
    """
    df = pd.read_csv(StringIO(csv_data))
    markdown_table = df.to_markdown(index=False)

    return markdown_table
