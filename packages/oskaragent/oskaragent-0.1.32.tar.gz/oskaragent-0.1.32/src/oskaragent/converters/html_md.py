from __future__ import annotations

import locale
import os
import re
from typing import Tuple, List

from bs4 import BeautifulSoup
from markdown2 import markdown

from .helpers import create_randon_filename

# Conjunto das linguagens reconhecidas pelos blocos de código gerados.
SUPPORTED_LANGUAGES = [
    "1c", "abnf", "accesslog", "actionscript", "ada", "angelscript", "apache", "applescript",
    "arcade", "arduino", "armasm", "xml", "asciidoc", "aspectj", "autohotkey", "autoit", "avrasm",
    "awk", "axapta", "bash", "basic", "bnf", "brainfuck", "c", "cal", "capnproto", "ceylon",
    "clean", "clojure", "clojure-repl", "cmake", "coffeescript", "coq", "cos", "cpp", "crmsh",
    "crystal", "csharp", "csp", "css", "d", "dart", "delphi", "diff", "django", "dns", "dockerfile",
    "dos", "dsconfig", "dts", "dust", "ebnf", "elixir", "elm", "ruby", "erb", "erlang-repl",
    "erlang", "excel", "fix", "flix", "fortran", "fsharp", "gams", "gauss", "gcode", "gherkin",
    "glsl", "gml", "go", "golo", "gradle", "graphql", "groovy", "haml", "handlebars", "haskell",
    "haxe", "hsp", "http", "hy", "inform7", "ini", "irpf90", "isbl", "java", "javascript",
    "jboss-cli", "json", "julia", "julia-repl", "kotlin", "lasso", "latex", "ldif", "leaf", "less",
    "lisp", "livecodeserver", "livescript", "llvm", "lsl", "lua", "makefile", "mathematica",
    "matlab", "maxima", "mel", "mercury", "mipsasm", "mizar", "perl", "mojolicious", "monkey",
    "moonscript", "n1ql", "nestedtext", "nginx", "nim", "nix", "node-repl", "nsis", "objectivec",
    "ocaml", "openscad", "oxygene", "parser3", "pf", "pgsql", "php", "php-template", "plaintext",
    "pony", "powershell", "processing", "profile", "prolog", "properties", "protobuf", "puppet",
    "purebasic", "python", "python-repl", "q", "qml", "r", "reasonml", "rib", "roboconf", "routeros",
    "rsl", "ruleslanguage", "rust", "sas", "scala", "scheme", "scilab", "scss", "shell", "smali",
    "smalltalk", "sml", "sqf", "sql", "stan", "stata", "step21", "stylus", "subunit", "swift",
    "taggerscript", "yaml", "tap", "tcl", "thrift", "tp", "twig", "typescript", "vala", "vbnet",
    "vbscript", "vbscript-html", "verilog", "vhdl", "vim", "wasm", "wren", "x86asm", "xl", "xquery",
    "zephir", "html", "csv",
]


def convert_markdown_to_html(md_path: str, img_dir: str | None = None, insert_header: bool = True) -> str:
    """Generate an HTML file from a Markdown source.

    Args:
        md_path (str): Caminho do arquivo Markdown de origem.
        img_dir (str): Diretório usado para resolver paths de imagens relativas.
        insert_header (bool, optional): Indica se deve incluir um cabeçalho HTML padrão. Defaults to True.

    Returns:
        str: Caminho do arquivo HTML criado.

    Raises:
        Exception: Quando o arquivo especificado não pode ser localizado ou lido.
    """
    _, filename = os.path.split(md_path)

    if not os.path.exists(md_path) or not os.path.isfile(md_path):
        raise Exception(f"*** Erro: o arquivo '{filename}'não existe!")
    # endif --

    html_filename = md_path[:-3] + '.html'

    if os.path.exists(html_filename):
        os.remove(html_filename)
    # endif --

    with open(md_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    html_text, _ = convert_markdown_to_html_block(markdown_text, flag_insert_copy_to_clipboard_command=False)

    if insert_header:
        html_text = f"""
<html lang="en" data-bs-theme="auto">
    <head>
        <meta charset="utf-8">
        <meta name="author" content="AiSteg">
    </head>

    <body>
    {html_text}
    </body>
</html>"""
    # endif --

    if img_dir:
        html_text = html_text.replace('src="', f'src="{img_dir}/')

    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(html_text)

    return html_filename


def convert_markdown_to_html_block(text: str, flag_insert_copy_to_clipboard_command: bool = True) -> Tuple[str, List[str]]:
    """Convert Markdown text to HTML with optional copy-to-clipboard controls.

    Args:
        text (str): Conteúdo em Markdown que será convertido.
        flag_insert_copy_to_clipboard_command (bool, optional): Indica se deve incluir botões de copiar. Defaults to True.

    Returns:
        tuple[str, list]: Conteúdo HTML gerado e lista de linguagens detectadas em blocos de código.
    """

    def _gen_start_tag(_tipo: str, _html_id: str) -> str:
        """Create the HTML snippet for copy-to-clipboard controls."""
        if not flag_insert_copy_to_clipboard_command:
            return ""
        # endif --

        _func = "copyToClipboard"

        return f'''
[StartCopyToClipboard]<div class="d-flex justify-content-between bg text-white">
<div class="p-2 bg">{_tipo}</div>
<div class="p-2 bg"></div>
<div class="p-2 bg">
    <a onclick="{_func}('{_html_id}')" style="cursor: pointer;" class="text-decoration-none text-white" data-bs-toggle="tooltip" data-bs-placement="right" title="Copia o bloco para área de transferência">
        <i class="bi bi-copy"></i>
        <span class="ms-1">Copiar</span>
    </a>
</div>
</div>[EndCopyToClipboard]'''

    def _get_final_text(_text: str, _tipo: str) -> str:
        """Wrap fenced code blocks with proper HTML markup."""
        if f"\n```{_tipo}" not in _text and not _text.startswith(f"```{_tipo}"):
            return _text
        # endif --

        if _tipo not in ['plantuml', 'mermaid'] and (_tipo == '' or _tipo not in SUPPORTED_LANGUAGES):
            _class = 'code-block'
        else:
            _class = _tipo
        # endif --

        if flag_insert_copy_to_clipboard_command:
            _html_id = create_randon_filename(prefix=_tipo + "-")
            _start_tag = _gen_start_tag(_tipo, _html_id)

            _padrao = re.compile(f"```{_tipo}" + r'(.*?)```', re.DOTALL)
            _match = _padrao.findall(_text)
            _bloco = f'<div id="{_html_id}" style="display: none;">{_match[0]}</div>\n'

            _text = _text.replace(f"```{_tipo}", _start_tag + f'<pre class="{_class}">', 1)
            _pos = _text.find(f'<pre class="{_class}">')
            _text = _text[:_pos] + _text[_pos:].replace("```", f"</pre>{_bloco}", 1)

        else:
            _text = _text.replace(f"```{_tipo}", f'<pre class="{_class}">', 1)
            _pos = _text.find(f'<pre class="{_class}">')
            _text = _text[:_pos] + _text[_pos:].replace("```", "</pre>", 1)
        # endif --

        return _text

    linhas = text.split('\n')
    q = len(linhas)
    for i in range(q):
        if i == 0:
            continue
        # endif --

        lin = linhas[i]
        if lin and lin[0] in ['-', '*']:
            if len(linhas[i - 1]) > 0 and linhas[i - 1][0] not in ['-', '*'] and linhas[i - 1][0:1] != '\n':
                linhas[i] = '\n' + linhas[i]
            # endif --

            if i + 1 < q and len(linhas[i + 1]) > 0 and linhas[i + 1][0] not in ['-', '*'] and linhas[i + 1][0:1] != '\n':
                linhas[i] = linhas[i] + '\n'
            # endif --
        # endif --
    # endfor --

    text = "\n".join(linhas)

    languages: list[str] = []

    if "```" in text:
        final_text = text.replace("```\n@startuml", "```plantuml\n@startuml")

        padrao = re.compile(r'```markdown(.*?)```', re.DOTALL)
        blocos = padrao.findall(final_text)

        for bloco in blocos:
            final_text = final_text.replace(f"```markdown{bloco}```", bloco, 1)
        # endfor --

        while True:
            if "```" not in final_text:
                break
            # endif --

            language = re.search(r'```(\w+)', final_text)
            language = language.group(1).lower() if language else ''

            if language == "mermaid":
                final_text = _get_final_text(final_text, 'mermaid')

            elif language == "plantuml":
                final_text = _get_final_text(final_text, 'plantuml')

            elif language == "csv":
                continue

            else:
                anchor = language if language else ''
                language = language if language else 'plaintext'

                if language not in SUPPORTED_LANGUAGES and language not in ['plantuml', 'mermaid']:
                    language = 'plaintext'
                # endif --

                html_id = create_randon_filename(prefix=language + "-")
                start_tag = _gen_start_tag(language, html_id)

                final_text = final_text.replace(
                    f"```{anchor}",
                    start_tag + f'<pre><code id="{html_id}" class="language-{language}">',
                    1
                )
                pos = final_text.find(f'<pre><code id="{html_id}" class="language-{language}">')
                final_text = final_text[:pos] + final_text[pos:].replace("```", "</code></pre>", 1)

                languages.append(language)
            # endif --
        # endwhile --.

    else:
        final_text = text.replace("<", "&lt;").replace(">", "&gt;")
    # endif --

    final_text = final_text.replace("<pre", "[pre").replace("</pre>", "[/pre]")
    padrao = re.compile(r'\[pre(.*?)\[/pre]', re.DOTALL)

    snippets = list(padrao.findall(final_text))
    for count, bloco in enumerate(snippets):
        final_text = final_text.replace(bloco, f"]BLOCO-{count}-", 1)
    # endfor --

    padrao = re.compile(r'\[StartCopyToClipboard](.*?)\[EndCopyToClipboard]', re.DOTALL)
    snippets_copy_to_clipboard = list(padrao.findall(final_text))
    for count, bloco in enumerate(snippets_copy_to_clipboard):
        final_text = final_text.replace(bloco, f"COPY-{count}-", 1)
    # endfor --

    final_text = final_text.replace("\r\n", "\n")
    html_code = markdown(
        final_text,
        extras={
            "tables": None,
            "code-friendly": None,
            'breaks': {
                'on_newline': True,
                'on_backslash': True
            }
        }
    )

    if '<table>' in html_code:
        soup = BeautifulSoup(html_code, 'html.parser')

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        table_elements = soup.find_all('table')
        for table in table_elements:
            table['style'] = 'font-size: smaller; border-collapse: collapse; border-radius: 8px; overflow: hidden;'

            th_elements = soup.find_all('th')
            for th in th_elements:
                th['style'] = 'background-color: #D3D3D3; border: 1px solid #F5F5F5;'
            # endfor --

            number_pattern = re.compile(r'^-?\\d+(\\.\\d+)?$')
            tr_elements = soup.find_all('tr')
            for i, tr in enumerate(tr_elements):
                td_elements = tr.find_all('td')
                if i % 2 == 0:
                    for td in td_elements:
                        td['style'] = td.get('style', '') + 'background-color: #F5F5F5; border: 1px solid #D3D3D3;'
                    # endfor --
                else:
                    for td in td_elements:
                        td['style'] = td.get('style', '') + 'background-color: #FFFFFF; border: 1px solid #D3D3D3;'
                    # endfor --
                # endif --

                for td in td_elements:
                    content = td.get_text(strip=True)

                    if number_pattern.match(content):
                        flag_negative = False

                        try:
                            number = float(content)

                            if number.is_integer():
                                formatted_content = locale.format_string("%d", number, grouping=True)
                            else:
                                formatted_content = locale.format_string("%.4f", number, grouping=True)

                            if number < 0:
                                flag_negative = True
                            # endif --

                        except ValueError:
                            formatted_content = content

                        td.string = formatted_content + "$#@"
                        td['style'] = td.get('style', '') + 'text-align: right;'

                        if flag_negative:
                            td['style'] += 'color: red;'
                        # endif --

                    # endif --
                # endfor --
            # endfor --
        # endfor --

        html_code = str(soup)
        html_code = html_code.replace("$#@", "")
    # endif --

    if snippets_copy_to_clipboard:
        html_code = html_code.replace("<p>[StartCopyToClipboard]", "[StartCopyToClipboard]")

        for count, bloco in enumerate(snippets_copy_to_clipboard):
            html_code = html_code.replace(f"[StartCopyToClipboard]COPY-{count}-[EndCopyToClipboard]", bloco, 1)
        # endfor --
    # endif --

    if snippets:
        html_code = html_code.replace("[/pre]</p>", "[/pre]")

        for count, bloco in enumerate(snippets):
            if 'class="language-html">' in bloco:
                padrao = re.compile(r'class="language-html">(.*?)</code>', re.DOTALL)
                match = padrao.findall(bloco)

                if match:
                    for bloco_original in match:
                        bloco_revisado = bloco_original.replace("<", "&lt;").replace(">", "&gt;")
                        bloco = bloco.replace(bloco_original, bloco_revisado)
                    # endfor --
                # endif --
            # endif --

            html_code = html_code.replace(f"]BLOCO-{count}-", bloco, 1)
        # endfor --

        html_code = html_code.replace("[pre", "<pre").replace("[/pre]", "</pre>")
    # endif --

    languages = list(set(languages))

    return html_code, languages
