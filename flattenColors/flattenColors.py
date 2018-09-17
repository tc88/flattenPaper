#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created in 10/2016 by Thorben Casper 
# edited by Thorben Casper
# This script changes a .tex file in a way that the color definitions are flattened and only the colors that are needed are included. The used .tex file needs to be flattened before this script is applied.

import os
import argparse
import re

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help="the .tex-file that shall be modified")
parser_args = parser.parse_args()
filename = parser_args.tex_file

# identify tud style file
path = os.path.dirname(os.path.abspath(__file__))
if os.path.isfile('tud_colors_presentation.sty'):
    f_tud_colors = 'tud_colors_presentation.sty'
else:
    f_tud_colors = 'tud_colors_publications.sty'

# find colors that are used in document
f = open(filename,'r')
content = f.readlines()
usedColors = []
for line in content:
    m = re.search('(tud\d+[a-d])',line)
    if m:
        usedColors.append(m.group(1))
f.close()
usedColors = list(set(usedColors))
usedColors.sort()

# find the lines in tudcolor .sty file that need to be added
f = open(f_tud_colors,'r')
tud_colors = f.readlines()
lines2add = []
for line in tud_colors:
    # if CMYK colors are used, we need the \defineCMYKcolor command
    if '\\def\\defineCMYKcolor' in line or 'pgfmathsetmacro' in line or 'cmyk' in line or line == '}\n':
        lines2add.append(line)
    m = re.search('(tud.+?)}',line)
    if m and m.group(1) in usedColors:
        lines2add.append(line)
f.close()

# read in .tex file and save position to add color definitions in next step
f = open(filename,'r')
lastUsepackage = 0
contents = []
for num, line in enumerate(f,1):
    if not '\\usepackage{tud_colors' in line:
        contents.append(line)
    if '\\usepackage' in line:
        lastUsepackage = num
f.close()

# add lines to content list
lines2add.append('\n')
contents[lastUsepackage:lastUsepackage]=lines2add        
contents = "".join(contents)

# write modified contents to output file
f = open(filename,'w')
f.write(contents)
f.close()

# remove .sty file
os.remove(f_tud_colors)
