# -*- coding: utf-8 -*-

'''
:author: Emily Chen
:date:   2021

'''
import argparse
import json
import pprint

from zipfian_methods import *
from sampling_methods import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zipfian_method', help='OPTIONS: random, shortest, mixed, uniform-frac, conditional-frac')
    parser.add_argument('sampling_method', help='OPTIONS: 1A, 2A, 2B, 3A')
    parser.add_argument('num_samples', help='number of training items to generate')
    parser.add_argument('include_zero_derivations',  help='OPTIONS: include_zero, exclude_zero')
    args = parser.parse_args()

    jsonfile   = "/home/echen41/neural-experiments-thesis/make-dataset/word2analyses.json"
    outputfile = "/home/echen41/neural-experiments-thesis/make-dataset/underlying.txt"

    num_samples     = int(args.num_samples)
    sampling_method = args.sampling_method
    parameters      = []

    with open(jsonfile) as f:
        word2analyses = json.load(f)

    if args.zipfian_method == "random":
        random_w2a, morpheme_dist, deriv_count_dist = get_zipfdist_of_morphemes_over_random_analyses(word2analyses)
        enclitic_count_dist = get_enclitic_counts(random_w2a)
        deriv_count_after_stem_dist = get_deriv_counts_after_stem_type(random_w2a)

    elif args.zipfian_method == "shortest":
        shortest_w2a, morpheme_dist, deriv_count_dist = get_zipfdist_of_morphemes_over_shortest_analyses(word2analyses)
        enclitic_count_dist = get_enclitic_counts(shortest_w2a)
        deriv_count_after_stem_dist = get_deriv_counts_after_stem_type(shortest_w2a)

    elif args.zipfian_method == "mixed":
        mixed_w2a, morpheme_dist, deriv_count_dist = get_zipfdist_of_morphemes_over_random_and_shortest_analyses(word2analyses)
        enclitic_count_dist = get_enclitic_counts(mixed_w2a)
        deriv_count_after_stem_dist = get_deriv_counts_after_stem_type(mixed_w2a)

    params = list()
    params.append(morpheme_dist)
    params.append(deriv_count_dist)
    params.append(enclitic_count_dist)
    params.append(deriv_count_after_stem_dist)

    samples = generate_samples(num_samples, sampling_method, params)

    # write to an output file
    with open(outputfile, 'w') as f:
        for sample in samples:
            f.write(sample + "\n")


if __name__ == "__main__":
    main()
