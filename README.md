# 📄 LaTeX Submission Flattener

This Python script helps flatten a LaTeX project into a single `.tex` file, suitable for submission to journals, archives, or collaborators.

---

## ✅ Features

- Recursively processes `\input{}` and `\subfile{}` commands
- Embeds bibliography files (`.bib`) via `filecontents*`
- Optionally includes local style files (`.sty`) and auxiliary files (`.aux`)
- Preserves paragraph spacing and empty lines
- Can strip LaTeX comments and remove specified commands (e.g. `\hl{}`, `\textcolor{}`)

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
python3 submit_latex.py main.tex -o submission.tex
```

### 🔍 Full example with all options

```bash
python3 submit_latex.py main.tex -o submission.tex -c -s -a -r \hl \textcolor
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

---

## 🔁 Workflow Example

1. **Compile your full project first** — especially if you use external documents or bibliographies:

    ```bash
    pdflatex main.tex
    bibtex main.aux
    pdflatex main.tex
    pdflatex main.tex
    ```
    Note: If you are using biber instead of bibtex, use the command biber main (not main.aux).

2. **Flatten the LaTeX document**:

    ```bash
    python3 submit_latex.py main.tex -o submission.tex -csa
    ```

3. **Compile the submission version** to check:

    ```bash
    pdflatex submission.tex
    bibtex submission.tex
    pdflatex submission.tex
    pdflatex submission.tex
    ```
    Note: If you are using biber instead of bibtex, use the command biber main (not submission.aux).
---

## ⚠️ Important Notes

- 🔍 **Always compare the final PDF with your original version**. The output may differ depending on LaTeX settings or removed commands.
- 📂 `.aux` files are required for documents using `\myexternaldocument{}` (e.g., supplementary material cross-referencing).
- 🛠️ Complex projects may need **manual adjustments**.
- 🚫 This script **does not support** `\includeonly`.

---

📘 Good luck with your submission!
