README - Example for submit_latex.py usage
==========================================

This example demonstrates how to flatten a LaTeX project into a single file using the submit_latex.py script.

Folder structure:
-----------------
- Latex_Source_Files/
  Contains an example LaTeX project with:
  - `file1.tex`: the main LaTeX file
  - `file2.tex`: used via \myexternaldocument for cross-referencing
  - `included_content.tex`: included using \input
  - `subfile_content.tex`: included using \subfile
  - `references.bib`: bibliography database
  - Inline comments and environments for removal (\hl, \textcolor, comment environment, etc.)
  - Local .sty files (e.g., for MATLAB code with `mcode.sty`)

- Latex_Output_Files/
  This folder will contain all output files after compiling with:
    latexmk file1.tex

  In Overleaf, you can get the same output by clicking:
    “Logs and output files” → scroll to the bottom → “Other logs and files”

- Submission/
  The generated submit.tex file is a standalone LaTeX document that can be compiled independently to produce the submit.pdf file.

Steps to use submit_latex.py:
-----------------------------
1. Place `submit_latex.py` inside `Latex_Output_Files/` or the working directory.
2. Run the following command to generate a submission-ready LaTeX file:


   python3 submit_latex.py file1.tex -o submission.tex -csaB -r \hl \textcolor{red} -p \st -R center -P enumerate


    -c: strip comments

    -s: include .sty files

    -a: include .aux files (for cross-referencing)

    -B: include the .bbl file instead of the .bib and use biblatex-readbbl

    -r: remove specific commands (keep content)

    -p: purge (remove commands and their arguments)

    -R, -P: remove environments and purge their content

3. Compile the resulting submission.tex using:

    pdflatex -interaction=nonstopmode submission.tex
    pdflatex -interaction=nonstopmode submission.tex

4. Output:

    submission.tex: single LaTeX file ready for journal submission

    submission.pdf: the compiled version (if -g option is used)

    (No `biber` run needed with `-B` option, you can use this file also in Overleaf.)

NOTE:

Always verify that the final PDF (submission.pdf) is correct before submission!
