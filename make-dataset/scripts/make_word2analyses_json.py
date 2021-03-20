# -*- coding: utf-8 -*-

'''
:author: Emily Chen
:date:   2020

Generates the 'word2analyses.json' file for a selected corpus, formatted like so:

    {"anipaghllak0":
        {"analyses": [anipa(N)^ghllag(NN)^[Abs.Sg], anipaghllag(N)^[Abs.Sg]],
         "num deriv": [1, 0]
        },
     "naken0":
        {"analyses": [naken(WH)],
         "num deriv": [0]
        },
     .
     .
     .
     "anipaghllak1":
        {"analyses": [anipa(N)^ghllag(NN)^[Abs.Sg], anipaghllag(N)^[Abs.Sg]],
         "num deriv": [1, 0]
        },
     .
     .
     .
    }

PREREQS:
    * a directory of Yupik texts
          the selected corpus
    * unanalyzed.tsv
          proposed analyses for words the analyzer cannot handle
    * neural_uppercase.fomabin
          Yupik FST analyzer that handles both lowercase and uppercase
    * yupik.cg3
          Yupik constraint grammar

USAGE:
    python3 make_word2analyses_json.py [INCLUDE-ERROR-FLAG]

NOTE: Check file paths in this file and 'scripts/run_cg.sh'
      Set [PARAM] to "dataset" in subprocess.call(["scripts/run_cg.sh", [PARAM] ])
        if generating a training dataset, "devset" otherwise
       

'''
import argparse
import csv
import json
import pprint
import random
import re
import subprocess

from contextlib import redirect_stdout
from format_analyses_for_cg import reformat_analyses
from foma import *


def convert_cg_to_fst_format(analysis):
    '''
    :param analysis: the text to convert
    :type  analysis: str

    Reformats an analysis from constraint grammar output format
    to FST output format that is conducive to sampling, e.g.
       FROM = "qiya" (N) [Ind] [Intr] [3Sg] <DER:0>
       TO   = qiya(V)^[Ind.Intr.3Sg]

    '''
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

    # there's some bug where asterisked noun roots are getting tagged twice
    # idk where this is occurring so we're just going to fix it here...
    if "(N)*(N)" in fst_analysis:
        tmp = fst_analysis.replace("(N)*","*")
        fst_analysis = tmp

    # reformat interrogative
    #elif "Intrg" in fst_analysis:
    #    tmp = fst_analysis.replace("[Intrg.Intr]^[2Sg]","[Intrg.Intr.2Sg]") \
    #                      .replace("[Intrg.Intr]^[2Pl]","[Intrg.Intr.2Pl]") \
    #                      .replace("[Intrg.Intr]^[2Du]","[Intrg.Intr.2Du]")
    #    fst_analysis = tmp

    # fix optative
    #elif "Opt" in fst_analysis:
    #    tmp = fst_analysis.replace("[Opt.Pres.Intr]^[2Sg]","[Opt.Pres.Intr.2Sg]") \
    #                      .replace("[Opt.Pres.Trns]^[2Sg.3Sg]","[Opt.Pres.Trns.2Sg.3Sg]") \
    #                      .replace("[Opt.Neg.Pres.Trns]^[2Sg.3Pl]","[Opt.Neg.Pres.Trns.2Sg.3Pl]") \
    #                      .replace("[Opt.Neg.Pres.Trns]^[2Pl.3Pl]","[Opt.Neg.Pres.Trns.2Pl.3Pl]") \
    #                      .replace("[Opt.Neg.Pres.Trns]^[2Du.3Pl]","[Opt.Neg.Pres.Trns.2Du.3Pl]")
    #    fst_analysis = tmp
    return fst_analysis


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
                else: 
                    unanalyzed2analysis[key] = line 

        #pprint.pprint(unanalyzed2analysis)

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


def write_out_to_json(word2analyses, jsonfile):
    '''
    :param word2analyses: a list of tuples, where each tuple
                          is of the form (str, list)
    :type  word2analyses: list
    :param jsonfile: file path to json output
    :type  jsonfile: str

    Writes out 'word2analyses' to a json file whose path is given
    in the parameter 'jsonfile'.

    '''
    d = {}
    key_counter = {}

    for tup in word2analyses:

        # (1) locate the original word
        word = tup[0].split("<")[1].split(">")[0]

        # (2) locate the analyses
        list_analyses = []
        list_num_deriv_suffixes = []

        for analysis in tup[1]:
            if "DER" in analysis:
                fst_analysis = convert_cg_to_fst_format(analysis)
                num_deriv_suffixes = int(analysis.split("<DER:")[1].split(">")[0])

                list_analyses.append(fst_analysis)
                list_num_deriv_suffixes.append(num_deriv_suffixes)
            else:
                list_analyses.append(analysis)
                list_num_deriv_suffixes.append(0)

        # update the dictionary d
        if word not in key_counter.keys():
            d[word + "0"] = {"analyses": [], "num deriv": []}
            d[word + "0"]["analyses"] = list_analyses
            d[word + "0"]["num deriv"] = list_num_deriv_suffixes

            key_counter[word] = 1
        else: 
            d[word + str(key_counter[word])] = {"analyses": [], "num deriv": []}
            d[word + str(key_counter[word])]["analyses"] = list_analyses
            d[word + str(key_counter[word])]["num deriv"] = list_num_deriv_suffixes

            key_counter[word] += 1

    with open(jsonfile, 'w') as f:
        json.dump(d, f)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--proposed_analyses', help='file path to proposed analyses for unanalyzed words')
    args = parser.parse_args()

    # (1) run the analyzer and the constraint grammar
    #     over the selected dataset
    print("running constraint grammar...")
    subprocess.call(["scripts/run_cg.sh", "dataset"])

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


    # (2) write 'one2one_word_analysis' out to json format
    print("writing out json file...")

    jsonfile = "/home/chenemile/thesis-work/make-dataset/word2analyses.json"
    write_out_to_json(word_and_analyses, jsonfile)


if __name__ == "__main__":
    main()
