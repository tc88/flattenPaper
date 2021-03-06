#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created in 10/2016 by Thorben Casper 
# edited by Thorben Casper
# flattens the bibliography of a .tex file such that thebibliography environment is used. Converts biblatex to bibtex if necessary. Then obtains bibliography from .bbl-file created by bibtex
#
# it is important to enclose all bib setup lines in the preamble into a beginning line containing BEGIN BIBLIOGRAPHY SETUP and an ending line END BIBLIOGRAPHY SETUP. The only supported commands between \begin{document} and \end{document} are \bibliographystyle, \bibliography and \printbibliography. DO NOT use any other commands here!

import os
import argparse
import subprocess
import re
import sys
import glob
import shutil

print "flattening bibliography ..."

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help="the .tex-file that shall be modified")
parser.add_argument("quiet", help="enables quiet output")
parser_args = parser.parse_args()
filename = parser_args.tex_file
quiet = int(parser_args.quiet)

# parses the .tex file to obtain name of bib file and the .tex-file's content without bibliography lines
f = open(filename+'.tex','r')
bibline = 0
bib_file = None
skipLines = 0
nrSkippedLines = 0
contents = []
biblatexDetected = False
for num, line in enumerate(f,1):
    if 'BEGIN BIBLIOGRAPHY SETUP' in line:
        skipLines = 1
        biblatexDetected = True
    if skipLines:
        nrSkippedLines += 1
    if not biblatexDetected or (not '\\printbibliography' in line and not '\\bibliography' in line and not '\\bibfont' in line and not skipLines):
        contents.append(line)
    if '\\bibliography' in line and line.strip()[0] != '%':
        nrSkippedLines += 1
        m = re.search('\\\\bibliography{(.+?)}',line)
        if m: 
            bib_file = m.group(1)
    if '\\addbibresource' in line and line.strip()[0] != '%':
        m = re.search('\\\\addbibresource{(.+?)}',line)
        if m: 
            bib_file = m.group(1)
    if '\\printbibliography' in line or '\\bibfont' in line:
        nrSkippedLines += 1
    if '\\end{document}' in line:
        bibline = num-nrSkippedLines-2
    if 'END BIBLIOGRAPHY SETUP' in line:
        skipLines = 0
f.close()

# only continue if a bib_file to be flattened has been found
if bib_file:
    # strip extension of bib_file if present
    bib_file = os.path.splitext(os.path.basename(bib_file))[0]

    # inserts the commands required by bibtex
    if biblatexDetected:
        contents.insert(bibline,'\\bibliographystyle{flatPaper}\n')
        contents.insert(bibline+1,'\\bibliography{'+bib_file+'}\n')

    # write modified contents to output file
    contents = "".join(contents)
    f = open(filename+'.tex','w')
    f.write(contents)
    f.close()

    # remove any .aux and .bbl files if existent
    path = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile('./build/'+filename+'.aux'):
        os.remove('./build/'+filename+'.aux')
    if os.path.isfile(filename+'.bbl'):
        os.remove(filename+'.bbl')

    # call pdflatex and bibtex to generate .bbl file
    FNULL = open(os.devnull,'w')
    if not quiet:
        subprocess.call(["pdflatex", "-shell-escape","--output-directory=build",filename])
        for file in glob.glob(r'./build/*.bib'):
            shutil.copy(file,'./')
        subprocess.call(["bibtex",'./build/'+filename])
    else:
        subprocess.call(["pdflatex", "-shell-escape","--output-directory=build",filename],stdout=FNULL)
        for file in glob.glob(r'./build/*.bib'):
            shutil.copy(file,'./')
        subprocess.call(["bibtex",'./build/'+filename],stdout=FNULL)
    os.rename('./build/'+filename+'.bbl',filename+'_bib.tex')

    # reads in .tex file's content without bib commands again and save index of line where to insert .bbl file
    f = open(filename+'.tex','r')
    contents = []
    skipLines = 0
    for num, line in enumerate(f,1):
        if not '\\bibliography' in line:
            contents.append(line)
        else:
            skipLines += 1
        if '\\end{document}' in line:
            bibline = num-skipLines-1
    f.close()

    # insert .bbl file to the contents
    contents.insert(bibline,'\\input{'+filename+'_bib}\n')
    contents.insert(bibline+1,'\n')
    contents = "".join(contents)

    # write modified contents to output file
    f = open(filename+'.tex','w')
    f.write(contents)
    f.close()

    # remove original .bib file that represents the full library, the required entries are now in filename_bib.tex
    os.remove(bib_file+'.bib')

    # replacing '_' with '\_' in second argument of '\href{}{}' command, since escaping is required (using a recursive approach with sed). For performance and/or compatibility, this could be implemented directly in Python.
    subprocess.call(["sed","-e",":loop","-e",r"s/\(\\href{.*}\)\({.*\)[^\]_\(.*}\)/\1\2\\_\3/g","-e","t loop","-i",filename+'_bib.tex'])

    # test run
    if not quiet:
        subprocess.call(["pdflatex","-shell-escape","--output-directory=build",filename])
    else:
        subprocess.call(["pdflatex","-shell-escape","--output-directory=build",filename],stdout=FNULL)
else:
    print("no bib file was detected. Thus, there was nothing to do.")

print("finished flattening bibliography.")
