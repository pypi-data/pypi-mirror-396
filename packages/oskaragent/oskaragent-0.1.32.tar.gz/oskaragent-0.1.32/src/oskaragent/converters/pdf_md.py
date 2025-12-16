from __future__ import annotations

import os

from .html_md import convert_markdown_to_html


def convert_pdf_to_markdown(pdf_path: str, md_path: str=None) -> str:
    """Convert a PDF document into Markdown text.

    Args:
        pdf_path (str): Caminho absoluto ou relativo do arquivo PDF a ser processado.
        md_path: Caminho de saída para o arquivo Markdown gerado.

    Returns:
        str: Caminho do arquivo Markdown gerado a partir do PDF original.

    Raises:
        FileNotFoundError: Quando o arquivo especificado não existe.
        Exception: Para falhas durante a extração de conteúdo do PDF.
    """
    # pip install pdfminer.six
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer

    _, filename = os.path.split(pdf_path)

    if not os.path.exists(pdf_path) or not os.path.isfile(pdf_path):
        raise Exception(f"*** Erro: o arquivo '{filename}' não existe!")
    # endif --

    md_filename = pdf_path[:-4] + '.md' if md_path is None else md_path

    if os.path.exists(md_filename):
        os.remove(md_filename)
    # endif --

    # extrai o texto do PDF
    pages = extract_pages(pdf_path)

    def _is_title(text: str) -> bool:
        """Check whether a text snippet should be treated as a heading.

        Args:
            text (str): Linha analisada a partir do PDF.

        Returns:
            bool: `True` se a linha aparenta representar um título; caso contrário `False`.
        """
        if 5 <= len(text) <= 120 and (text[0].isupper() or text[0].isdigit()) and (
                ':' not in text and
                '=' not in text and
                not text.startswith('Figure ') and
                not text.startswith('Figura ') and
                not text.startswith('Table ') and
                not text.startswith('Tabela ') and
                text[-1].isalpha() and
                ',' not in text and
                '  ' not in text
        ):
            return True
        # endif --

        return False
    # enddef --

    doc_lines = []
    for page_layout in pages:
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_lines = element.get_text().split("\n")

                # Remover rodapé
                if len(page_lines) == 2 and str(page_lines[0].strip()).isdigit():
                    continue
                # endif --

                if len(page_lines) == 2 and page_lines[1] == "":
                    page_lines[0] = page_lines[0].strip()

                    if _is_title(page_lines[0]):
                        # formata o título
                        page_lines[0] = f"# {page_lines[0]}"
                    # endif --
                # endif --

                doc_lines.extend(line.strip() for line in page_lines)
            # endif --
        # endfor --
    # endfor --

    if not doc_lines:
        # não conseguiu extrair nenhum conteúdo do documento
        raise Exception(f"*** Erro: falha ao extrair o conteúdo do PDF - '{filename}'")
    # endif --

    # remover itens de cabeçalho e roda-pé (que são textos duplicados)
    repeated_lines = []
    tested_lines = set()
    for item in doc_lines:
        if item == "":
            continue
        # endif --

        if item in tested_lines:
            repeated_lines.append(item)
        else:
            tested_lines.add(item)
        # endif --
    # endfor --
    tested_lines.clear()
    doc_lines = [item for item in doc_lines if item not in repeated_lines]

    # junta linhas de parágrafos quebrados
    i = 1
    q = len(doc_lines) - 1
    sep = [',', ';', ':', '-', '(', ')', ']', '[']

    def _same_paragraph(text: str, parag: int) -> bool:
        """Determine whether two adjacent lines belong to the same paragraph.

        Args:
            text (str): Símbolo analisado na borda da linha.
            parag (int): Posição relativa (1 para linha anterior, 2 para próxima).

        Returns:
            bool: `True` quando as linhas devem ser unidas; caso contrário `False`.
        """
        if parag == 1:
            # primeira linha - é número ou um separador
            return text.isdigit() or text in sep
        else:
            # segunda linha - é minúsculo ou dígito ou um separador
            return text.islower() or text.isdigit() or text in sep
        # endif --

    # enddef --

    while i < q:
        if doc_lines[i] == '':
            if doc_lines[i - 1] == '':
                # remove quebra de linhas duplicadas
                doc_lines.pop(i)
                i -= 1
                q -= 1
                continue
            # endif --

            elif doc_lines[i - 1] != '' and doc_lines[i + 1] != '':
                if _same_paragraph(doc_lines[i - 1][-1], 1) and _same_paragraph(doc_lines[i + 1][0], 2):
                    # junta linhas num mesmo parágrafo
                    if doc_lines[i - 1][-1] == '-':
                        # remove o hífen no final da linha
                        doc_lines[i - 1] = f"{doc_lines[i - 1][:-1]} {doc_lines[i + 1]}"
                    else:
                        doc_lines[i - 1] = f"{doc_lines[i - 1]} {doc_lines[i + 1]}"
                    # endif --

                    doc_lines.pop(i + 1)
                    doc_lines.pop(i)
                    q -= 2

                    if doc_lines[i - 1][0] == '#':
                        # título pode ser sido marcado incorretamente
                        if not _is_title(doc_lines[i - 1]):
                            doc_lines[i - 1] = doc_lines[i - 1][2:]
                        # endif --
                    # endif --

                    continue
                # endif --
            # endif --
        # endif --

        i += 1
    # endwhile --

    for i in range(len(doc_lines)):
        if doc_lines[i] == '':
            # adiciona as quebras de parágrafo
            doc_lines[i] = '\n\n'

        elif doc_lines[i][-1] != ' ':
            # adiciona espaço no fim das linhas remanescentes
            doc_lines[i] += ' '
        # endif --
    # endfor --

    # Save the markdown text
    with open(md_filename, "w", encoding="utf-8") as md_file:
        md_file.write("".join(doc_lines))

    return md_filename


def convert_markdown_to_pdf(md_path: str, img_dir: str, pdf_path: str=None) -> str:
    """Render a Markdown document into PDF format.

    Args:
        md_path (str): Caminho do arquivo Markdown de entrada.
        pdf_path (str): Caminho do arquivo PDF de saída.
        img_dir (str): Diretório utilizado para localizar imagens referenciadas.

    Returns:
        str: Caminho do arquivo PDF gerado.

    Raises:
        Exception: Quando ocorrer falha durante a conversão ou leitura do arquivo.
    """
    convert_markdown_to_html(md_path, img_dir)

    import pdfkit  # essa biblioteca requer a ferramenta de linha de comando 'wkhtmltopdf' do site https://wkhtmltopdf.org/

    html_filename = md_path[:-4] + '.html'
    pdf_filename = md_path[:-4] + '.pdf' if pdf_path is None else pdf_path

    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
    # endif --

    with open(html_filename, 'r', encoding='utf-8') as file:
        html_text = file.read()

    path_wkhtmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    options = {'enable-local-file-access': '', }
    configuration = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdfkit.from_string(html_text, pdf_filename, configuration=configuration, options=options)

    return pdf_filename
