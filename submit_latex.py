import os
import re
import argparse
import subprocess
import urllib.request
import tempfile

def download_biblatex_readbbl():
    """Download the latest biblatex-readbbl.sty from CTAN"""
    url = "https://mirrors.ctan.org/macros/latex/contrib/biblatex-contrib/biblatex-readbbl/biblatex-readbbl.sty"
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            with urllib.request.urlopen(url) as response:
                tmp_file.write(response.read())
            return tmp_file.name
    except Exception as e:
        raise RuntimeError(f"Failed to download biblatex-readbbl.sty: {str(e)}")

def extract_bbl_file(tex):
    # Look for \bibliography or \addbibresource commands to guess the .bbl filename
    bib_matches = re.findall(r'\\(?:bibliography|addbibresource)\{([^}]+)\}', tex)
    if bib_matches:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        return f"{base_name}.bbl"
    return None

def read_file_strip_comments(filename, remove_comments):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not remove_comments:
        return content
    
    # Split into lines while preserving line endings
    lines = content.splitlines(keepends=True)
    
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('%'):
            # Skip full-line comments but preserve empty lines
            if line.strip() == '%':
                cleaned_lines.append('\n')  # preserve standalone % as empty line
            continue
        
        # Remove inline comments but preserve the rest of the line including empty lines
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


def find_balanced_braces(text, start):
    """Find the range of the balanced {...} starting at index `start` (which must be the '{')."""
    assert text[start] == '{', "Expected opening brace at start position"
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    return start, i  # inclusive start, exclusive end

def remove_command_instances(text, command, purge=True):
    """Remove all instances of a command. If `purge` is False, keep the content inside the braces."""
    pattern = re.compile(r'(\\?)' + re.escape(command) + r'\s*(?=\{)')
    pos = 0
    output = ''

    while True:
        match = pattern.search(text, pos)
        if not match:
            output += text[pos:]
            break

        output += text[pos:match.start()]
        brace_start = match.end()
        if brace_start >= len(text) or text[brace_start] != '{':
            pos = match.end()
            continue

        try:
            start, end = find_balanced_braces(text, brace_start)
            if purge:
                # Remove command and content
                pos = end
            else:
                # Keep content, remove command only
                output += text[start + 1:end - 1]
                pos = end
        except AssertionError:
            pos = brace_start + 1

    return output


def remove_environment_instances(text, env_name, purge=True):
    """Remove all instances of an environment. If `purge` is False, keep the content inside the environment."""
    begin_pattern = re.compile(r'\\begin\s*\{\s*' + re.escape(env_name) + r'\s*\}')
    end_pattern = re.compile(r'\\end\s*\{\s*' + re.escape(env_name) + r'\s*\}')
    
    pos = 0
    output = ''
    
    while True:
        begin_match = begin_pattern.search(text, pos)
        if not begin_match:
            output += text[pos:]
            break
            
        # Find matching \end{env_name}
        end_search_pos = begin_match.end()
        depth = 1
        end_match = None
        
        while True:
            next_begin = begin_pattern.search(text, end_search_pos)
            next_end = end_pattern.search(text, end_search_pos)
            
            if not next_end:
                # No matching end found, skip this begin
                break
                
            if next_begin and next_begin.start() < next_end.start():
                depth += 1
                end_search_pos = next_begin.end()
            else:
                depth -= 1
                end_search_pos = next_end.end()
                if depth == 0:
                    end_match = next_end
                    break
    
        if not end_match:
            # No matching end found, skip this begin
            output += text[pos:begin_match.end()]
            pos = begin_match.end()
            continue
            
        if purge:
            # Remove entire environment
            output += text[pos:begin_match.start()]
            pos = end_match.end()
        else:
            # Remove BOTH begin AND end tags, keep content
            output += text[pos:begin_match.start()]  # Keep text before begin
            output += text[begin_match.end():end_match.start()]  # Keep content
            pos = end_match.end()  # Skip end tag
            
    return output


def remove_commands(tex, remove_list=None, purge_list=None):
    if remove_list:
        for cmd in remove_list:
            cmd = cmd.lstrip('\\')
            tex = remove_command_instances(tex, cmd, purge=False)

    if purge_list:
        for cmd in purge_list:
            cmd = cmd.lstrip('\\')
            tex = remove_command_instances(tex, cmd, purge=True)

    return tex


def remove_environments(tex, remove_envs=None, purge_envs=None):
    if remove_envs:
        for env in remove_envs:
            tex = remove_environment_instances(tex, env, purge=False)

    if purge_envs:
        for env in purge_envs:
            tex = remove_environment_instances(tex, env, purge=True)

    return tex


def recursive_embed(filename, seen_files, remove_comments, is_main_file=False, 
                   remove_list=None, purge_list=None, remove_envs=None, purge_envs=None):
    if filename in seen_files:
        return ''
    seen_files.add(filename)

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Required input file '{filename}' not found")

    base_dir = os.path.dirname(filename)
    tex = read_file_strip_comments(filename, remove_comments)

    tex = remove_commands(tex, remove_list=remove_list, purge_list=purge_list)
    tex = remove_environments(tex, remove_envs=remove_envs, purge_envs=purge_envs)

    if not is_main_file:
        tex = re.sub(r'\\documentclass(?:\[[^\]]*\])?\{[^}]+\}', '', tex)
        tex = re.sub(r'\\begin\{document\}', '', tex)
        tex = re.sub(r'\\end\{document\}', '', tex)

    def replacer(match):
        sub_filename = match.group(1)
        if not sub_filename.endswith('.tex'):
            sub_filename += '.tex'
        sub_path = os.path.join(base_dir, sub_filename)
        return recursive_embed(sub_path, seen_files, remove_comments, is_main_file=False,
                             remove_list=remove_list, purge_list=purge_list,
                             remove_envs=remove_envs, purge_envs=purge_envs)

    tex = re.sub(r'\\(?:input|subfile)\{([^}]+)\}', replacer, tex)
    return tex


def create_filecontents_block(filename, content):
    return ("\\begin{filecontents*}[overwrite]{" + filename + "}\n" +
            content.rstrip() + "\n\n\\end{filecontents*}\n\n")


def submit_latex(input_file, output_file, remove_comments, include_sty, include_external,
                include_bbl, use_readbbl, remove_list=None, purge_list=None,
                remove_envs=None, purge_envs=None):
    # If remove_comments is True, add 'comment' to purge_envs
    if remove_comments:
        purge_envs = list(purge_envs) if purge_envs else []
        if 'comment' not in purge_envs:
            purge_envs.append('comment')
    
    seen = set()
    try:
        main_content = recursive_embed(
            input_file,
            seen,
            remove_comments,
            is_main_file=True,
            remove_list=remove_list,
            purge_list=purge_list,
            remove_envs=remove_envs,
            purge_envs=purge_envs
        )
    except FileNotFoundError as e:
        print(str(e))
        exit(1)

    # Download biblatex-readbbl.sty if -B is used
    readbbl_block = ""
    if use_readbbl:
        try:
            # Download latest version from CTAN
            url = "https://mirrors.ctan.org/macros/latex/contrib/biblatex-contrib/biblatex-readbbl/latex/biblatex-readbbl.sty"
            with urllib.request.urlopen(url) as response:
                readbbl_content = response.read().decode('utf-8')
            readbbl_block = create_filecontents_block("biblatex-readbbl.sty", readbbl_content)
            
            # Replace \addbibresource with biblatex-readbbl package
            output_name = os.path.splitext(os.path.basename(output_file))[0]
            main_content = re.sub(
                r'\\addbibresource\{[^}]+\}',
                r'\\usepackage[bblfile=' + output_name + r']{biblatex-readbbl}',
                main_content
            )
        except Exception as e:
            print(f"Warning: Could not download biblatex-readbbl.sty ({str(e)})")
            use_readbbl = False

    bib_blocks = ""
    # Only process .bib files if neither -b nor -B is specified
    if not (include_bbl or use_readbbl):
        for bib in extract_bibliographies(main_content):
            if not os.path.exists(bib):
                raise FileNotFoundError(f"Required bibliography file '{bib}' not found")
            content = read_file_strip_comments(bib, remove_comments)
            content = remove_commands(content, remove_list=remove_list, purge_list=purge_list)
            content = remove_environments(content, remove_envs=remove_envs, purge_envs=purge_envs)
            bib_blocks += create_filecontents_block(bib, content)

    # Handle .bbl file inclusion (for both -b and -B)
    bbl_block = ""
    if include_bbl or use_readbbl:
        input_base = os.path.splitext(os.path.basename(input_file))[0]
        bbl_file = f"{input_base}.bbl"
        
        if not os.path.exists(bbl_file):
            raise FileNotFoundError(
                f"Required .bbl file '{bbl_file}' not found. "
                f"Please compile with biber/bibtex first to generate it."
            )
            
        content = read_file_strip_comments(bbl_file, remove_comments=False)
        output_base = os.path.splitext(os.path.basename(output_file))[0]
        embedded_bbl_name = f"{output_base}.bbl"
        bbl_block = create_filecontents_block(embedded_bbl_name, content)

    sty_blocks = ""
    if include_sty:
        for sty in extract_usepackages(main_content):
            for name in sty.split(','):
                name = name.strip()
                if not name.endswith('.sty'):
                    name += '.sty'
                if os.path.exists(name):
                    content = read_file_strip_comments(name, remove_comments)
                    content = remove_commands(content, remove_list=remove_list, purge_list=purge_list)
                    content = remove_environments(content, remove_envs=remove_envs, purge_envs=purge_envs)
                    sty_blocks += create_filecontents_block(name, content)

    aux_blocks = ""
    if include_external:
        for aux_base in extract_external_docs(main_content):
            aux_file = aux_base + ".aux"
            if not os.path.exists(aux_file):
                raise FileNotFoundError(f"Required external document file '{aux_file}' not found")
            content = read_file_strip_comments(aux_file, remove_comments)
            content = remove_commands(content, remove_list=remove_list, purge_list=purge_list)
            content = remove_environments(content, remove_envs=remove_envs, purge_envs=purge_envs)
            aux_blocks += create_filecontents_block(aux_file, content)

    full_output = readbbl_block + bib_blocks + bbl_block + sty_blocks + aux_blocks + main_content
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(full_output)

    print(f"Successfully created flattened LaTeX file: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flatten LaTeX document with dependencies.")
    parser.add_argument("input", help="Main LaTeX input file")
    parser.add_argument("-o", "--output", default="flattened.tex", help="Output file")
    parser.add_argument("-c", "--strip-comments", action="store_true", 
                       help="Remove comments and empty lines, and completely purge comment environments")
    parser.add_argument("-s", "--include-sty", action="store_true", help="Embed .sty files")
    parser.add_argument("-a", "--include-aux", action="store_true", help="Embed .aux files")
    parser.add_argument("-b", "--include-bbl", action="store_true", help="Embed formatted .bbl bibliography")
    parser.add_argument("-B", "--use-readbbl", action="store_true", help="Download and include latest biblatex-readbbl.sty and use it")
    parser.add_argument("-r", "--remove", nargs='+', help="Commands to remove")
    parser.add_argument("-p", "--purge", nargs='+', help="Commands to completely purge")
    parser.add_argument("-R", "--remove-env", nargs='+', help="Environments to remove")
    parser.add_argument("-P", "--purge-env", nargs='+', help="Environments to completely purge")
    parser.add_argument("-g", "--generate-pdf", action="store_true", help="Generate PDF after flattening")

    args = parser.parse_args()

    try:
        submit_latex(
            args.input,
            args.output,
            args.strip_comments,
            args.include_sty,
            args.include_aux,
            args.include_bbl,
            args.use_readbbl,
            args.remove,
            args.purge,
            args.remove_env,
            args.purge_env
        )

        if args.generate_pdf:
            print("\nGenerating PDF...")
            base_name = os.path.splitext(args.output)[0]
    
            try:
                # When -b or -B is used, we already have the .bbl file included
                if args.include_bbl or args.use_readbbl:
                    # Two pdflatex runs are sufficient
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', args.output], check=False)
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', args.output], check=False)
                else:
                    # Normal compilation sequence
                    with open(args.output, 'r', encoding='utf-8') as f:
                        content = f.read()
                        uses_biblatex = 'biblatex' in content
        
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', args.output], check=False)
        
                    if uses_biblatex:
                        bib_result = subprocess.run(['biber', base_name], capture_output=True, text=True)
                        if bib_result.returncode != 0:
                            print(f"Biber warning: {bib_result.stderr}")
                    else:
                        bib_result = subprocess.run(['bibtex', base_name], capture_output=True, text=True)
                        if bib_result.returncode != 0:
                            print(f"BibTeX warning: {bib_result.stderr}")
        
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', args.output], check=False)
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', args.output], check=False)
        
                if os.path.exists(f"{base_name}.pdf"):
                    print(f"\nPDF successfully generated: {base_name}.pdf")
                else:
                    raise RuntimeError("PDF file was not created despite compilation attempts")
    
            except Exception as e:
                print(f"\nWarning: PDF generation completed with minor issues: {str(e)}")
                if os.path.exists(f"{base_name}.pdf"):
                    print("...but a PDF file was still generated (check for warnings)")

    except FileNotFoundError as e:
        print(str(e))
        exit(1)
