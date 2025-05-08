import os
import re
import argparse


def read_file_strip_comments(filename, remove_comments):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not remove_comments:
        return ''.join(lines)

    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('%'):
            continue
        cleaned_line = re.sub(r'(?<!\\)%.*', '', line)
        cleaned_lines.append(cleaned_line)
    return ''.join(cleaned_lines)


def extract_inputs(tex):
    return re.findall(r'\\(?:input|subfile)\{([^}]+)\}', tex)


def extract_bibliographies(tex):
    bib_cmds = re.findall(r'\\(?:bibliography|addbibresource)\{([^}]+)\}', tex)
    bibs = []
    for group in bib_cmds:
        for item in group.split(','):
            item = item.strip()
            if not item.endswith('.bib'):
                item += '.bib'
            bibs.append(item)
    return bibs


def extract_usepackages(tex):
    return re.findall(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', tex)


def extract_external_docs(tex):
    return re.findall(r'\\myexternaldocument(?:\[[^\]]*\])?\{([^}]+)\}', tex)


def remove_balanced_command(text, command):
    pattern = re.compile(r'\\' + re.escape(command) + r'\s*\{', re.DOTALL)
    result = ''
    pos = 0
    while True:
        match = pattern.search(text, pos)
        if not match:
            result += text[pos:]
            break
        result += text[pos:match.start()]
        start = match.end()
        i = start
        depth = 1
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        if depth == 0:
            result += text[start:i - 1]  # keep inner content only
            pos = i
        else:
            result += text[match.start():]
            break
    return result


def remove_commands(tex, commands_to_remove):
    if not commands_to_remove:
        return tex

    for cmd in commands_to_remove:
        cmd = cmd.lstrip('\')
        if cmd == 'hl':
            tex = remove_balanced_command(tex, 'hl')
            continue
        tex = re.sub(r'\\' + re.escape(cmd) + r'(\{[^{}]*\})?', '', tex)
    return tex


def recursive_embed(filename, seen_files, remove_comments, is_main_file=False, commands_to_remove=None):
    if filename in seen_files:
        return ''
    seen_files.add(filename)

    if not os.path.exists(filename):
        return f"% Missing file: {filename}\n"

    base_dir = os.path.dirname(filename)
    tex = read_file_strip_comments(filename, remove_comments)

    if commands_to_remove:
        tex = remove_commands(tex, commands_to_remove)

    if not is_main_file:
        tex = re.sub(r'\\documentclass(?:\[[^\]]*\])?\{[^}]+\}', '', tex)
        tex = re.sub(r'\\begin\{document\}', '', tex)
        tex = re.sub(r'\\end\{document\}', '', tex)

    def replacer(match):
        sub_filename = match.group(1)
        if not sub_filename.endswith('.tex'):
            sub_filename += '.tex'
        sub_path = os.path.join(base_dir, sub_filename)
        return recursive_embed(sub_path, seen_files, remove_comments, is_main_file=False, commands_to_remove=commands_to_remove)

    tex = re.sub(r'\\(?:input|subfile)\{([^}]+)\}', replacer, tex)
    return tex


def create_filecontents_block(filename, content):
    return ("\\begin{filecontents*}[overwrite]{" + filename + "}\n" +
            content.rstrip() + "\n\n\\end{filecontents*}\n\n")


def submit_latex(input_file, output_file, remove_comments, include_sty, include_external, commands_to_remove=None):
    seen = set()
    main_content = recursive_embed(input_file, seen, remove_comments, is_main_file=True, commands_to_remove=commands_to_remove)

    bib_blocks = ""
    for bib in extract_bibliographies(main_content):
        if not os.path.exists(bib):
            raise FileNotFoundError(f"Error: Required bibliography file '{bib}' not found")
        content = read_file_strip_comments(bib, remove_comments)
        if commands_to_remove:
            content = remove_commands(content, commands_to_remove)
        bib_blocks += create_filecontents_block(bib, content)

    sty_blocks = ""
    if include_sty:
        for sty in extract_usepackages(main_content):
            for name in sty.split(','):
                name = name.strip()
                if not name.endswith('.sty'):
                    name += '.sty'
                if os.path.exists(name):
                    content = read_file_strip_comments(name, remove_comments)
                    if commands_to_remove:
                        content = remove_commands(content, commands_to_remove)
                    sty_blocks += create_filecontents_block(name, content)

    aux_blocks = ""
    if include_external:
        for aux_base in extract_external_docs(main_content):
            aux_file = aux_base + ".aux"
            if not os.path.exists(aux_file):
                raise FileNotFoundError(f"Error: Required external document file '{aux_file}' not found")
            content = read_file_strip_comments(aux_file, remove_comments)
            if commands_to_remove:
                content = remove_commands(content, commands_to_remove)
            aux_blocks += create_filecontents_block(aux_file, content)

    full_output = bib_blocks + sty_blocks + aux_blocks + main_content
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(full_output)

    print(f"Successfully created flattened LaTeX file: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flatten LaTeX document with dependencies.")
    parser.add_argument("input", help="Main LaTeX input file")
    parser.add_argument("-o", "--output", default="flattened.tex", help="Output file")
    parser.add_argument("-c", "--strip-comments", action="store_true", help="Remove comments and empty lines")
    parser.add_argument("-s", "--include-sty", action="store_true", help="Embed .sty files")
    parser.add_argument("-a", "--include-aux", action="store_true", help="Embed .aux files")
    parser.add_argument("-r", "--remove", nargs='+', help="Commands to remove (e.g., 'hl' 'textcolor{red}')")

    args = parser.parse_args()

    try:
        submit_latex(
            args.input,
            args.output,
            args.strip_comments,
            args.include_sty,
            args.include_aux,
            args.remove
        )
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        exit(1)
