author: Thorben Casper
created on: 2020/03/11

This is a list of the examples provided in this directory. Each example demonstrates certain latex features that 'flattenPaper' has to deal with. In this list, a feature is only listed if it has not yet been covered by any of the preceding examples. To run any of the examples, execute the 'flatten' script in the corresponding directory or simply use the 'runAllExamples' bash-script.

Example 01
----------

- documentclass elsarticle
- two custom macro (.sty) files with custom prefix 'my' and standard postfix 'private'
- option (non-functional) for private package 'my-macros.sty'
- standard tikz figures using \input
- standalone tikz figures using \includestandalone
- tikz figures including nodes that contain \includegraphics
- tikzpicture environments without using \input, \includestandalone or similar
- subfigures using subcaptions package
- bibliography using natbib (bibtex)
- table using table and tabular environments
- pgfplot using axis environment and \addplot
- subfiles using \input
- figures are stored in multiple figure directories
- documentclass article
- acknowledgment
- appendix
- algorithm
- acronyms using glossaries package
- remark block
- comment block
- figure in comment block

Example 02
----------

- using thebibliography-environment to typeset bibliography directly
- no figures at all, thus no separate figure directories
- no \usepackage is used
- IEEE copyright notice is placed by option -i
