# 📄 LaTeX Submission Flattener

This Python script helps flatten a LaTeX project into a single `.tex` file, suitable for submission to journals, archives, or collaborators.

---

## 🎯 Why?

Because sometimes journals just want *one single file*. And if your project looks like a spaghetti bowl of `\input`, `\subfile`, `\addbibresource`, and `\usepackage`, this tool will untangle it for you!

---

## ✅ Features

- Recursively processes `\input{}` and `\subfile{}` commands to inline external content
- Embeds bibliography files (`.bib`) using `filecontents*`, allowing single-file compilation
- Supports inclusion of local style files (`.sty`) and auxiliary files (`.aux`) for cross-references
- Allows replacing `.bib` files with precompiled `.bbl` files if the bibliography is not processed during submission
- Optionally uses [`biblatex-readbbl`](https://ctan.org/pkg/biblatex-readbbl) to include `.bbl` files when `biber` is unavailable
- Supports stripping LaTeX comments, including `\begin{comment}...\end{comment}` blocks
- Can remove specified LaTeX commands (e.g., `\hl{}`, `\textcolor{}`) and environments
- Can completely remove specified commands or environments **along with** their content (e.g., `\sout{}` or custom environments)
- Can compile the resulting file using LaTeX to generate the final `.pdf` output

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/submit_latex.git
cd submit_latex
```

---

## 🚀 Usage

Just complie your document and run the script:

### 🔧 Basic command

```bash
python submit_latex.py main.tex -o submission.tex
```

### 🔍 Extended example

```bash
python submit_latex.py main.tex -o submission.tex -c -s -a -B -r \hl \textcolor -p \sout -g
```

---

## ⚙️ Command Line Options

| Option       | Description                                               |
|--------------|-----------------------------------------------------------|
| `-o FILE`    | Output filename (default: `flattened.tex`)                |
| `-c`         | Remove LaTeX comments                                      |
| `-s`         | Include local `.sty` files used via `\usepackage{}`        |
| `-a`         | Include `.aux` files used for cross-referencing            |
| `-b`         | Include `.bbl` file instead of the .bib file for references|
| `-B`         | Include `.bbl` file and replace \addbibresource with biblatex-readbbl package|
| `-r CMD ...` | Remove specified LaTeX commands (but keep their content)   |
| `-p CMD ...` | Remove specified LaTeX commands (delete their content)     |
| `-R ENV ...` | Remove specified LaTeX environments (but keep their content)   |
| `-P ENV ...` | Remove specified LaTeX environments (delete their content)     |
| `-g`	       | Generate PDF after flattening (requires pdflatex/biber)    |

 **Note:**  
> When using the `-b` or `-B` options, the script still embeds the original `.bib` files.  
> Although these files are not required for compilation when a `.bbl` file is included, many journals
> explicitly request the `.bib` sources as part of the submission. For this reason, they are always
> included by default.


---

## 🔁 Workflow Example

1. **Compile your full project first** — especially if you use external documents or bibliographies:

    ```bash
    pdflatex main.tex
    bibtex main.aux
    pdflatex main.texlatexmk
    pdflatex main.tex
    ```
    Note 1: If you are using `biber` instead of `bibtex`, compile your bibliography with `biber main` (or use `latexmk`, which handles this automatically). Make sure to use the same `biber` version consistently—mixing versions can cause subtle incompatibilities. For example, Overleaf may use a different `biber` version than your local machine. To avoid issues, generate all bibliography-related files on the same system whenever possible.
   
    Note 2: You can also download your Overleaf project, but you’ll need to download the `.aux` file (e.g., supplementary.aux) if you have cross-references or the `.bbl` file (e.g., main.bbl, with the -b and -B options) — Overleaf → “Logs and output files” → “Other logs and files” (at the bottom of the page).


2. **Flatten the LaTeX document**:

    ```bash
    python submit_latex.py main.tex -o submission.tex -csab -r \hl -p \sout
    ```
    Note1: It will create a single tex file ("submission.tex"), removing the comments, including local .sty files and cross referencing data, removing the highlighting command (`\hl{}`) and deleting the crossed text (inside `\sout{}`).

   Note2: If latex is installed, with the -g option it will generate "submission.pdf", by running the commands from the next step.

   Note 3: Using the -b option includes the precompiled "main.bbl" file instead of relying on a ".bib" file for bibliography generation. This is particularly useful when the journal’s submission system supports only pdflatex run and does not execute `biber` or `bibtex`.

   Note 4: The -B option also includes the `.bbl` file and uses the [`biblatex-readbbl`](https://ctan.org/pkg/biblatex-readbbl?lang=en) package. This is particularly useful for journals that do not support `biber`, as it allows you to bypass the need for a `.bib` file and use a precompiled `.bbl` instead. We automatically download `biblatex-readbbl.sty`, embed it in the `.tex` file using the `filecontents` environment, and generate it during compilation. This allows the document to compile even if the journal or platform does not support installing additional LaTeX packages.

3. **Compile the submission version** to check:

    ```bash
    pdflatex submission.tex
    bibtex submission.tex
    pdflatex submission.tex
    pdflatex submission.tex
    ```
    Note 1: If you are using biber instead of bibtex, use the command `biber submission`.

    Note 2: If you're using Overleaf, you can upload "submission.tex" to your project and compile it directly.

    Note3: If the -b and -B option is used, compiling with two `pdflatex submission.tex` is sufficient. Do not run `bibtex` or `biber`, as the bibliography is already included via the `.bbl` file.

---

📂 Example Files Folder Overview

    Latex_Source_Files/ – Contains example project using cross-references, .bib, and commands to clean

    Latex_Output_Files/ – The output files after compilation

    Submission/ – The final submission.tex and submission.pdf ready to upload

---

## ⚠️ Important Notes

- 🔍 **Always compare the final PDF with your original version**. The output may differ depending on LaTeX settings or removed commands.
- 📂 `.aux` files are required for documents using `\myexternaldocument{}` (e.g., supplementary material cross-referencing).
- 📂 `.bbl` files are required for bibliography with the -b and -B options.
- 🛠️ If you have `.bbl` file included, **do not change the name** of the file.
- 🚫 This script **does not support** `\includeonly`.

---

🙏 Pay With a Citation

If this script saves your sanity, please "pay" with a citation from one of my less cited works — I need those sweet academic karma points to survive. 😅
[Google Scholar](https://scholar.google.com/citations?user=Vk3q974AAAAJ&hl=hu)

---

📘 Good luck with your submission!
