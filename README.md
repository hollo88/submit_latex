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
| `-r CMD ...` | Remove specified LaTeX commands (but keep their content)   |
| `-p CMD ...` | Remove specified LaTeX commands (delete their content)     |

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
   
    Note 2: You can also download your Overleaf project, but you’ll need to download the .aux file (e.g., supplementary.aux) if you have cross-references — Overleaf → “Logs and output files” → “Other logs and files” (at the bottom of the page).


3. **Flatten the LaTeX document**:

    ```bash
    python submit_latex.py main.tex -o submission.tex -csa -r \hl -p \sout
    ```
    Note: It will create a sinle tex file ("submission.tex"), removing the comments, including local .sty files and cross referencing data, removing the highlighting command (`\hl{}`) and deleting the crossed text (inside `\sout{}`).

4. **Compile the submission version** to check:

    ```bash
    pdflatex submission.tex
    bibtex submission.tex
    pdflatex submission.tex
    pdflatex submission.tex
    ```
    Note 1: If you are using biber instead of bibtex, use the command "biber main".

    Note 2: If you're using Overleaf, you can upload "submission.tex" to your project and compile it directly.
---

## ⚠️ Important Notes

- 🔍 **Always compare the final PDF with your original version**. The output may differ depending on LaTeX settings or removed commands.
- 📂 `.aux` files are required for documents using `\myexternaldocument{}` (e.g., supplementary material cross-referencing).
- 🛠️ Complex projects may need **manual adjustments**.
- 🚫 This script **does not support** `\includeonly`.

---

📘 Good luck with your submission!
