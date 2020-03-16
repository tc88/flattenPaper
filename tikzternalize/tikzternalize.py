#!/usr/bin/env python
# -*- coding: utf-8 -*-
# changes a .tex file in a way that all tikz figures are included as pdf files 
# 
# Usage: - tikzternalize example.tex figsDir flatDir quiet
#
# Tested under Linux and Windows
#
# The figures are numbered according to the figure numbers in the paper. If subfigures are involved, this script supports the subcaption, subfigure and subfig package to add 'a', 'b', [...] to the figure numbers. However, special options of these packages might not be supported
#
# options
# - flatDir: if True, a flat output directory is generated
# - quiet: enables quiet output
#
# prerequisites
# - different figures must have different names, not only different extensions
# - if \graphicspath is used for \includegraphics, only figsDir must be given as the argument
# - if externalize library is loaded and its prefix is set in .tex file, it must be done before last \usepackage command
#
# commented lines are ignored
#
# author: Thorben Casper 
# created in 2016/10

import os
import argparse
import subprocess
import re
import glob
import shutil

print("shadowing figure sources by applying tikzternalize ...")

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("tex_file", help=".tex-file that shall be modified")
parser.add_argument("figsDir" , help="directory, in which ALL figures are contained")
parser.add_argument("flatDir" , help="if true, a flat output directory is generated")
parser.add_argument("quiet"   , help="enables quiet output")
# example how to include additional optional arguments
# parser.add_argument("-c","--createPDF", help="use if you want to create the .pdf directly",action="store_true")
parser_args = parser.parse_args()
filename = parser_args.tex_file
figsDir = parser_args.figsDir
flatDir = int(parser_args.flatDir)
quiet = int(parser_args.quiet)

# reads .tex file and mainly saves line numbers for tikz pictures and the file names of includegraphics files
f = open(filename,'r')
contents = []                     # collects file content in array of lines
lineIdxTikz = []                  # collects all first lines of a tikzpicture environment 
figIdxTikz = []                   # collects all figure indices of tikzpicture figures
figIdxInclude = []                # collects all figure indices of \include* figures
figIdxIncludeLineNo = []          # collects line numbers of \include* figures
figIdxSuffix = ''                 # handles to add letter if subfigures are used
graphicsNames = []                # collects all file names that were originally included using includegraphics
foundExternalize = False          # initializes switch whether externalize library is already used
foundExternalizePrefix = False    # initializes switch whether prefix of externalize library is already set
lastUsepackage = 0                # line of last usepackage use in main .tex file
figCounter = 0                    # top level figure counter
insideTikzEnviron = False         # indicator whether inside of a tikz environment
insideCommentEnviron = False      # indicator whether inside of a comment environment
for num, line in enumerate(f,1):
    contents.append(line)
    if line.strip() and not line.strip()[0] == '%':
        if '\\end{tikzpicture}' in line:
            insideTikzEnviron = False
        if '\\end{comment}' in line:
            insideCommentEnviron = False
        if not insideCommentEnviron and not insideTikzEnviron: # only check for new figures if outside of any tikz environment
            if '\\begin{figure}' in line or '\\begin{figure*}' in line:
                figCounter += 1
            if '\\begin{subfigure}' in line or '\\subfloat' in line or '\\subfigure' in line:
                if not figIdxSuffix:
                    figIdxSuffix = 'a'
                else:
                    figIdxSuffix = chr(ord(figIdxSuffix)+1)
            if '\\end{figure}' in line or '\\end{figure*}' in line:
                figIdxSuffix = '';
            if ('\\usepgfplotslibrary' in line or '\\usetikzlibrary' in line) and 'external' in line:
                foundExternalize = True
            if 'tikzexternalize[prefix' in line:
                foundExternalizePrefix = True
            if '\\usepackage' in line:
                lastUsepackage = num
            if '\\begin{tikzpicture}' in line:
                insideTikzEnviron = True
                lineIdxTikz.append(num)
                figIdxTikz.append(str(figCounter)+figIdxSuffix)
            if '\\begin{comment}' in line:
                insideCommentEnviron = True
            if '\\includegraphics' in line:
                match = re.search(r'includegraphics.*{(.+?)}',line)
                searchResult = match.group(1)
                figPath = os.path.dirname(searchResult)
                figName = os.path.splitext(os.path.basename(searchResult))[0]
                files2copy = glob.glob(figPath+'/'+figName+'*')
                for ff in files2copy:
                    if not figsDir in ff:
                        shutil.copy(ff,'./'+figsDir+'/'+os.path.basename(ff))
                if flatDir:
                    contents[-1] = line.replace('{'+searchResult+'}','{./fig'+str(figCounter)+figIdxSuffix+'}')
                else:
                    contents[-1] = line.replace('{'+searchResult+'}','{./'+figsDir+'/fig'+str(figCounter)+figIdxSuffix+'}')
                graphicsNames.append(os.path.splitext(os.path.basename(searchResult))[0])
                figIdxInclude.append(str(figCounter)+figIdxSuffix)
                figIdxIncludeLineNo.append(num)
            if '\\includestandalone' in line:
                match = re.search(r'includestandalone.*{(.+?)}',line)
                searchResult = match.group(1)
                figPath = os.path.dirname(searchResult)
                figName = os.path.splitext(os.path.basename(searchResult))[0]
                files2copy = glob.glob(figPath+'/'+figName+'*')
                for ff in files2copy:
                    if not figsDir in ff:
                        shutil.copy(ff,'./'+figsDir+'/'+os.path.basename(ff))
                if flatDir:
                    contents[-1] = line.replace(searchResult,'./fig'+str(figCounter)+figIdxSuffix)
                else:
                    contents[-1] = line.replace(searchResult,'./'+figsDir+'/fig'+str(figCounter)+figIdxSuffix)
                contents[-1] = contents[-1].replace('includestandalone','includegraphics') 
                graphicsNames.append(os.path.splitext(os.path.basename(searchResult))[0])
                figIdxInclude.append(str(figCounter)+figIdxSuffix)
                figIdxIncludeLineNo.append(num)
f.close()

# modify \include* commands by appending {'a','b',...} to the file names such that no duplicate entries exist (occurs when multiple \includegraphics commands are used in one figure environment)
suffix = 'a'
temp = figIdxInclude[:]
for i in range(len(figIdxInclude)):
    line = contents[figIdxIncludeLineNo[i]-1]
    if i<len(figIdxInclude)-1 and figIdxInclude[i] == figIdxInclude[i+1]:
        temp[i] = figIdxInclude[i]+suffix
        contents[figIdxIncludeLineNo[i]-1] = line.replace('fig'+figIdxInclude[i],'fig'+figIdxInclude[i]+suffix)
        suffix = chr(ord(suffix)+1)
if len(figIdxInclude) > 1 and figIdxInclude[-1] == figIdxInclude[-2]:
    temp[-1] = figIdxInclude[-1]+suffix
    contents[figIdxIncludeLineNo[-1]-1] = line.replace('fig'+figIdxInclude[-1],'fig'+figIdxInclude[-1]+suffix)
figIdxInclude = temp

# copy files that are used by includegraphics and includestandalone according to new name
os.chdir(figsDir)
for i in range(len(graphicsNames)):
    if os.path.isfile(graphicsNames[i]+'.eps'):
        os.remove(graphicsNames[i]+'.eps')
    for figname in glob.glob(graphicsNames[i]+'*'):
        if figname[-4:] == '.tex':
            continue
        if os.path.splitext(figname)[0] == graphicsNames[i] or "-eps-converted-to" in figname:
            if "-eps-converted-to" in figname:
                os.rename(figname,re.sub("-eps-converted-to","",figname))
                figname = re.sub("-eps-converted-to","",figname)
            new_name = re.sub(graphicsNames[i],'fig'+figIdxInclude[i],figname)
            if flatDir:
                shutil.copyfile(figname,'../'+new_name)
            else:
                shutil.copyfile(figname,new_name)
os.chdir('..')

# adds tikzexternalizer loading commands
if lastUsepackage != 0 and figIdxTikz:
    if not foundExternalize:
        contents.insert(lastUsepackage  ,'\\usetikzlibrary{external}\n')
    if not foundExternalizePrefix:
        contents.insert(lastUsepackage+1,'\\tikzexternalize[prefix='+figsDir+'/]\n')
        contents.insert(lastUsepackage+2,'\\tikzset{external/system call={pdflatex \\tikzexternalcheckshellescape --output-directory=build -halt-on-error -interaction=batchmode -jobname "\image" "\\texsource"}}\n')

# add tikzsetnextfilename commands to make the tikzexternalizer use the correct filenames
if len(lineIdxTikz) != 0:
    lineIdxTikz.reverse() # walk backwards since additional lines are to be included
    figIdxTikz.reverse()  # walk backwards since additional lines are to be included
    for i in range(len(figIdxTikz)):
        contents.insert(lineIdxTikz[i]+2, '\\tikzsetnextfilename{fig'+figIdxTikz[i]+'}\n')

# write modified contents back to file
f = open(filename,'w')
contents = "".join(contents)
f.write(contents)
f.close()

# call pdflatex to let tikzexternalizer do its work
FNULL = open(os.devnull,'w')
if not quiet:
    subprocess.call(["pdflatex", "-shell-escape","--output-directory=build", filename])
else:
    subprocess.call(["pdflatex", "-shell-escape","--output-directory=build", filename],stdout=FNULL)

# move pdf files from build-directory to figsDir
if len(lineIdxTikz) !=0:
    for i in range(len(figIdxTikz)):
        if flatDir:
            shutil.move('./build/'+figsDir+'/fig'+figIdxTikz[i]+'.pdf','./')
        else:
            shutil.move('./build/'+figsDir+'/fig'+figIdxTikz[i]+'.pdf','./'+figsDir+'/')

# find line numbers where tikzpicture-environment starts and ends
f = open(filename,'r')
contents = []             # collects file content in array of lines
idxTikzBegin = []         # line where tikz environment starts
idxTikzEnd = []           # line where tikz environment ends
indicesDelete = []        # lines that shall be removed (that contain tikzsetfilename)
insideTikzEnviron = False # indicator whether inside of a tikz environment
for num, line in enumerate(f,1):
    contents.append(line)
    if '\\end{tikzpicture}' in line:
        insideTikzEnviron = False
    if '\\end{comment}' in line:
        insideCommentEnviron = False
    if not insideCommentEnviron and not insideTikzEnviron:
        if '\\tikzsetnextfilename' in line:
            indicesDelete.append(num)
        if '\\begin{tikzpicture}' in line:
            idxTikzBegin.append(num)
            insideTikzEnviron = True
        if '\\begin{comment}' in line:
            insideCommentEnviron = True
        if '\\end{tikzpicture}' in line:
            idxTikzEnd.append(num)
f.close()

# replaces tikzpicture environments with includegraphics commands
idxTikzBegin.reverse()
idxTikzEnd.reverse()
indicesDelete.reverse()

for i in range(0,len(idxTikzBegin)):
    idxBegin = idxTikzBegin[i]-1
    idxEnd = idxTikzEnd[i]-1
    idxDelete = indicesDelete[i]-1
    if flatDir:
        contents[idxBegin] = re.sub(r'\\begin{tikzpicture}\[*.*\]*','\\includegraphics{./fig'+figIdxTikz[i]+'}',contents[idxBegin])
    else:
        contents[idxBegin] = re.sub(r'\\begin{tikzpicture}\[*.*\]*','\\includegraphics{'+figsDir+'/fig'+figIdxTikz[i]+'}',contents[idxBegin])
    contents[idxEnd] = re.sub(r'\\end{tikzpicture}\s?','',contents[idxEnd])
    if not contents[idxEnd]:
        del contents[idxEnd]
    del contents[idxBegin+1:idxEnd]
    del contents[idxDelete]

# write out cleaned up file
f = open(filename,'w')
contents = "".join(contents)
f.write(contents)
f.close()

# clean figsDir directory by removing original figure files 
os.chdir(figsDir)
for i in range(len(graphicsNames)):
    for figname in glob.glob(graphicsNames[i]+'*'):
        os.remove(figname)
for figname in glob.glob('*.tex'):
    os.remove(figname)
os.chdir("..")

print("finished applying tikzternalize.")
