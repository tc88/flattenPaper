#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created in 10/2016 by Thorben Casper 
# edited by Thorben Casper
# includes copyright notice into a given .tex file.

import argparse

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help="the .tex-file that shall be modified")
parser_args = parser.parse_args()
filename = parser_args.tex_file

# find line of last usepackage use in main .tex file
contents = []
idxLastUsepackage = 0  
f = open(filename,'r')
for num, line in enumerate(f,1):
    contents.append(line)
    if '\\usepackage' in line:
        idxLastUsepackage = num
f.close()

copyrightNotice='\\AddToShipoutPicture*{\\footnotesize\\sffamily\\raisebox{1cm}{\\hspace{1.65cm}\\fbox{\\parbox{\\textwidth}{\\copyright~2016 IEEE. Personal use of this material is permitted. Permission from IEEE must be obtained for all other uses, in any current or future media, including reprinting/republishing this material for advertising or promotional purposes, creating new collective works, for resale or redistribution to servers or lists, or reuse of any copyrighted component of this work in other works.}}}}'
if idxLastUsepackage != 0:
    contents.insert(idxLastUsepackage,'\\usepackage{eso-pic}\n\n'+copyrightNotice+'\n') 

# write modified contents to output file
f = open(filename,'w')
contents = "".join(contents)
f.write(contents)
f.close()
