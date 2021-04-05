# -*- coding: utf-8 -*-
'''
:author: Emily Chen
:date:   2021

code repeats because i'm lazy and don't
feel like refactoring.

'''
import random
import re
import pprint
import sys


def make_partofspeech_dictionary_count(d):
    '''
    :param d: corpus counts (for all morphemes)
    :type  d: dict

    :return: dicts

    Creates dictionary counts for each part-of-speech
    tag based on the given corpus.

    '''
    partofspeech_count = {"noun"          :0,
                          "verb"          :0,
                          "particle"      :0,
                          "emotional root":0,
                          "postural root" :0,
                          "numeral"       :0,
                          "positional"    :0,
                          "exclamation"   :0,
                          "wh word" :0,
                          "quantqual"     :0,
                          "pronoun"       :0,
                          "vocative"      :0,
                          "demonstrative" :0,
                          "dem anaphor"   :0,
                          "dem adverb root"  :0,
                          "dem pronoun root" :0
                         }

    for key in d:
        if key.endswith("(N)"):
            partofspeech_count["noun"] += 1 
        elif key.endswith("(V)"):
            partofspeech_count["verb"] += 1 
        elif "(PTCL)" in key:
            partofspeech_count["particle"] += 1 
        elif "(EMO)" in key:
            partofspeech_count["emotional root"] += 1 
        elif "(POS)" in key or "(POS→QUANTQUAL)" in key:
            partofspeech_count["postural root"] += 1 
        elif "(NUM)" in key:
            partofspeech_count["numeral"] += 1 
        elif "(AREA)" in key:
            partofspeech_count["positional"] += 1 
        elif "(XCLM)" in key:
            partofspeech_count["exclamation"] += 1 
        elif "(WH)" in key:
            partofspeech_count["wh word"] += 1 
        elif "(QUANTQUAL)" in key:
            partofspeech_count["quantqual"] += 1 
        elif "(PRO" in key:
            partofspeech_count["pronoun"] += 1 
        elif "(VOC" in key:
            partofspeech_count["vocative"] += 1 
        elif key.startswith("[Anaphor]"):
            partofspeech_count["dem anaphor"] += 1 
        elif key.endswith("(DEM.ADV)"):
            partofspeech_count["dem adverb root"] += 1 
        elif key.endswith("(DEM.PRO)"):
            partofspeech_count["dem pronoun root"] += 1 
        elif "(DEM" in key:
            partofspeech_count["demonstrative"] += 1 

    return partofspeech_count 


def make_dictionary_counts(d):
    '''
    :param d: corpus counts (for all morphemes)
    :type  d: dict

    # TODO: add this parameter back in when hallucinating data?
    :param zero_deriv: corpus counts for all zero derivations
                       of non-N and non-V roots (EMO, POS, etc.)
    :type  zero_deriv: dict

    :return: tuple of dicts 

    Creates dictionary counts for each type of morpheme,
    based on the given corpus.

    '''
    noun_roots = {}
    verb_roots = {}
    particles  = {}
    emo_roots  = {}
    pos_roots  = {}
    num_roots  = {}
    area_roots = {}
    xclm_roots = {}
    wh_roots   = {}
    qq_roots   = {}
    pronouns   = {}
    vocatives  = {}
    dem_anaphors   = {}
    dem_adv_roots  = {}
    dem_pro_roots  = {}
    demonstratives = {}

    noun_deriv = {}
    verb_deriv = {}
    emo_deriv  = {}
    pos_deriv  = {}
    num_deriv  = {}
    dem_deriv  = {}

    noun_infl = {}
    verb_infl = {}
    qq_infl   = {}

    enclitics = {}

    for key in d:
        # count roots
        if "(N)" in key:
            noun_roots[key] = d[key]
        elif "(V)" in key:
            verb_roots[key] = d[key]
        elif "(PTCL)" in key:
            particles[key] = d[key]
        elif "(EMO)" in key:
            emo_roots[key] = d[key]
        elif "(POS)" in key or "(POS→QUANTQUAL)" in key:
            pos_roots[key] = d[key]
        elif "(NUM)" in key:
            num_roots[key] = d[key]
        elif "(AREA)" in key:
            area_roots[key] = d[key]
        elif "(XCLM)" in key:
            xclm_roots[key] = d[key]
        elif "(WH)" in key:
            wh_roots[key] = d[key]
        elif "(QUANTQUAL)" in key:
            qq_roots[key] = d[key]
        elif "(PRO" in key:
            pronouns[key] = d[key]
        elif "(VOC" in key:
            vocatives[key] = d[key]
        elif key.startswith("[Anaphor]"):
            dem_anaphors[key] = d[key]
        elif key.endswith("(DEM.ADV)"):
            dem_adv_roots[key] = d[key]
        elif key.endswith("(DEM.PRO)"):
            dem_pro_roots[key] = d[key]
        elif key.startswith("(DEM"):
            demonstratives[key] = d[key]
        # count derivational morphemes
        elif "(N→" in key:
            noun_deriv[key] = d[key]
        elif "(V→" in key or "(CmpdVbl)" in key:
            verb_deriv[key] = d[key]
        elif "(EMO→" in key:
            emo_deriv[key] = d[key]
        elif "(POS→STATIVE)" in key or "(POS→ACTIVE)" in key:
            pos_deriv[key] = d[key]
        elif "(NUM→" in key:
            num_deriv[key] = d[key]
        elif "(DEM→" in key:
            dem_deriv[key] = d[key]
        # count inflectional morphemes
        elif "Abs" in key or "Rel" in key or "Abl_Mod" in key or \
             "Loc" in key or "All" in key or "Prl" in key or "Equ" in key:
            if "DEM" not in key and "PRO" not in key and "WH" not in key:
                noun_infl[key] = d[key]
        elif "Intr" in key or "Trns" in key or "Fear" in key:
            verb_infl[key] = d[key]
        elif "Sg" in key or "Pl" in key or "Du" in key:
            if "VOC" not in key:
                qq_infl[key] = d[key]
        elif "=" in key:
            enclitics[key] = d[key]

    '''
    # TODO: uncomment this when hallucinating data
    if zero_deriv:
        # permit EMO and POS roots to zero derive to V
        emo_deriv["NULL(EMO→V)"] = zero_deriv["EMO"]
        pos_deriv["NULL(POS→V)"] = zero_deriv["POS"]

        # permit NUM and DEM.ADV roots to zero derive to N
        num_deriv["NULL(NUM→N)"] = zero_deriv["NUM"]
        dem_deriv["NULL(DEM→N)"] = zero_deriv["DEM ADV"]
    '''
    return noun_roots, verb_roots, particles, \
           emo_roots, pos_roots, \
           num_roots, area_roots, \
           xclm_roots, wh_roots, qq_roots, \
           pronouns, vocatives, \
           dem_anaphors, dem_adv_roots, dem_pro_roots, demonstratives, \
           noun_deriv, verb_deriv, \
           emo_deriv, pos_deriv, \
           num_deriv, dem_deriv, \
           noun_infl, verb_infl, qq_infl, \
           enclitics


def make_prior_probability_dict(d):
    '''
    :param d: corpus counts (for a particular
              type of morpheme)
    :type  d: dict

    :return: dict 

    Creates a prior probability dictionary, i.e.
    the dartboard, for the given morpheme type.

    '''
    probability_dict = {}

    total = sum(d.values())
    for key in d:
        key_probability = d[key]/total
        probability_dict[key] = key_probability

    return probability_dict


def make_tag_count_dict(d):
    '''
    :param d: corpus counts (for all morphemes)
    :type  d: dict

    :return: dict

    Creates a dictionary where each key is a morpheme
    and its corresponding value is a nested dict which
    counts the number of times a morpheme is of a certain
    type,
    e.g. { laag: { (N): 84,
                   (V): 234
                 }
         }
         which means laag- was seen 84 times as a noun root
         in the corpus and 234 times as a verb root.

    '''
    tag_count = {}

    for key in d:
        if "(" in key:
            morpheme = key.rsplit("(", 1)[0]
            tag      = "(" + key.rsplit("(", 1)[1]

            # strip the morpheme to its bare minimum, i.e. no symbols
            #stripped = morpheme.replace("=","").\
            #                    replace("~sf","").replace("~f","").\
            #                    replace("-w","").replace("+","").\
            #                    replace("@","").replace("–","").\
            #                    replace("~","").replace(":","")

            # 
            if morpheme in tag_count:
                tag_count[morpheme][tag] = d[key]
            else:
                tag_count[morpheme] = {}
                tag_count[morpheme][tag] = d[key]

    return tag_count


def make_all_probability_dicts(morpheme_dist):
    '''
    :param morpheme_dist: counts for all of the morphemes 
    :type  morpheme_dist: dict

    :return: list of dicts

    Creates the probability dictionaries, i.e. the dartboards, for all types of morphemes.
    NOTE: 'dist' here just means 'counts'

    '''
    # create dictionary counts for each type of morpheme
    noun_root_dist, verb_root_dist, particle_dist, \
    emo_root_dist, pos_root_dist, \
    num_root_dist, area_root_dist, \
    xclm_root_dist, wh_root_dist, qq_root_dist, \
    pronoun_dist, vocative_dist, \
    dem_anaphor_dist, dem_adv_dist, dem_pro_dist, demonstrative_dist, \
    noun_deriv_dist, verb_deriv_dist, \
    emo_deriv_dist, pos_deriv_dist, \
    num_deriv_dist, dem_deriv_dist, \
    noun_infl_dist, verb_infl_dist, qq_infl_dist, \
    enclitic_dist = make_dictionary_counts(morpheme_dist)

    # simplifies the code
    all_dist_dicts = [noun_root_dist, verb_root_dist, particle_dist, \
                      emo_root_dist, pos_root_dist, \
                      num_root_dist, area_root_dist, \
                      xclm_root_dist, wh_root_dist, qq_root_dist, \
                      pronoun_dist, vocative_dist, \
                      dem_anaphor_dist, dem_adv_dist, dem_pro_dist, demonstrative_dist, \
                      noun_deriv_dist, verb_deriv_dist, \
                      emo_deriv_dist, pos_deriv_dist, \
                      num_deriv_dist, dem_deriv_dist, \
                      noun_infl_dist, verb_infl_dist, qq_infl_dist, \
                      enclitic_dist]

    # create probability dictionaries for each type of morpheme using bayes' theorem: P(A|B) = P(B|A)*P(A) / P(B)
    #   e.g. for each noun root:
    #
    #        P(noun root R | root type NOUN) = P(root type NOUN | root R)*P(root R) / P(root type NOUN)
    #
    #        where P(root type NOUN | root R) = (# words with root R of root type NOUN) / (# words with root R)
    #                  NUMERATOR:   num words where the root is a noun root and that root is this particular root 
    #                  DENOMINATOR: num words where the root is this particular root 
    #
    #              P(root R) = (# words with root R) / (total # words)
    #                  NUMERATOR:   num words where the root is this particular root 
    #                  DENOMINATOR: total number of words in the corpus 
    #
    #              P(root type NOUN) = (# words with root type NOUN) / (total # words)
    #                  NUMERATOR:   num words where the root is a noun root 
    #                  DENOMINATOR: total number of words in the corpus 
    #
    #        therefore P(noun root R | root type NOUN) = P(root type NOUN | root R)*(# words with root R) / (# words with root type NOUN)
    
    # make a type count dictionary to facilitate calculation of P(B|A)
    tag_count_dictionary = make_tag_count_dict(morpheme_dist)

    all_probability_dicts = []

    for d in all_dist_dicts:
        
        probability_dict = {} # set up the corresponding probability dictionary

        # calculate the relevant probability for each key
        # e.g. for 'noun_root_dist', calculates the probability of each noun root (given the root type is a noun)
        for key in d:
            if "(" in key:
                morpheme = key.rsplit("(", 1)[0]

                prob_A = sum(tag_count_dictionary[morpheme].values())
                prob_B  = sum(d.values())
    
                numerator = d[key]
                denominator = prob_A
                prob_BA = numerator / denominator
            else:
                prob_A  = d[key]
                prob_B  = sum(d.values())
                prob_BA = 1

            prob_AB = (prob_BA * prob_A)/prob_B
            probability_dict[key] = prob_AB

        all_probability_dicts.append(probability_dict)

    # sanity checks
    if len(all_dist_dicts) != len(all_probability_dicts):
        sys.exit("ABORTING: number of probability dictionaries doesn't match the number of dictionaries containing counts")

    for idx, d in enumerate(all_probability_dicts):
        if len(d.keys()) > 0:
            if int(round(sum(d.values()))) != 1:
                sys.exit("ABORT ABORT: conditional probabilities don't add up to 1 D:")

    return all_probability_dicts


def generate_samples(sample_num, sampling_method, all_params):
    '''
    :param sample_num:      number of samples to create
    :type  sample_num:      int
    :param sampling_method: self-explanatory 
    :type  sampling_method: str
    :param all_params:      parameters required by the sampling methods 
    :type  all_params:      list

    Wrapper function for calling the sampling methods.

    '''
    samples = []

    morpheme_dist, deriv_count_dist, enclitic_count_dist, deriv_count_after_stem_dist = [parameter for parameter in all_params]

    if sampling_method == "1A":
        samples = sampling_1A(sample_num, morpheme_dist, deriv_count_dist)
    elif sampling_method == "2A":
        samples = sampling_2A(sample_num, morpheme_dist, deriv_count_dist, enclitic_count_dist)
    elif sampling_method == "2B":
        samples = sampling_2B(sample_num, enclitic_count_dist, deriv_count_after_stem_dist)

    return samples


def sampling_1A(sample_num, morpheme_dist, deriv_count_dist):
    '''
    :param sample_num:        number of samples to create
    :type  sample_num:        int
    :param morpheme_dist:     counts of all morphemes
    :type  morpheme_dist:     dict
    :param deriv_count_dist:  counts of the number of words with
                              N derivational morphemes
    :type  deriv_count_dist:  dict

    :return: list

    Samples using Variation 1A: Roots and the number of derivational
    morphemes to include are sampled using a uniform distribution.
    All other considerations are conditionally dependent on the
    type of the preceding morpheme using P(A|B)=P(B|A)*P(A)/P(B).
    But we make the simplifying assumption that P(B|A) = 0 or 1.

    '''
    # make all of the relevant probability dictionaries
    partofspeech_counts = make_partofspeech_dictionary_count(morpheme_dist)
    partofspeech_count_probabilities = make_prior_probability_dict(partofspeech_counts)

    deriv_count_probabilities = make_prior_probability_dict(deriv_count_dist)

    noun_root_probabilities, verb_root_probabilities, particle_probabilities, \
    emo_root_probabilities, pos_root_probabilities, \
    num_root_probabilities, area_root_probabilities, \
    xclm_root_probabilities, wh_root_probabilities, qq_root_probabilities, \
    pronoun_probabilities, vocative_probabilities, \
    dem_anaphor_probabilities, dem_adv_probabilities, dem_pro_probabilities, demonstrative_probabilities, \
    noun_deriv_probabilities, verb_deriv_probabilities, \
    emo_deriv_probabilities, pos_deriv_probabilities, \
    num_deriv_probabilities, dem_deriv_probabilities, \
    noun_infl_probabilities, verb_infl_probabilities, qq_infl_probabilities, \
    enclitic_probabilities = [d for d in make_all_probability_dicts(morpheme_dist)]

    samples = []
    counter = 0
    while counter < sample_num:
        if counter % 100000 == 0:
            print("sampling " + str(counter) + " out of " + str(sample_num) + "...")

        sample = []

        # sample the part-of-speech tag
        if partofspeech_count_probabilities:
            partofspeech = random.choice(list(partofspeech_count_probabilities.keys()))

        # sample the number of derivational morphemes to include
        if partofspeech == "particle" or partofspeech == "exclamation" or \
           partofspeech == "wh word" or partofspeech == "quantqual" or \
           partofspeech == "pronoun" or partofspeech == "vocative" or \
           partofspeech == "demonstrative" or partofspeech == "dem pronoun root":
            num_deriv = 0
        else:
            if deriv_count_probabilities:
                num_deriv = random.choice(list(deriv_count_probabilities.keys()))

        # sample a root 
        root = ""
        if partofspeech == "noun":
            if noun_root_probabilities:
                root = random.choice(list(noun_root_probabilities.keys()))
        elif partofspeech == "verb":
            if verb_root_probabilities:
                root = random.choice(list(verb_root_probabilities.keys()))
        elif partofspeech == "particle":
            if particle_probabilities:
                root = random.choice(list(particle_probabilities.keys()))
        elif partofspeech == "emotional root":
            if emo_root_probabilities:
                root = random.choice(list(emo_root_probabilities.keys()))
        elif partofspeech == "postural root":
            if pos_root_probabilities:
                root = random.choice(list(pos_root_probabilities.keys()))
        elif partofspeech == "numeral":
            if num_root_probabilities:
                root = random.choice(list(num_root_probabilities.keys()))
        elif partofspeech == "positional":
            if area_root_probabilities:
                root = random.choice(list(area_root_probabilities.keys()))
        elif partofspeech == "exclamation":
            if xclm_root_probabilities:
                root = random.choice(list(xclm_root_probabilities.keys()))
        elif partofspeech == "wh word":
            if wh_root_probabilities:
                root = random.choice(list(wh_root_probabilities.keys()))
        elif partofspeech == "quantqual":
            if qq_root_probabilities:
                root = random.choice(list(qq_root_probabilities.keys()))
        elif partofspeech == "pronoun":
            if pronoun_probabilities:
                root = random.choice(list(pronoun_probabilities.keys()))
        elif partofspeech == "vocative":
            if vocative_probabilities:
                root = random.choice(list(vocative_probabilities.keys()))
        elif partofspeech == "demonstrative":
            if demonstrative_probabilities:
                root = random.choice(list(demonstrative_probabilities.keys()))
        elif partofspeech == "dem anaphor":
            if dem_anaphor_probabilities:
                root = random.choice(list(dem_anaphor_probabilities.keys()))
        elif partofspeech == "dem adverb root":
            if dem_adv_probabilities:
                root = random.choice(list(dem_adv_probabilities.keys()))
        elif partofspeech == "dem pronoun root":
            if dem_pro_probabilities:
                root = random.choice(list(dem_pro_probabilities.keys()))

        if root:
            sample.append(root)

            # sample morpheme to follow EMO, POS, NUM, DEM.ADV root
            morpheme = ""
            if partofspeech == "emotional root":
                if emo_deriv_probabilities:
                    morpheme = random.choice(list(emo_deriv_probabilities.keys()))
                    sample.append("^" + morpheme)
            elif partofspeech == "postural root":
                if pos_deriv_probabilities:
                    if "(POS→QUANTQUAL)" in sample[-1]:
                        num_deriv = 0
                    else:
                        morpheme = random.choice(list(pos_deriv_probabilities.keys()))
                        sample.append("^" + morpheme)
            elif partofspeech == "numeral":
                if num_deriv_probabilities:
                    morpheme = random.choice(list(num_deriv_probabilities.keys()))
                    sample.append("^" + morpheme)
            elif partofspeech == "dem adverb root":
                if dem_deriv_probabilities:
                    morpheme = random.choice(list(dem_deriv_probabilities.keys()))
                    sample.append("^" + morpheme)

            # sample the derivational morphemes
            if num_deriv > 0: 
                for m in range(num_deriv):
                    if ("N)" in sample[-1] or "(AREA)" in sample[-1]) and "DEM" not in sample[-1]:
                        if noun_deriv_probabilities:
                            dm = random.choice(list(noun_deriv_probabilities.keys()))
                            sample.append("^" + dm)
                    elif "V)" in sample[-1] and "DEM" not in sample[-1]:
                        if verb_deriv_probabilities:
                            dm = random.choice(list(verb_deriv_probabilities.keys()))
                            sample.append("^" + dm)

            # sample an inflectional morpheme
            if "N)" in sample[-1] or "(AREA)" in sample[-1] or "(DEM.PRO)" in sample[-1]:
                if noun_infl_probabilities:
                    im = random.choice(list(noun_infl_probabilities.keys()))
                    sample.append("^" + im)
            elif ("V)" in sample[-1] and "DEM" not in sample[-1]) or \
                  "(CmpdVbl)" in sample[-1] or "STATIVE)" in sample[-1] or "ACTIVE)" in sample[-1]:
                if verb_infl_probabilities:
                    im = random.choice(list(verb_infl_probabilities.keys()))
                    sample.append("^" + im)
            elif "QUANTQUAL)" in sample[-1]:
                if qq_infl_probabilities:
                    im = random.choice(list(qq_infl_probabilities.keys()))
                    sample.append("^" + im)
 
            # cleanup: remove explicit NULL morphemes (from zero derivations)
            cleaned_sample = [morpheme for morpheme in sample if "NULL" not in morpheme]

            samples.append(''.join(cleaned_sample))
            counter += 1

    return samples



def sampling_2A(sample_num, morpheme_dist, deriv_count_dist, enclitic_count_dist):
    '''
    :param sample_num:          number of samples to create
    :type  sample_num:          int
    :param morpheme_dist:       counts of all morphemes
    :type  morpheme_dist:       dict
    :param deriv_count_dist:    counts of the number of words with
                                N derivational morphemes
    :type  deriv_count_dist:    dict
    :param enclitic_count_dist: counts of the number of words with N enclitics 
                               
    :type  enclitic_count_dist: dict

    :return: list

    Samples using Variation 2A: All morphemes and number of
    morphemes to include are sampled using a Zipfian distribution,
    and are conditionally dependent on the type of the preceding stem.

    '''
    # make all of the relevant probability dictionaries
    partofspeech_counts = make_partofspeech_dictionary_count(morpheme_dist)
    partofspeech_count_probabilities = make_prior_probability_dict(partofspeech_counts)

    deriv_count_probabilities = make_prior_probability_dict(deriv_count_dist)

    enclitic_count_probabilities = make_prior_probability_dict(enclitic_count_dist)

    noun_root_probabilities, verb_root_probabilities, particle_probabilities, \
    emo_root_probabilities, pos_root_probabilities, \
    num_root_probabilities, area_root_probabilities, \
    xclm_root_probabilities, wh_root_probabilities, qq_root_probabilities, \
    pronoun_probabilities, vocative_probabilities, \
    dem_anaphor_probabilities, dem_adv_probabilities, dem_pro_probabilities, demonstrative_probabilities, \
    noun_deriv_probabilities, verb_deriv_probabilities, \
    emo_deriv_probabilities, pos_deriv_probabilities, \
    num_deriv_probabilities, dem_deriv_probabilities, \
    noun_infl_probabilities, verb_infl_probabilities, qq_infl_probabilities, \
    enclitic_probabilities = [d for d in make_all_probability_dicts(morpheme_dist)]

    samples = []
    counter = 0
    while counter < sample_num:
        if counter % 100000 == 0:
            print("sampling " + str(counter) + " out of " + str(sample_num) + "...")

        sample = []

        # sample the part-of-speech tag
        partofspeech = ""
        total = 0
        sample_n = random.random()
        for part_of_speech in partofspeech_count_probabilities:
            total += partofspeech_count_probabilities[part_of_speech]
            if sample_n < total:
                partofspeech = part_of_speech
                break

        # sample the number of derivational morphemes
        if partofspeech == "particle" or partofspeech == "exclamation" or \
           partofspeech == "wh word" or partofspeech == "quantqual" or \
           partofspeech == "pronoun" or partofspeech == "vocative" or \
           partofspeech == "demonstrative" or partofspeech == "dem pronoun root":
            num_deriv = 0
        else:
            num_deriv = 0
            total = 0
            sample_n = random.random()
            for deriv_count in deriv_count_probabilities: 
                total += deriv_count_probabilities[deriv_count]
                if sample_n < total:
                    num_deriv = deriv_count
                    break

        # sample a root 
        root  = ""
        total = 0
        sample_n = random.random()
        if partofspeech == "noun":
            for root in noun_root_probabilities: 
                total += noun_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "verb":
            for root in verb_root_probabilities: 
                total += verb_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "particle":
            for root in particle_probabilities: 
                total += particle_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "emotional root":
            for root in emo_root_probabilities: 
                total += emo_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "postural root":
            for root in pos_root_probabilities: 
                total += pos_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "numeral":
            for root in num_root_probabilities: 
                total += num_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "positional":
            for root in area_root_probabilities: 
                total += area_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "exclamation":
            for root in xclm_root_probabilities: 
                total += xclm_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "wh word":
            for root in wh_root_probabilities: 
                total += wh_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "quantqual":
            for root in qq_root_probabilities: 
                total += qq_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "pronoun":
            for root in pronoun_probabilities: 
                total += pronoun_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "vocative":
            for root in vocative_probabilities: 
                total += vocative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "demonstrative":
            for root in demonstrative_probabilities: 
                total += demonstrative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem anaphor":
            for root in dem_anaphor_probabilities: 
                total += dem_anaphor_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem adverb root":
            for root in dem_adv_probabilities: 
                total += dem_adv_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem pronoun root":
            for root in dem_pro_probabilities: 
                total += dem_pro_probabilities[root]
                if sample_n < total:
                    break

        if root:
            sample.append(root)

            # sample the morpheme to follow EMO, POS, NUM, DEM.ADV root
            total = 0
            sample_n = random.random()
            if partofspeech == "emotional root":
                for morpheme in emo_deriv_probabilities:
                    total += emo_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv -= 1
                        sample.append("^" + morpheme)
                        break
            elif partofspeech == "postural root":
                if "(POS→QUANTQUAL)" in sample[-1]:
                    num_deriv = 0
                else:
                    for morpheme in pos_deriv_probabilities:
                        total += pos_deriv_probabilities[morpheme]
                        if sample_n < total:
                            if "NULL" in morpheme:
                                num_deriv -= 1
                            sample.append("^" + morpheme)
                            break
            elif partofspeech == "numeral":
                for morpheme in num_deriv_probabilities:
                    total += num_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv -= 1
                        sample.append("^" + morpheme)
                        break
            elif partofspeech == "dem adverb root":
                for morpheme in dem_deriv_probabilities:
                    total += dem_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv = 0
                        sample.append("^" + morpheme)
                        break
    
            # sample the derivational morphemes
            if num_deriv > 0: 
                for m in range(num_deriv):
                    if ("N)" in sample[-1] or "(AREA)" in sample[-1]) and \
                        "DEM" not in sample[-1]:
                        total = 0
                        sample_n = random.random()
                        for dm in noun_deriv_probabilities: 
                            total += noun_deriv_probabilities[dm]
                            if sample_n < total:
                                break
                        sample.append("^" + dm)
                    elif "V)" in sample[-1] and "DEM" not in sample[-1]:
                        total = 0
                        sample_n = random.random()
                        for dm in verb_deriv_probabilities: 
                            total += verb_deriv_probabilities[dm]
                            if sample_n < total:
                                break
                        sample.append("^" + dm)
    
            # sample the inflectional morpheme
            if "N)" in sample[-1] or "(AREA)" in sample[-1] or "(DEM.PRO)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in noun_infl_probabilities: 
                    total += noun_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break
            elif ("V)" in sample[-1] and "ADV)" not in sample[-1]) or \
                  "(CmpdVbl)" in sample[-1] or \
                  "STATIVE)" in sample[-1] or "ACTIVE)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in verb_infl_probabilities: 
                    total += verb_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break
            elif "QUANTQUAL)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in qq_infl_probabilities: 
                    total += qq_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break

            # sample the number of enclitics to include
            num_enclitic = 0
            total = 0
            sample_n = random.random()
            for enclitic_count in enclitic_count_probabilities: 
                total += enclitic_count_probabilities[enclitic_count]
                if sample_n < total:
                    num_enclitic = enclitic_count
                    break

            # sample the enclitic(s)
            if num_enclitic > 0:
                total = 0
                sample_n = random.random()
                for encl in enclitic_probabilities: 
                    total += enclitic_probabilities[encl]
                    if sample_n < total:
                        sample.append("^" + encl)
                        break
     
            # cleanup: remove explicit NULL morphemes (from zero derivations)
            cleaned_sample = [morpheme for morpheme in sample if "NULL" not in morpheme]
    
            samples.append(''.join(cleaned_sample))
            counter += 1

    return samples


def sampling_2B(sample_num, morpheme_dist, enclitic_count_dist, deriv_count_after_stem_dist):
    '''
    :param sample_num:                  number of samples to create
    :type  sample_num:                  int
    :param morpheme_dist:               counts of all morphemes
    :type  morpheme_dist:               dict
    :param enclitic_count_dist:         counts of the number of words with N enclitics
    :type  enclitic_count_dist:         dict
    :param deriv_count_after_stem_dist: counts of the number of words with N derivational morphemes
                                        following a particular stem
    :type  deriv_count_after_stem_dist: nested dict

    :return: list

    Samples using Variation 2B: This is identical to Variation 2A except
    the number of derivational morphemes to include is conditionally
    dependent on the type of the root.

    '''
    # make all of the relevant probability dictionaries
    partofspeech_counts = make_partofspeech_dictionary_count(morpheme_dist)
    partofspeech_count_probabilities = make_prior_probability_dict(partofspeech_counts)

    enclitic_count_probabilities = make_prior_probability_dict(enclitic_count_dist)

    noun_root_probabilities, verb_root_probabilities, particle_probabilities, \
    emo_root_probabilities, pos_root_probabilities, \
    num_root_probabilities, area_root_probabilities, \
    xclm_root_probabilities, wh_root_probabilities, qq_root_probabilities, \
    pronoun_probabilities, vocative_probabilities, \
    dem_anaphor_probabilities, dem_adv_probabilities, dem_pro_probabilities, demonstrative_probabilities, \
    noun_deriv_probabilities, verb_deriv_probabilities, \
    emo_deriv_probabilities, pos_deriv_probabilities, \
    num_deriv_probabilities, dem_deriv_probabilities, \
    noun_infl_probabilities, verb_infl_probabilities, qq_infl_probabilities, \
    enclitic_probabilities = [d for d in make_all_probability_dicts(morpheme_dist)]

    samples = []
    counter = 0 
    while counter < sample_num: 
        if counter % 100000 == 0:
            print("sampling " + str(counter) + " out of " + str(sample_num) + "...")

        sample = []

        # sample the part-of-speech tag
        partofspeech = ""
        total = 0
        sample_n = random.random()
        for part_of_speech in partofspeech_count_probabilities:
            total += partofspeech_count_probabilities[part_of_speech]
            if sample_n < total:
                partofspeech = part_of_speech
                break

        # sample the number of derivational morphemes to include
        num_deriv = 0
        if partofspeech != "particle" and partofspeech != "exclamation" and \
           partofspeech != "wh word" and partofspeech != "quantqual" and \
           partofspeech != "pronoun" and partofspeech != "vocative" and \
           partofspeech != "demonstrative" and partofspeech != "dem pronoun root":

            deriv_count_after_stem_probabilities = {}
            if partofspeech == "noun":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["noun"])
            elif partofspeech == "verb":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["verb"])
            elif partofspeech == "emotional root":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["emotional root"])
            elif partofspeech == "postural root":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["postural root"])
            elif partofspeech == "numeral":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["numeral"])
            elif partofspeech == "positional":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["positional"])
            elif partofspeech == "dem anaphor":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["dem anaphor"])
            elif partofspeech == "dem adverb root":
                deriv_count_after_stem_probabilities = make_prior_probability_dict(deriv_count_after_stem_dist["dem adverb root"])

            total = 0
            sample_n = random.random()
            for deriv_count in deriv_count_after_stem_probabilities: 
                total += subdict[deriv_count]
                if sample_n < total:
                    num_deriv = int(deriv_count[2])
                    break

        # sample a root 
        root  = ""
        total = 0
        sample_n = random.random()
        if partofspeech == "noun":
            for root in noun_root_probabilities: 
                total += noun_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "verb":
            for root in verb_root_probabilities: 
                total += verb_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "particle":
            for root in particle_probabilities: 
                total += particle_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "emotional root":
            for root in emo_root_probabilities: 
                total += emo_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "postural root":
            for root in pos_root_probabilities: 
                total += pos_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "numeral":
            for root in num_root_probabilities: 
                total += num_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "positional":
            for root in area_root_probabilities: 
                total += area_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "exclamation":
            for root in xclm_root_probabilities: 
                total += xclm_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "wh word":
            for root in wh_root_probabilities: 
                total += wh_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "quantqual":
            for root in qq_root_probabilities: 
                total += qq_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "pronoun":
            for root in pronoun_probabilities: 
                total += pronoun_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "vocative":
            for root in vocative_probabilities: 
                total += vocative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "demonstrative":
            for root in demonstrative_probabilities: 
                total += demonstrative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem anaphor":
            for root in dem_anaphor_probabilities: 
                total += dem_anaphor_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem adverb root":
            for root in dem_adv_probabilities: 
                total += dem_adv_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem pronoun root":
            for root in dem_pro_probabilities: 
                total += dem_pro_probabilities[root]
                if sample_n < total:
                    break

        if root:
            sample.append(root)

            # sample the morpheme to follow EMO, POS, NUM, DEM.ADV root
            total = 0
            sample_n = random.random()
            if partofspeech == "emotional root":
                for morpheme in emo_deriv_probabilities:
                    total += emo_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv -= 1
                        sample.append("^" + morpheme)
                        break
            elif partofspeech == "postural root":
                if "(POS→QUANTQUAL)" in sample[-1]:
                    num_deriv = 0
                else:
                    for morpheme in pos_deriv_probabilities:
                        total += pos_deriv_probabilities[morpheme]
                        if sample_n < total:
                            if "NULL" in morpheme:
                                num_deriv -= 1
                            sample.append("^" + morpheme)
                            break
            elif partofspeech == "numeral":
                for morpheme in num_deriv_probabilities:
                    total += num_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv -= 1
                        sample.append("^" + morpheme)
                        break
            elif partofspeech == "dem adverb root":
                for morpheme in dem_deriv_probabilities:
                    total += dem_deriv_probabilities[morpheme]
                    if sample_n < total:
                        if "NULL" in morpheme:
                            num_deriv = 0
                        sample.append("^" + morpheme)
                        break
    
            # sample the derivational morphemes
            if num_deriv > 0: 
                for m in range(num_deriv):
                    if ("N)" in sample[-1] or "(AREA)" in sample[-1]) and \
                        "DEM" not in sample[-1]:
                        total = 0
                        sample_n = random.random()
                        for dm in noun_deriv_probabilities: 
                            total += noun_deriv_probabilities[dm]
                            if sample_n < total:
                                break
                        sample.append("^" + dm)
                    elif "V)" in sample[-1] and "DEM" not in sample[-1]:
                        total = 0
                        sample_n = random.random()
                        for dm in verb_deriv_probabilities: 
                            total += verb_deriv_probabilities[dm]
                            if sample_n < total:
                                break
                        sample.append("^" + dm)
    
            # sample the inflectional morpheme
            if "N)" in sample[-1] or "(AREA)" in sample[-1] or "(DEM.PRO)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in noun_infl_probabilities: 
                    total += noun_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break
            elif ("V)" in sample[-1] and "ADV)" not in sample[-1]) or \
                  "(CmpdVbl)" in sample[-1] or \
                  "STATIVE)" in sample[-1] or "ACTIVE)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in verb_infl_probabilities: 
                    total += verb_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break
            elif "QUANTQUAL)" in sample[-1]:
                total = 0
                sample_n = random.random()
                for im in qq_infl_probabilities: 
                    total += qq_infl_probabilities[im]
                    if sample_n < total:
                        sample.append("^" + im)
                        break

            # sample the number of enclitics to include
            num_enclitic = 0
            total = 0
            sample_n = random.random()
            for enclitic_count in enclitic_count_probabilities: 
                total += enclitic_count_probabilities[enclitic_count]
                if sample_n < total:
                    num_enclitic = enclitic_count
                    break

            # sample the enclitic(s)
            if num_enclitic > 0:
                total = 0
                sample_n = random.random()
                for encl in enclitic_probabilities: 
                    total += enclitic_probabilities[encl]
                    if sample_n < total:
                        sample.append("^" + encl)
                        break
     
            # cleanup: remove explicit NULL morphemes (from zero derivations)
            cleaned_sample = [morpheme for morpheme in sample if "NULL" not in morpheme]
    
            samples.append(''.join(cleaned_sample))
            counter += 1

    return samples


def sampling_3A(sample_num, morpheme_dist, enclitic_count_dist, pos_counts_after_pos_dist):
    '''
    :param sample_num:                number of samples to create
    :type  sample_num:                int
    :param morpheme_dist:             counts of all morphemes
    :type  morpheme_dist:             dict
    :param enclitic_count_dist:       counts of the number of words with N enclitics
    :type  enclitic_count_dist:       dict
    :param pos_counts_after_pos_dist: counts the number of times each POS tag follows 
                                      each POS tag
    :type  pos_counts_after_pos_dist: nested dict

    :return: list

    Samples using Variation 3A: 

    '''
    # make all of the relevant probability dictionaries
    partofspeech_counts = make_partofspeech_dictionary_count(morpheme_dist)
    partofspeech_count_probabilities = make_prior_probability_dict(partofspeech_counts)

    enclitic_count_probabilities = make_prior_probability_dict(enclitic_count_dist)

    noun_root_probabilities, verb_root_probabilities, particle_probabilities, \
    emo_root_probabilities, pos_root_probabilities, \
    num_root_probabilities, area_root_probabilities, \
    xclm_root_probabilities, wh_root_probabilities, qq_root_probabilities, \
    pronoun_probabilities, vocative_probabilities, \
    dem_anaphor_probabilities, dem_adv_probabilities, dem_pro_probabilities, demonstrative_probabilities, \
    noun_deriv_probabilities, verb_deriv_probabilities, \
    emo_deriv_probabilities, pos_deriv_probabilities, \
    num_deriv_probabilities, dem_deriv_probabilities, \
    noun_infl_probabilities, verb_infl_probabilities, qq_infl_probabilities, \
    enclitic_probabilities = [d for d in make_all_probability_dicts(morpheme_dist)]

    samples = []
    counter = 0 
    while counter < sample_num: 
        if counter % 100000 == 0:
            print("sampling " + str(counter) + " out of " + str(sample_num) + "...")

        sample = []

        # sample the part-of-speech tag
        partofspeech = ""
        total = 0
        sample_n = random.random()
        for part_of_speech in partofspeech_count_probabilities:
            total += partofspeech_count_probabilities[part_of_speech]
            if sample_n < total:
                partofspeech = part_of_speech
                break

        # sample a root 
        root  = ""
        total = 0
        sample_n = random.random()
        if partofspeech == "noun":
            for root in noun_root_probabilities: 
                total += noun_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "verb":
            for root in verb_root_probabilities: 
                total += verb_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "particle":
            for root in particle_probabilities: 
                total += particle_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "emotional root":
            for root in emo_root_probabilities: 
                total += emo_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "postural root":
            for root in pos_root_probabilities: 
                total += pos_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "numeral":
            for root in num_root_probabilities: 
                total += num_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "positional":
            for root in area_root_probabilities: 
                total += area_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "exclamation":
            for root in xclm_root_probabilities: 
                total += xclm_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "wh word":
            for root in wh_root_probabilities: 
                total += wh_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "quantqual":
            for root in qq_root_probabilities: 
                total += qq_root_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "pronoun":
            for root in pronoun_probabilities: 
                total += pronoun_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "vocative":
            for root in vocative_probabilities: 
                total += vocative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "demonstrative":
            for root in demonstrative_probabilities: 
                total += demonstrative_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem anaphor":
            for root in dem_anaphor_probabilities: 
                total += dem_anaphor_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem adverb root":
            for root in dem_adv_probabilities: 
                total += dem_adv_probabilities[root]
                if sample_n < total:
                    break
        elif partofspeech == "dem pronoun root":
            for root in dem_pro_probabilities: 
                total += dem_pro_probabilities[root]
                if sample_n < total:
                    break

        if root:
            sample.append(root)

            # sample the morpheme to follow the root
            if partofspeech in pos_counts_after_pos_dist:

                while True:

                    # first sample the morpheme's part of speech
                    pos_counts_after_pos_probabilities = make_prior_probability_dict(pos_counts_after_pos_dist[partofspeech])
    
                    total = 0
                    sample_n = random.random()
                    for pos in pos_counts_after_pos_probabilities:
                        total += pos_counts_after_pos_probabilities[pos]
                        if sample_n < total:
                            partofspeech = pos 
                            break

                    # then sample the morpheme itself
                    if partofspeech != "Infl":
                        morpheme_probability_dict = {}
                        if "(N→" in partofspeech:
                            morpheme_probability_dict = noun_deriv_probabilities
                        elif "(V→" in partofspeech:
                            morpheme_probability_dict = verb_deriv_probabilities
                        elif "(EMO→" in partofspeech:
                            morpheme_probability_dict = emo_deriv_probabilities
                        elif "(POS→" in partofspeech:
                            morpheme_probability_dict = pos_deriv_probabilities
                        elif "(NUM→" in partofspeech:
                            morpheme_probability_dict = num_deriv_probabilities
                        elif "(DEM→" in partofspeech:
                            morpheme_probability_dict = dem_deriv_probabilities
    
                        chosen_morpheme = "()"
    
                        while partofspeech != "(" + chosen_morpheme.rsplit("(", 1)[1]:
                            total = 0
                            sample_n = random.random()

                            for morpheme in morpheme_probability_dict:
                                total += morpheme_probability_dict[morpheme]
                                if sample_n < total:
                                    chosen_morpheme = morpheme
                                    break
        
                        sample.append("^" + chosen_morpheme)
                        partofspeech = "(" + chosen_morpheme.rsplit("(", 1)[1]
    
                    if "→" not in partofspeech:
                        break

            # sample the inflectional morpheme
            if partofspeech == "Infl":
                if "N)" in sample[-1] or "(AREA)" in sample[-1] or "(DEM.PRO)" in sample[-1]:
                    total = 0
                    sample_n = random.random()
                    for im in noun_infl_probabilities: 
                        total += noun_infl_probabilities[im]
                        if sample_n < total:
                            sample.append("^" + im)
                            break
                elif ("V)" in sample[-1] and "ADV)" not in sample[-1]) or \
                      "(CmpdVbl)" in sample[-1] or \
                      "STATIVE)" in sample[-1] or "ACTIVE)" in sample[-1]:
                    total = 0
                    sample_n = random.random()
                    for im in verb_infl_probabilities: 
                        total += verb_infl_probabilities[im]
                        if sample_n < total:
                            sample.append("^" + im)
                            break
                elif "QUANTQUAL)" in sample[-1]:
                    total = 0
                    sample_n = random.random()
                    for im in qq_infl_probabilities: 
                        total += qq_infl_probabilities[im]
                        if sample_n < total:
                            sample.append("^" + im)
                            break

                # sample the enclitic(s)
                while True:

                    previous_morpheme = sample[-1]
                    previous_morpheme_tag = ""
                    for tag in pos_counts_after_pos_dist["enclitic"]:
                        if tag in previous_morpheme:
                            previous_morpheme_tag = tag
                            break
                        elif "Abs" in previous_morpheme or "Rel" in previous_morpheme or \
                           "Abl_Mod" in previous_morpheme or "Loc" in previous_morpheme or \
                           "All" in previous_morpheme or "Prl" in previous_morpheme or "Equ" in previous_morpheme:
                            previous_morpheme_tag = "N"
                            break
                        elif "Intr" in previous_morpheme or "Trns" in previous_morpheme or "Fear" in previous_morpheme:
                            previous_morpheme_tag = "V"
                            break
                        elif "Sg" in previous_morpheme or "Pl" in previous_morpheme or "Du" in previous_morpheme:
                            previous_morpheme_tag = "QUANTQUAL"
                            break

                    # sample whether or not to suffix an enclitic
                    add_enclitic_probabilities = make_prior_probability_dict(pos_counts_after_pos_dist["enclitic"][previous_morpheme_tag])
                    add_enclitic = False
    
                    total = 0
                    sample_n = random.random()
                    for yesno in add_enclitic_probabilities: 
                        total += add_enclitic_probabilities[yesno]
                        if sample_n < total:
                            if yesno == "YES":
                                add_enclitic = True
                            break
    
                    # sample the enclitic if 'add_enclitic' == True
                    if add_enclitic == True:
                        total = 0
                        sample_n = random.random()
                        for encl in enclitic_probabilities: 
                            total += enclitic_probabilities[encl]
                            if sample_n < total:
                                sample.append("^" + encl)
                                break

                    if add_enclitic == False:
                        break

            # cleanup: remove explicit NULL morphemes (from zero derivations)
            cleaned_sample = [morpheme for morpheme in sample if "NULL" not in morpheme]

            samples.append(''.join(cleaned_sample))
            counter += 1

    return samples
