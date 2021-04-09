# -*- coding: utf-8 -*-
# USAGE:
# cat ../ben/test_sentences.txt \
#     | python preprocess_analyses_for_sentences.py \
#     > ../ben/test_sentences.input

import sys
import os
import re
import string

def reformat_analyses(analysis_line):
    surface_form = ""
    if analysis_line: # e.g. 'esghaatut    esghagh(V)^~:(ng)u(V→V)^+te(V→V)^[Ind.Intr]^[3Pl]'
        anaphor_base = ""
        n_derivation = 0
        if analysis_line.split("\t")[0].strip() != "":
            if surface_form != analysis_line.split("\t")[0].strip(): # surface_form = 'esghaatut'
                surface_form = analysis_line.split("\t")[0].strip()
                print('"<' + surface_form + '>"' )

            if surface_form in string.punctuation:
                print('  "' + surface_form + '" [Punct]\n')

            else:
                analysis = analysis_line.split("\t")[1].strip() # 'esghagh(V)^~:(ng)u(V→V)^+te(V→V)^[Ind.Intr]^[3Pl]'
                base = analysis.split('^')[0].strip() # 'esghagh(V)'
                if base == "[Anaphor]": # e.g. taakuq   [Anaphor]^ukuq(DEM.PRO.Abs.Sg)
                    anaphor_base = base
                    base = analysis.split('^')[1]
                    analysis = analysis.replace('(DEM', '[DEM')
                    analysis = analysis.replace('Sg)', 'Sg]') # ukuq(DEM.PRO.Abs.Sg) -> ukuq[DEM.PRO.Abs.Sg]
                    analysis = analysis.replace('Pl)', 'Pl]')
                    analysis = analysis.replace('Du)', 'Du]')
                    analysis = analysis.replace('PRO)', 'PRO]')
                    analysis = analysis.replace('ADV)', 'ADV]')
                    analysis = analysis.replace('ADV.Loc)', 'ADV.Loc]')
                    analysis = analysis.replace('ADV.All)', 'ADV.All]')
                    analysis = analysis.replace('ADV.Prl)', 'ADV.Prl]')
                    analysis = analysis.replace('ADV.Abl_Mod)', 'ADV.Abl_Mod]')
                base = base.replace('(', ' (') # 'esghagh (V)'
                base = base.replace('=', ' =')
                base = base.split()[0].strip() # 'esghagh'
                #tags = analysis.replace(base, '') # '(V)^~:(ng)u(V→V)^+te(V→V)^[Ind.Intr]^[3Pl]'
                tags  = analysis.split(base)[1] 
                # tags = tags.replace(anaphor_base, '')
                tags_str = tags.replace('^', ' ').strip() # '(V) ~:(ng)u(V→V) +te(V→V) [Ind.Intr] [3Pl]'
                tags_str = re.sub(r'\(([A-Z]+)(→)([A-Z]+)\)', r" (\1\2\3)", tags_str) # '(V) ~:(ng)u (V→V) +te (V→V) [Ind.Intr] [3Pl]' or '(EMO→V)'
                tags_str = re.sub(r'(\(CmpdVbl\))', r' \1 ', tags_str) # in case of +(te)ste(CmpdVbl) etc.
                tags_str = tags_str.replace('.', '] [') # '(V) ~:(ng)u (V→V) +te (V→V) [Ind] [Intr] [3Pl]'
                tags_str = tags_str.replace('=', ' = ') # e.g. 'kaa(PTCL) = tuq'
                tags_str = tags_str.replace('@', '\@') # @ is reserved for mapping in cg3
                n_derivation += tags_str.count("→") # count derivational tags such as (V→V)
                n_derivation += tags_str.count("CmpdVbl") # count derivational CmpdVbl tag
                n_derivation += tags_str.count("Augmentive") # count derivational Augmentive tag
                print('  "' + base + '" ' + tags_str + " <DER:" + str(n_derivation) + ">")


if __name__ == '__main__':

    if not sys.stdin.isatty():
        for line in sys.stdin:
            if line:
                reformat_analyses(line)
    else:
        filename = "/home/echen41/neural-experiments-thesis/make-dataset/stories.analyses"

        with open(filename, 'r') as f:
            for line in f:
                if line:
                    reformat_analyses(line)
