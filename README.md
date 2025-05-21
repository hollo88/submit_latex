# 📄 LaTeX Submission Flattener

This Python script helps flatten a LaTeX project into a single `.tex` file, suitable for submission to journals, archives, or collaborators.

---

## ✅ Features

- Recursively processes `\input{}` and `\subfile{}` commands
- Embeds bibliography files (`.bib`) via `filecontents*`
- Optionally includes local style files (`.sty`)
- Optionally includes auxiliary files (`.aux`) for cross references
- Can strip LaTeX comments
- Can remove specified commands (e.g. `\hl{}`, `\textcolor{}`)
- Can remove specified commands with their argument block (e.g. `\sout{}`)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/submit_latex.git
cd submit_latex
```

---

## 🚀 Usage

### 🔧 Basic command

```bash
python submit_latex.py main.tex -o submission.tex
```

### 🔍 Full example with all options

```bash
python submit_latex.py main.tex -o submission.tex -c -s -a -r \hl \textcolor -p \sout
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
| `-g`	       | Generate PDF after flattening (requires pdflatex/biber)    |

---

## 🔁 Workflow Example

1. **Compile your full project first** — especially if you use external documents or bibliographies:

    ```bash
    pdflatex main.tex
    bibtex main.aux
    pdflatex main.tex
    pdflatex main.tex
    ```
    Note 1: If you are using biber instead of bibtex, use the command "biber main".
   
    Note 2: You can also download your Overleaf project, but you’ll need to download the `.aux` file (e.g., supplementary.aux) if you have cross-references or the `.bbl` file (e.g., main.bbl, with the -b and -B options) — Overleaf → “Logs and output files” → “Other logs and files” (at the bottom of the page).


3. **Flatten the LaTeX document**:

    ```bash
    python submit_latex.py main.tex -o submission.tex -csab -r \hl -p \sout
    ```
    Note1: It will create a single tex file ("submission.tex"), removing the comments, including local .sty files and cross referencing data, removing the highlighting command (`\hl{}`) and deleting the crossed text (inside `\sout{}`).

   Note2: If latex is installed, with the -g option it will generate "submission.pdf", by running the commands from the next step.

   Note 3: Using the -b option includes the precompiled "main.bbl" file instead of relying on a ".bib" file for bibliography generation. This is particularly useful when the journal’s submission system supports only pdflatex run and does not execute `biber` or `bibtex`.

   Note 4: The -B option also includes the `.bbl` file and uses the [`biblatex-readbbl`](https://ctan.org/pkg/biblatex-readbbl?lang=en) package. This is particularly useful for journals that do not support `biber`, as it allows you to bypass the need for a `.bib` file and use a precompiled `.bbl` instead.

5. **Compile the submission version** to check:

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

## ⚠️ Important Notes

- 🔍 **Always compare the final PDF with your original version**. The output may differ depending on LaTeX settings or removed commands.
- 📂 `.aux` files are required for documents using `\myexternaldocument{}` (e.g., supplementary material cross-referencing).
- 📂 `.bbl` files are required for bibliography with the -b and -B options.
- 🛠️ If you have `.bbl` file included, **do not change the name** of the file.
- 🚫 This script **does not support** `\includeonly`.

---

📘 Good luck with your submission!
