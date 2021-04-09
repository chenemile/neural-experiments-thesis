import pprint

from zipfian_methods import *
from sampling_methods import *


def main():
    jsonfile   = "/home/echen41/neural-experiments-thesis/make-dataset/word2analyses.json"

    with open(jsonfile) as f:
        word2analyses = json.load(f)

    probfrac_w2a, morpheme_dist, deriv_count_dist = get_zipfdist_of_morphemes_over_probable_fractional_counts(word2analyses)

    #pprint.pprint(morpheme_dist)
    #print()
    #pprint.pprint(deriv_count_dist)

    enclitic_count_dist = get_enclitic_counts(probfrac_w2a)
    pos_counts_after_each_pos = get_pos_counts_after_each_pos(probfrac_w2a)

    samples = sampling_3A(1000, morpheme_dist, enclitic_count_dist, pos_counts_after_each_pos) 

    for sample in samples:
        print(sample)
    

if __name__ == "__main__":
    main()
