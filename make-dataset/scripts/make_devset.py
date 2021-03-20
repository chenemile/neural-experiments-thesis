# -*- coding: utf-8 -*-

'''
:author: Emily Chen
:date:   2021

'''
import argparse
import pprint
import re
import subprocess

from format_analyses_for_cg import reformat_analyses

from contextlib import redirect_stdout
from foma import *


def convert_cg_to_fst(analysis):
    '''
    :param analysis: the text to convert
    :type  analysis: str

    Reformats an analysis from constraint grammar output format
    to FST output format:
       FROM = "qiya" (N) [Ind] [Intr] [3Sg] <DER:0>
       TO   = qiya(V)^[Ind.Intr]^[3Sg]

    '''
    # this is code from 'convert_cg_to_fst_format()' from 'make_word2analyses_json.py'
    cg_analysis = analysis.split("\"", 1)[1].split(" <DER:")[0]

    fst_analysis = cg_analysis.replace("\"","").replace("\\","") \
                              .replace(" = ","^=").replace(" ?","^?").replace("? ","?^").replace(" (?)","(?)") \
                              .replace(" (N","(N").replace(" (V","(V") \
                              .replace("N) ","N)^").replace("V) ","V)^") \
                              .replace("] [",".") \
                              \
                              .replace(" (P","(P").replace(" (WH","(WH") \
                              .replace(" (AREA) ","(AREA)^").replace(" (CmpdVbl) ","(CmpdVbl)^") \
                              .replace(" (EMO","(EMO").replace(" (POS","(POS") \
                              .replace(" (QUANTQUAL)","(QUANTQUAL)").replace(" (XCLM)","(XCLM)") \
                              .replace(" @","^@").replace(" ~","^~").replace(" –","^–").replace(" +","^+") \
                              .replace(" e","^e").replace(" (ADJ)", "(ADJ)").replace(" [", "^[").replace(" ","")
                              #.replace("Intr.","Intr]^[").replace("Trns.","Trns]^[") \
                              #.replace(" Fear.","Fear]^[") \

    # reformat demonstratives
    if "DEM" in fst_analysis:
        if "Anaphor" in fst_analysis:
            tmp = re.sub(r'DEM([a-zA-Z\._]*)]', r'DEM\1)', fst_analysis)
            fst_analysis = "[Anaphor]" + tmp.replace("^[Anaphor.DEM","(DEM") \
                                            .replace(".Ind",")^[Ind").replace(".Ptcp",")^[Ptcp") \
                                            .replace(".Sbrd",")^[Sbrd") \
                                            .replace(".C",")^[C").replace(".O",")^[O") # catch-all for remaining verb moods

    # reformat vocatives
    if "Voc" in fst_analysis:
        tmp = fst_analysis.replace(".Voc","]^[Voc")
        fst_analysis = tmp

    # this is code from 'convert_to_fst_input()' from 'make_surface.py'
    #   too lazy to make this look nice
    fused_infl = ["[Opt.Pres.Intr.2Sg]",
                  "[Opt.Pres.Trns.2Sg.3Sg]",
                  "[Opt.Neg.Pres.Trns.2Sg.3Pl]",
                  "[Opt.Neg.Pres.Trns.2Pl.3Pl]",
                  "[Opt.Neg.Pres.Trns.2Du.3Pl]",
                  "[Intrg.Intr.2Sg]",
                  "[Intrg.Intr.2Pl]",
                  "[Intrg.Intr.2Du]"
                 ]

    converted = fst_analysis

    if "Intr" in fst_analysis or "Trns" in fst_analysis:
        if not any(infl in fst_analysis for infl in fused_infl):
            converted = fst_analysis.replace("Intr.", "Intr]^["). \
                               replace("Trns.", "Trns]^[")

    if "Anaphor" in fst_analysis:
        converted = fst_analysis.replace("Anaphor]", "Anaphor]^")

    if "(DEM.PRO)" in fst_analysis:
        if "Poss" in fst_analysis:
            converted = fst_analysis[:-12] + fst_analysis[-4:]
        elif "[Abs.Pl]" in fst_analysis or "[Abs.Du]" in fst_analysis:
            converted = fst_analysis.replace("[Abs", "[AbsRel") \
                              .replace("[Rel", "[AbsRel")

    if "ingagh(POS)" in fst_analysis:
        converted = fst_analysis.replace("ingagh(POS)","ingagh*(POS)")

    if "=" in fst_analysis:
        converted = fst_analysis.replace("^=", "=")

    return converted


def fill_in_unanalyzed(analyzed, unanalyzed):
    '''
    :param analyzed: file containing FST output for every
                     word in the selected corpus in constraint
                     grammar format
    :type  analyzed: str
    :param unanalyzed: file containing every uananalyzed word 
                       in the selected corpus with a proposed
                       analysis in constraint grammar format
    :type  unanalyzed: str

    :return: list of tuples

    Returns a list of tuples 'word_and_analyses', where the first
    value is a word in the corpus and the second value is a list of
    analyses for that word.
    For each unanalyzed word in the corpus,
    use the analysis proposed by me listed in the file denoted by
    the parameter 'unanalyzed'.
    
    '''
    word_and_analyses = [] 

    if unanalyzed:
        unanalyzed2analysis = {}
        with open(unanalyzed, mode='r', encoding='utf-8-sig') as f:
            key = ""

            for line in f:
                # line contains a word
                if line[1] == "<":
                    key = line
                    unanalyzed2analysis[key] = ""

                # line contains an analysis
                else: 
                    unanalyzed2analysis[key] = line 

    with open(analyzed) as f:
        word = ""
        analyses = []

        for line in f:
            if line.strip() != "":

                # line contains a word
                if line[1] == "<":
                    
                    # check if the current line contains a new word
                    # if so, add the previous word and its analyses
                    if line != word:
                        word_and_analyses.append((word, analyses))
                        word = line 
                        analyses = []
                else: 
                    # check if the word went unanalyzed and add the proposed analysis
                    if unanalyzed:
                        if word in unanalyzed2analysis:
                            analyses.append(unanalyzed2analysis[word])
                        elif word.lower() in unanalyzed2analysis:
                            analyses.append(unanalyzed2analysis[word.lower()])
                        else:
                            analyses.append(line)

                    # otherwise, add the current analysis to the list of analyses
                    else:
                        analyses.append(line)

        # don't forget to add the last word and its analyses
        word_and_analyses.append((word, analyses))

    # remove the empty ('', []) that gets added
    # during the first pass through the 'for' loop
    word_and_analyses.pop(0)

    #pprint.pprint(word_and_analyses)

    return word_and_analyses


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--proposed_analyses', help='file path to proposed analyses for unanalyzed words')
    args = parser.parse_args()

    # (1) run the analyzer and the constraint grammar
    #     over the selected dataset
    print("running constraint grammar...")
    subprocess.call(["scripts/run_cg.sh", "devset"])

    if args.proposed_analyses:
        # (1a) convert the proposed analyses for the unanalyzed
        #     words to constraint grammar output format
        #       e.g."aghnegh" (N) [Loc] [Sg] <DER:0>
        print("converting error analysis to cg format...")
    
        unformatted = args.proposed_analyses
        formatted   = "/home/chenemile/thesis-work/make-dataset/unanalyzed.output"
    
        with open(unformatted, 'r') as input_file:
            lines = input_file.readlines()
            with open(formatted, 'w') as output_file:
                with redirect_stdout(output_file):
                    for line in lines:
                        reformat_analyses(line)
    
        # (1b) fill in the proposed analyses so every word
        #     in the selected dataset has at least one analysis,
        #     either from the analyzer or from me
        print("replacing +? with proposed analyses...")
    
        analyzed = "/home/chenemile/thesis-work/make-dataset/stories.output"
        unanalyzed = "/home/chenemile/thesis-work/make-dataset/unanalyzed.output"
        word_and_analyses = fill_in_unanalyzed(analyzed, unanalyzed)
    else:
        print("converting cg output to dict format...")

        analyzed = "/home/chenemile/thesis-work/make-dataset/stories.output"
        unanalyzed = ""
        word_and_analyses = fill_in_unanalyzed(analyzed, unanalyzed)


    # (2) write out 'word_and_analyses' to 'devset-files/devset.tsv
    devset = "/home/chenemile/thesis-work/make-dataset/devset-files/devset.tsv"

    with open(devset, 'w') as f: 
        for tup in word_and_analyses:

            # (1) locate the original word
            word = tup[0].split("<")[1].split(">")[0]

            # (2) get the shortest analysis
            analysis = min(tup[1], key=len)

            if "PUNCT" not in analysis and \
               "Punct" not in analysis and \
               "?" not in analysis:
                 underlying_form = convert_cg_to_fst(analysis).strip()

                 f.write(underlying_form + "\t" + word + "\n")


if __name__ == "__main__":
    main()
