LaTeX Flatten Paper
===

This tool prepares a paper source code to be published to any journal or repository. This includes the following features:

- flatten the LaTeX files such that all LaTeX code is contained in one .tex-file
- flatten the bibliography such that only the actually used references are contained as plain text in the .tex-file
- all privately used macros are expanded
- source code of figures created by TikZ are replaced by the resulting .pdf-file to not publish the source itself
- for each figure in the paper, a corresponding fig<xx>.pdf-file will be available with correct numbering of the files
- the result of this tool is a new directory including a .zip-file that (in an ideal world) can be directly submitted to any journal or repository.

author: Thorben Casper  
created in October 2016


## Installation

This tool is based on bash and has only been tested on Ubuntu. On Windows, it could be promising to use Git Bash for Windows or a Linux subsystem under Windows 10. Apart from the OS requirement, the following tools need to be pre-installed:
- latexpand
- de-macro (officially only tested on Unix systems)
- tikz-cd (a TikZ library)

## LaTeX Prerequisites

### Packages
- packages are loaded without using any additional path
- do not load more than one package for each \usepackage command
- all custom packages that are not present in a standard LaTeX installation must be present as .sty-files in the current directory or any of its sub-directories

### Figures
- all figures must be contained in sub-directories according to the input parameters 'figsDir' and 'figsDirAdditional', figures in the root directory of the paper are not supported
- applying tikzexternalize to the paper must be working. However, when flattening the paper, \usetikzlibrary{external} must be removed on beforehand
- different figures must have different names, not only different extensions
- there must only be one tikzpicture environment per (sub-)figure, use scope environment if necessary, see example01
- if standalone figures are used together with the standalone package, they must be included using the \includestandalone macro (see standalone package documentation) instead of \input or \include. This is due to a limitation of latexpand that does not recognize standalone input files. The filename of the standalone figure must be given without extension, e.g., 'example' instead of 'example.tex'. Additionally, the standalone package option 'mode=build', 'mode=buildmissing' or 'mode=buildnew' must be used
- if figures include references to anything in the rest of the LaTeX document, they must be included directly in the LaTeX document or by the \input command
- in one line, there must always only be one figure file that is included.

### Bibliography
- if using biblatex instead of bibtex, all bib setup lines in the preamble must be enclosed by a beginning line containing BEGIN BIBLIOGRAPHY SETUP and an ending line END BIBLIOGRAPHY SETUP, see example03. DO NOT use any other commands than \bibliographystyle, \bibliography and \printbibliography within \begin{document} and \end{document}.
- LaTeX package hyperref must be used to typeset links in bibliography correctly.
- For bibliography flattening, there should be no comment lines including the token '\bibliography' in the file


## Usage and Examples

Besides the help function of the 'flattenPaper' script, the best approach to understand flattenPaper is by providing a set of examples. These examples demonstrate the capabilities of flattenPaper, explain the usage, and serve as a testbench. In the following list of examples, a feature is only listed if it has not yet been covered by any of the preceding examples. To run any of the examples, execute the 'flatten' script in the individual directory of the corresponding example or simply use the 'runAllExamples' script in the 'examples' directory.

### Example 01

- documentclass elsarticle
- two custom macro (.sty) files with custom prefix 'my' and standard postfix 'private'
- option (non-functional) for private package 'my-macros.sty'
- acronyms using glossaries package
- remark block
- comment block
- subfiles using \input
- standard tikz figures using \input
- standalone tikz figures using \includestandalone
- tikz figures including nodes that contain \includegraphics
- using \includegraphics to load an eps file
- tikzpicture environments without using \input, \includestandalone or similar
- pgfplot using axis environment and \addplot
- figure in comment block
- subfigures using subcaptions package
- table using table and tabular environments
- algorithm environment
- using natbib (bibtex) to typeset bibliography
- figures are stored in multiple figure directories
- acknowledgment
- appendix

### Example 02

- documentclass article
- no \usepackage is used
- example how to solve the incompatibility of tikz-cd with tikzexternalize
- IEEE copyright notice is placed by option -i
- no figures at all, thus no separate figure directories
- using thebibliography-environment to typeset bibliography directly

### Example 03

- using biblatex to typeset bibliography
  warning: the use of biblatex leads to a different bibliography formatting in the flattened paper


## Acknowledgment

The author thanks Niklas Georg for testing and helpful discussions to improve this tool.
