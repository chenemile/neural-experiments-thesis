# -*- coding: utf-8 -*-
'''
:author: Emily Chen
:date:   2021

'''
import argparse
import csv
import json
import pprint
import random
import re
import operator


def get_zipfdist_of_morphemes_over_random_analyses(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: tuple of the form (dict, dict, dict)

    Counts the number of occurrences of each morpheme in a randomly
    chosen analysis for each word (using a uniform distribution to choose).

    Returns:
      * uniform_w2a:      a dict where each key is a word mapped to
                          a randomly chosen analysis and the number of
                          derivational morphemes in that analysis.
      * zipf_dist:        a dict where each key is a morpheme and
                          each value is the number of occurrences of that
                          morpheme.
                          Sorting this dict by value returns the Zipfian
                          distribution.
      * deriv_count_dist: a dict where each key is the number of
                          derivational morphemes and each value is
                          the number of words with that many
                          derivational morphemes.

    '''
    uniform_w2a         = {}
    morpheme_dist       = {}
    deriv_count_dist    = {}

    for word in word2analyses:
        analyses = word2analyses[word]["analyses"]

        # ignore punctuation
        if word and any(char.isalpha() for char in word):

            # uniformly select a random analysis for each word
            # if it has multiple analysis
            idx = random.randint(0, len(analyses)-1)
            chosen_analysis = analyses[idx] 

            if chosen_analysis != "+?":
                morphemes = chosen_analysis.split("^")

                for m in morphemes:
                    if m in morpheme_dist:
                        morpheme_dist[m] += 1
                    else:
                        morpheme_dist[m] = 1

            # update 'uniform_w2a' which tracks the one analysis that
            # was chosen at random for each word
            uniform_w2a[word] = {"analyses":[], "num deriv":[]}
            uniform_w2a[word]["analyses"].append(chosen_analysis)

            num_deriv = word2analyses[word]["num deriv"][idx]
            uniform_w2a[word]["num deriv"].append(num_deriv)

            # update 'deriv_count_dist' which counts the number of words
            # that contains N derivational morphemes
            if num_deriv in deriv_count_dist:
                deriv_count_dist[num_deriv] += 1
            else:
                deriv_count_dist[num_deriv] = 1

    #zipf_dist = sorted(morpheme_dist.items(), word=lambda item: item[1], reverse=True)

    return uniform_w2a, morpheme_dist, deriv_count_dist


def get_zipfdist_of_morphemes_over_shortest_analyses(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: tuple of the form (dict, dict, dict)

    Method name is somewhat misleading.
    Counts the number of occurrences of each morpheme in the analysis
    with the fewest number of morphemes. If there are multiple options,
    choose one using a uniform distribution.

    Returns:
      * shortest_w2a:     a dict where each key is a word mapped to
                          the analysis with the fewest number of
                          derivational morphemes and the number of
                          derivational morphemes in that analysis.
      * zipf_dist:        a dict where each key is a morpheme and
                          each value is the number of occurrences of that
                          morpheme.
                          Sorting this dict by value returns the Zipfian
                          distribution.
      * deriv_count_dist: a dict where each key is the number of
                          derivational morphemes and each value is
                          the number of words with that many
                          derivational morphemes.

    '''
    shortest_w2a        = {}
    morpheme_dist       = {}
    deriv_count_dist    = {}

    for word in word2analyses:
        analyses = word2analyses[word]["analyses"]
        deriv_counts = word2analyses[word]["num deriv"]

        # ignore punctuation
        if word and any(char.isalpha() for char in word):

            # get the number of derivational morphemes that the analysis
            # with the fewest number of derivational morphemes has
            min_num_deriv = min(deriv_counts)

            # select the analyses with the fewest number of derivational
            # morphemes and select one at random (uniform dist) 
            has_fewest_deriv = []
            for idx, analysis in enumerate(analyses):
                num_deriv = deriv_counts[idx]
                if num_deriv == min_num_deriv:
                    has_fewest_deriv.append(analysis)
            chosen_analysis = random.choice(has_fewest_deriv)

            if chosen_analysis != "+?":
                morphemes = chosen_analysis.split("^")

                for m in morphemes:
                    if m in morpheme_dist:
                        morpheme_dist[m] += 1
                    else:
                        morpheme_dist[m] = 1

            # update 'shortest_w2a' which tracks the one analysis that
            # was chosen for each word
            shortest_w2a[word] = {"analyses":[], "num deriv":[]}
            shortest_w2a[word]["analyses"].append(chosen_analysis)

            num_deriv = word2analyses[word]["num deriv"][idx]
            shortest_w2a[word]["num deriv"].append(num_deriv)

            # update 'deriv_count_dist' which counts the number of words
            # that contains N derivational morphemes
            if num_deriv in deriv_count_dist:
                deriv_count_dist[num_deriv] += 1
            else:
                deriv_count_dist[num_deriv] = 1

    #zipf_dist = sorted(morpheme_dist.items(), word=lambda item: item[1], reverse=True)

    return shortest_w2a, morpheme_dist, deriv_count_dist


def get_zipfdist_of_morphemes_over_random_and_shortest_analyses(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: tuple of the form (dict, dict, dict)

    Counts the number of occurrences of each morpheme in the shortest analysis
    75% of the time, and a randomly chosen analysis the remaining 25% of the
    time (using a uniform distribution to choose).

    Returns:
      * mixed_w2a:        a dict where each key is a word mapped to
                          the chosen analysis and the number of
                          derivational morphemes in that analysis.
      * zipf_dist:        a dict where each key is a morpheme and
                          each value is the number of occurrences of that
                          morpheme.
                          Sorting this dict by value returns the Zipfian
                          distribution.
      * deriv_count_dist: a dict where each key is the number of
                          derivational morphemes and each value is
                          the number of words with that many
                          derivational morphemes.

    '''
    mixed_w2a        = {}
    morpheme_dist       = {}
    deriv_count_dist    = {}

    sample_n = random.random()

    for word in word2analyses:
        analyses = word2analyses[word]["analyses"]

        # ignore punctuation
        if word and any(char.isalpha() for char in word):

            # 75% of the time, select the analysis with the fewest 
            # number of derivational morphemes
            chosen_analysis = ""
            idx = 0
            if sample_n <= 0.75:
                deriv_counts = word2analyses[word]["num deriv"]
                min_num_deriv = min(deriv_counts)

                has_fewest_deriv = []
                for index, analysis in enumerate(analyses):
                    num_deriv = deriv_counts[index]
                    if num_deriv == min_num_deriv:
                        has_fewest_deriv.append(analysis)
                chosen_analysis = random.choice(has_fewest_deriv)
                idx = index
            # 25% of the time, select an analysis at random 
            else:
                idx = random.randint(0, len(analyses)-1)
                chosen_analysis = analyses[idx]

            if chosen_analysis != "+?":
                morphemes = chosen_analysis.split("^")

                for m in morphemes:
                    if m in morpheme_dist:
                        morpheme_dist[m] += 1
                    else:
                        morpheme_dist[m] = 1

            # update 'mixed_w2a' which tracks the one analysis that
            # was chosen for each word
            mixed_w2a[word] = {"analyses":[], "num deriv":[]}
            mixed_w2a[word]["analyses"].append(chosen_analysis)

            num_deriv = word2analyses[word]["num deriv"][idx]
            mixed_w2a[word]["num deriv"].append(num_deriv)

            # update 'deriv_count_dist' which counts the number of words
            # that contains N derivational morphemes
            if num_deriv in deriv_count_dist:
                deriv_count_dist[num_deriv] += 1
            else:
                deriv_count_dist[num_deriv] = 1

    #zipf_dist = sorted(morpheme_dist.items(), word=lambda item: item[1], reverse=True)

    return mixed_w2a, morpheme_dist, deriv_count_dist


def get_zipfdist_of_morphemes_over_uniform_fractional_counts(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: tuple of the form (dict, dict, dict)

    Counts the number of occurrences of each morpheme over *all* analyses
    using fractional counts, e.g.
        qikmigh(N)^–ghhagh*(N→N)^[Abl_Mod.Sg]
        qikmigh(N)^–ghhagh*(N→N)^[Rel.4DuPoss.Pl]
        qikmigh(N)^–ghhagh*(N→N)^[Rel.4DuPoss.Sg]
        qikmigh(N)^–ghhagh*(N→N)^[Rel.4PlPoss.Pl]
        qikmigh(N)^–ghhagh*(N→N)^[Rel.4PlPoss.Sg]

    qikmigh = 1 -> (qikmigh appears five times and there are five analyses total)
    –ghhagh = 1
    [Abl_Mod.Sg] = 1/5 = 0.2
    [Rel.4DuPoss.Pl] = 1/5 = 0.2
    [Rel.4DuPoss.Sg] = 1/5 = 0.2
    [Rel.4PlPoss.Pl] = 1/5 = 0.2
    [Rel.4PlPoss.Sg] = 1/5 = 0.2

    Returns:
      * unifrac_w2a:      a dict where each key is a word mapped to
                          a list of analyses and the number of
                          derivational morphemes in each analysis.
      * zipf_dist:        a dict where each key is a morpheme and
                          each value is the fractional count of that
                          morpheme.
                          Sorting this dict by value returns the Zipfian
                          distribution.
      * deriv_count_dist: a dict where each key is the number of
                          derivational morphemes and each value is
                          the fractional count of words with that many
                          derivational morphemes.

    '''
    unifrac_w2a         = word2analyses
    morpheme_dist       = {}
    deriv_count_dist    = {}

    for word in word2analyses:

        # ignore punctuation
        if word and any(char.isalpha() for char in word):
            analyses = word2analyses[word]["analyses"]
            deriv_counts = word2analyses[word]["num deriv"]

            num_analyses = len(analyses)

            for analysis in analyses:
                morphemes = analysis.split("^")

                for morpheme in morphemes:
                    if morpheme in morpheme_dist:
                        morpheme_dist[morpheme] += 1/num_analyses
                    else:
                        morpheme_dist[morpheme] = 1/num_analyses

            # update 'deriv_count_dist' which counts the number of words
            # that contains N derivational morphemes
            for deriv_count in deriv_counts:
                if deriv_count in deriv_count_dist:
                    deriv_count_dist[deriv_count] += 1/num_analyses
                else:
                    deriv_count_dist[deriv_count] = 1/num_analyses

    return unifrac_w2a, morpheme_dist, deriv_count_dist

                    
def get_zipfdist_of_morphemes_over_probable_fractional_counts(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: tuple of the form (dict, dict, dict)

    Counts the number of occurrences of each morpheme over *all* analyses using
    fractional counts based on the probability of words having N number of morphemes, e.g.

    qikmighhaghmeng
        P(word having 3 morphemes) = 0.2  | qikmigh(N) ^ -ghhagh(NN) ^ [Rel.Sg]    -> 0.2 / 2.6 = 0.077
        P(word having 2 morphemes) = 0.6  | qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Pl]  -> 0.6 / 2.6 = 0.23
        P(word having 2 morphemes) = 0.6  | qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Sg]  -> 0.6 / 2.6 = 0.23
        P(word having 2 morphemes) = 0.6  | qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Pl]  -> 0.6 / 2.6 = 0.23
        P(word having 2 morphemes) = 0.6  | qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Sg]  -> 0.6 / 2.6 = 0.23

        each probability -> NUMERATOR
        normalize the probabilities by adding them -> DENOMINATOR
        numerator divided by denominator = fractional count for that analysis

    thus every time qikmighhaghmeng appears in the corpus:
        qikmigh  += 0.077
        ghhagh   += 0.077
        [Rel.Sg] += 0.077
        qikmighhagh += 0.23 + 0.23 + 0.23 + 0.23
        [Abl_Mod.4DuPoss.Pl] += 0.23
        ...

    Returns:
      * probfrac_w2a:     a dict where each key is a word mapped to
                          a list of analyses and the number of
                          derivational morphemes in each analysis.
      * zipf_dist:        a dict where each key is a morpheme and
                          each value is the fractional count of that
                          morpheme.
                          Sorting this dict by value returns the Zipfian
                          distribution.
      * deriv_count_dist: a dict where each key is the number of
                          derivational morphemes and each value is
                          the fractional count of words with that many
                          derivational morphemes.

    '''
    probfrac_w2a        = word2analyses
    morpheme_dist       = {}
    deriv_count_dist    = {}

    # get probabilities that a word contains N morphemes, N derivational morphemes
    morpheme_count_dist = {}
    derivational_count_dist    = {}

    # get fractional counts of the total number of times a word contains N morphemes, N derivational morphemes
    for word in word2analyses:

        # ignore punctuation
        if word and any(char.isalpha() for char in word):
            analyses = word2analyses[word]["analyses"]
            deriv_counts = word2analyses[word]["num deriv"]

            num_analyses = len(analyses)

            for analysis in analyses:
                num_morphemes = analysis.count("^") + 1

                if num_morphemes in morpheme_count_dist:
                    morpheme_count_dist[num_morphemes] += 1/num_analyses
                else:
                    morpheme_count_dist[num_morphemes] = 1/num_analyses

            for deriv_count in deriv_counts:
                if deriv_count in deriv_count_dist:
                    derivational_count_dist[deriv_count] += 1/num_analyses
                else:
                    derivational_count_dist[deriv_count] = 1/num_analyses

    # calculate aforementioned probabilities
    morpheme_count_probabilities = {}
    deriv_count_probabilities    = {}

    morpheme_total = sum(morpheme_count_dist.values())
    deriv_total    = sum(derivational_count_dist.values())

    for num_morphemes in morpheme_count_dist:
        morpheme_count_probabilities[num_morphemes] = morpheme_count_dist[num_morphemes] / morpheme_total

    for num_deriv in derivational_count_dist:
        deriv_count_probabilities[num_deriv] = derivational_count_dist[num_deriv] / deriv_total


    # now get the fractional counts of *each morpheme* based on the probability of a word containing N morphemes,
    # N derivational morphemes
    for word in word2analyses:

        # ignore punctuation
        if word and any(char.isalpha() for char in word):
            analyses = word2analyses[word]["analyses"]
            deriv_counts = word2analyses[word]["num deriv"]

            num_analyses = len(analyses)

            # calculate the denominators
            morpheme_denominator = 0
            for analysis in analyses:
                morphemes = analysis.split("^")
                num_morphemes = len(morphemes)

                morpheme_denominator += morpheme_count_probabilities[num_morphemes]

            deriv_denominator    = 0
            for num_deriv in deriv_counts:
                deriv_denominator += deriv_count_probabilities[num_deriv]

            # now calculate the numerator, divide, and update 'morpheme_dist'
            for analysis in analyses:
                morphemes = analysis.split("^")
                num_morphemes = len(morphemes)

                for morpheme in morphemes:
                    if morpheme in morpheme_dist:
                        morpheme_dist[morpheme] += morpheme_count_probabilities[num_morphemes] / morpheme_denominator
                    else:
                        morpheme_dist[morpheme] = morpheme_count_probabilities[num_morphemes] / morpheme_denominator

            # do the same for 'deriv_count_dist'
            for num_deriv in deriv_counts:
                if num_deriv in deriv_count_dist:
                    deriv_count_dist[num_deriv] += deriv_count_probabilities[num_deriv] / deriv_denominator
                else:
                    deriv_count_dist[num_deriv] = deriv_count_probabilities[num_deriv] / deriv_denominator

    return probfrac_w2a, morpheme_dist, deriv_count_dist


def get_zero_derivation_counts(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: dict

    Counts the number of times:
        * an emotional root behaves as a verb root
        * a postural root behaves as a verb root
        * a numeral behaves as a noun root
        * a demonstrative adverb root behaves as a noun root

    '''
    count = {"EMO":0,
             "POS":0,
             "NUM":0,
             "DEM ADV":0
            }

    for word in word2analyses:
        analyses = word2analyses[word]["analyses"]

        for analysis in analyses:
            if "(EMO)" in analysis and "(EMO→" not in analysis:
                count["EMO"] += 1
            elif "(POS)" in analysis and "(POS→" not in analysis:
                count["POS"] += 1
            elif "(NUM)" in analysis and "(NUM→" not in analysis:
                count["NUM"] += 1
            elif "(DEM.ADV)" in analysis and "(DEM→" not in analysis:
                count["DEM ADV"] += 1

    return count


def get_enclitic_counts(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: dict

    Creates a dict where each key is the number of enclitics and each
    value is the number of words with that many enclitics.

    '''
    count = {}

    for word in word2analyses:
        analyses = word2analyses[word]["analyses"]

        for analysis in analyses:
            num_enclitic = analysis.count("=")

            if num_enclitic in count:
                count[num_enclitic] += 1
            else:
                count[num_enclitic] = 1

    return count


def get_deriv_counts_after_stem_type(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    :return: dict

    Counts the number of times:
        * a noun root
        * a verb root
        * an emotional root
        * a postural root
        * a numeral
        * a positional
        * an anaphoric demonstrative
        * demonstrative adverb root
    is followed by 0-N derivational morphemes

    '''
    count = {"noun":{},
             "verb":{},
             "emotional root" :{},
             "postural root"  :{},
             "numeral"        :{},
             "positional"     :{},
             "dem anaphor"    :{},
             "dem adverb root":{}
            }

    for word in word2analyses:
        analyses  = word2analyses[word]["analyses"]
        num_deriv = word2analyses[word]["num deriv"]

        for analysis in analyses:
            key = ""  # key naming scheme simplifies code in 'sampling_2B()' method
            subdict = ""

            if "(N)" in analysis: 
                key = "N" + str(num_deriv)
                subdict = "noun"
            elif "(V)" in analysis: 
                key = "V" + str(num_deriv)
                subdict = "verb"
            elif "(EMO)" in analysis: 
                key = "E" + str(num_deriv)
                subdict = "emotional root"
            elif "(POS)" in analysis: 
                key = "P" + str(num_deriv)
                subdict = "postural root"
            elif "(NUM)" in analysis: 
                key = "R" + str(num_deriv) # R for roman
                subdict = "numeral"
            elif "(AREA)" in analysis: 
                key = "S" + str(num_deriv) # S for space
                subdict = "positional"
            elif "[Anaphor]" in analysis: 
                key = "F" + str(num_deriv) # F for -ph-
                subdict = "dem anaphor"
            elif "(DEM.ADV)" in analysis: 
                key = "D" + str(num_deriv) # D for demonstrative
                subdict = "dem adverb root"

            if key:
                if key in count[subdict]:
                    count[subdict][key] += 1
                else:
                    count[subdict][key] = 1

    return count


def get_pos_counts_after_each_pos(word2analyses):
    '''
    :param word2analyses: dictionary of the form
                          {word: {'analyses' : [analysis, analysis, analysis, etc.],
                                 'num deriv': [#, #, #, etc.]}
                          }
    :type  word2analyses: nested dict

    Counts the number of times each tag follows another tag,
      e.g. {(N): { (N→N): 23,
                   (N→V): 84,
                   etc.}
           }
           means an NN morpheme follows an N root 23 times,
                 an NV morpheme follows an N root 84 times, etc.
    
    '''
    count = {"enclitic":{}}

    for word in word2analyses:
        analyses  = word2analyses[word]["analyses"]

        for analysis in analyses:
            tags = re.findall(r'\([A-Z→.]+\)', analysis)

            if tags:
                previous_tag = ""

                for idx, tag in enumerate(tags):
                    # if only one tag
                    if len(tags) == 1:
                        if tag not in count:
                            count[tag] = {"Infl": 1}
                        else:
                            if "Infl" not in count[tag]:
                                count[tag]["Infl"] = 1
                            else:
                                count[tag]["Infl"] += 1

                    # otherwise first tag
                    elif idx == 0:
                        if tag not in count:
                            count[tag] = {}

                    # last tag
                    elif idx == len(tags)-1:
                        if tag not in count:
                            count[tag] = {}

                        if "Infl" not in count[tag]:
                            count[tag]["Infl"] = 1
                        else:
                            count[tag]["Infl"] += 1

                    # middle tags 
                    else:
                        if tag not in count:
                            count[tag] = {}

                        if tag not in count[previous_tag]:
                            count[previous_tag][tag] = 1
                        else:
                            count[previous_tag][tag] += 1

                    previous_tag = tag

            # also count what tags/parts of speech enclitics follow
            if analysis != "+?":
    
                # determine the previous tag
                if "[" in analysis:
                    previous_tag = "[" + analysis.rsplit("[", 1)[1]
                elif "(" in analysis:
                    previous_tag = "(" + analysis.rsplit("(", 1)[1]
    
                # rename 'previous_tag' to simplify code in 'sampling_3A()' in sampling_methods.py
                if "DEM.ADV" in previous_tag:
                    previous_tag = "DEM.ADV"
                elif "DEM.PRO" in previous_tag:
                    previous_tag = "DEM.PRO"
                elif "NUM" in previous_tag:
                    previous_tag = "NUM"
                elif "(PRO" in previous_tag:
                    previous_tag = "PRO"
                elif "PTCL" in previous_tag:
                    previous_tag = "PTCL"
                elif "WH" in previous_tag:
                    previous_tag = "WH"
                elif "XCLM" in previous_tag:
                    previous_tag = "XCLM"
                elif "Abs" in previous_tag or "Rel" in previous_tag or \
                     "Abl_Mod" in previous_tag or "Loc" in previous_tag or \
                     "All" in previous_tag or "Prl" in previous_tag or "Equ" in previous_tag:
                    previous_tag = "N"
                elif "Intr" in previous_tag or "Trns" in previous_tag or "Fear" in previous_tag:
                    previous_tag = "V"
                elif "Sg" in previous_tag or "Pl" in previous_tag or "Du" in previous_tag:
                    previous_tag = "QUANTQUAL"
    
                # NOTE: printing 'count["enclitic"]' shows quite a few errors in the analyses
                #       used to generate 'word2analyses.json', not sure how that happened
                if previous_tag not in count["enclitic"]:
                    count["enclitic"][previous_tag] = {"YES":0, "NO":0}
    
                if "=" in analysis:
                    count["enclitic"][previous_tag]["YES"] += 1
    
                    # don't forget to count the number of enclitics that follow enclitics
                    num_enclitics = analysis.count("=")
    
                    if "=" not in count["enclitic"]:
                        count["enclitic"]["="] = {"YES":0, "NO":0}
    
                    if num_enclitics > 1:
                        count["enclitic"]["="]["YES"] += (num_enclitics - 1) 
                    else:
                        count["enclitic"]["="]["NO"] += 1 
                else:
                    count["enclitic"][previous_tag]["NO"] += 1

    # rename keys to simplify code in 'sampling_3A()' in 'sampling_methods.py'
    count["noun"] = count.pop("(N)")
    count["verb"] = count.pop("(V)")
    count["particle"] = count.pop("(PTCL)")
    count["emotional root"] = count.pop("(EMO)")
    count["postural root"] = count.pop("(POS)")
    count["numeral"] = count.pop("(NUM)")
    count["positional"] = count.pop("(AREA)")
    count["quantqual"] = count.pop("(QUANTQUAL)")
    count["dem adverb root"] = count.pop("(DEM.ADV)")
    count["dem pronoun root"] = count.pop("(DEM.PRO)")

    return count 


###

def get_avg_num_morphemes_per_word(analyses):
    '''
    :param analyses: self-explanatory
    :type  analyses: pandas dataframe

    :return: float

    Counts the average number of morphemes per word.

    '''
    # get num of analyses
    num_analyses = len(analyses.index)

    # get morpheme boundary (^) count
    boundary_count = analyses.str.count("\^").sum()

    # num morphemes per analysis is ^ count + 1
    morpheme_total = boundary_count + num_analyses

    # return average
    return morpheme_total/num_analyses
