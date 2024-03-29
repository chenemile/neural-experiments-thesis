# notes on neural experiments

## research questions
theme -> low-resource setting. contributions are to low-resource languages.

1. we've accounted for all of the grammatical/phonological rules. why are there still so many items the analyzer is failing on?
    1. what are these items?
    1. is there a distinguishable pattern?
1. how do we learn these errors using deep learning?
    1. what does the training data look like? and how do we decide this? we go from too little data to too much.
    1. how much does sampling matter? can we start with incredibly noisy data, sample well, and get good results?
    1. how many training items do we need?
    1. what's the best architecture? does it make a difference?
    1. why might some of this be?
1. can we just throw more data at the problem or does the data have to be structured in some meaningful way? -> deep learning efficiency
    1. is there some quantifiable relationship between the "quality" of data and the number of training examples needed? closed domain machine translation
    1. what are the tradeoffs? human effort/time/payment versus electricity used/carbon footprint, etc.


## generating training data

### how sampling works in code
imagine a button that pops out one m&m. eventually the distribution of m&ms produced matches the distribution of the manual count.

```
for num_m&ms_you_want:
    sample an m&m
```

assume the following probabilities for each color of m&m:
* red  - 0.2
* green - 0.2
* yellow - 0.2
* blue - 0.2
* brown - 0.2

generate a number between 0 and 1. start at beginning of list. let's say the sample is n = 0.53, which is less than 0.6. that means we've sampled yellow. let's say n = 0.9. that means we've sampled brown.

```
sample = rand(0,1)
colors = [(red, 0.2), (yellow, 0.2), (red, 0.2), (brown, 0.2), (green, 0.2)]
total = 0.0
for color in colors:
    total += color.probability
    if sample <= total:
        sampled_color = color
        break
```

in order to do conditional distributions, outside of the `for` loop would be `while True:`

instead of m&ms, in our case, we would:
1. sample a sentence type.
2. sample a word structure.
3. sample a verb.
4. sample a subject and object based on the verb.


### which data to use
1. BASELINE
    * use only the analyses generated by the FST analyzer.

1. VARIATION
    * use the analyses generated by the FST analyzer _and_ my manual analyses for words the FST could not analyze.


### how to get zipf counts of morphemes
getting a zipfian distribution of morphemes and variations on getting that zipf dist.

get zipf counts for the whole digital corpus.

1. BASELINE
    * for each word, select one and only one analysis using a uniform dist.
    * simply count the number of instances of each morpheme.
    * this is just chaos.

1. VARIATION
    * for each word, select one and only one analysis, i.e. one with the fewest morphemes.
    * if multiple analyses have the fewest number of morphemes, use a uniform dist to select one.
    * simply count the number of instances of each morpheme.
    * reasonable since we know the analyzer is prone to overgeneration.

1. VARIATION
    * for each word, select one and only one analysis.
    * 75% of the time, select an analysis with the fewest number of morphemes using a uniform dist.
    * remaining 25%, use a uniform dist to select any analysis.
    * simply count the number of instances of each morpheme.
    * introduces some noise.

1. VARIATION
    * fractional counts with uniform probabilities.
    * e.g. assume a corpus with one word which has five analyses. treat each analysis as having occurred 1/5 times, so probability of selecting an analysis = 0.2.
    
    count the number of instances of each morpheme, but use its fractional count instead. so instead of `count+=1`, do `count+=0.2`.
    
        * qikmigh(N) ^ -ghhagh(NN) ^ [Rel.Sg]
        * qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Pl]
        * qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Sg]
        * qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Pl]
        * qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Sg]

    we'd get:
        * qikmigh  = 0.2
        * ghhagh   = 0.2
        * [Rel.Sg] = 0.2
        * qikmighhagh = 0.8 (because 0.2 + 0.2 + 0.2 + 0.2)
        * ...
        
1. VARIATION
    * fractional counts with probabilities based on the percentage of analyses that have one morpheme, two morphemes, three, etc.
    * e.g. assume a corpus with many words, one of which is _qikmighhaghmeng_. this word has five analyses. one of the analyses has three morphemes and the other four analyses have two morphemes. assume the following probabilities for this corpus:
        * P(word having three morphemes) = 0.2
        * P(word having two morphemes) = 0.6
        * P(word having one morpheme) = 0.2

    normalize these probabilities by adding them up -> denominator. in this example, denominator = 0.2 + 0.6 + 0.6 + 0.6 + 0.6 = 2.6.

    each probability gets divided by that denominator = fractional count for that analysis.

        *  qikmigh(N) ^ -ghhagh(NN) ^ [Rel.Sg]    -> 0.2 / 2.6 = 0.077
        * qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Pl]        -> 0.6 / 2.6 = 0.23
        * qikmighhagh(N) ^ [Abl_Mod.4DuPoss.Sg]        -> 0.6 / 2.6 = 0.23
        * qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Pl]        -> 0.6 / 2.6 = 0.23
        * qikmighhagh(N) ^ [Abl_Mod.4PlPoss.Sg]        -> 0.6 / 2.6 = 0.23

    then, for every time _qikmighhaghmeng_ appears in the corpus:
        * qikmigh  += 0.077
        * ghhagh   += 0.077
        * [Rel.Sg] += 0.077
        * qikmighhagh += 0.23 + 0.23 + 0.23 + 0.23
        * [Abl_Mod.4DuPoss.Pl] += 0.23
        * ...

### how to sample
the sampling process and variations on the sampling process.

1. BASELINE (Sample Method 1A)
    1. sample a root type where every root type has equal probability (prior)
    ```
    P(ROOT TYPE) = 1 / (total # root types)
    ```
    1. sample the number of derivational morphemes to include where every number of derivational morphemes has equal probability (prior)
    ```
    if ROOT TYPE in [particle, exclamation, quantqual, pronoun, vocative, demonstrative, dem pronoun root]
            NUM DERIV = 0
    else
            P(NUM DERIV) = 1 / (maximum # derivational morphemes found in a word in the corpus)
    
            P(NUM DERIV=n) = (# items in corpus with n derivational morphemes) / (total # of items in corpus)
    ```
    1. sample a root given a root type where every root has equal probability (conditional on POS)
    ```
    P(ROOT | ROOT TYPE) = P(ROOT TYPE | ROOT)*P(ROOT) / P(ROOT TYPE) -> bayes' theorem
            where P(ROOT TYPE | ROOT) is either 0 or 1 (this is a simplifying assumption, which is true in the majority of cases)
                  P(ROOT) = 1 / (total # roots)
                  P(ROOT TYPE) = 1 / (total # root types)
            therefore this probability P(ROOT | ROOT TYPE) = P(ROOT TYPE | ROOT)*(total # root types) / (total # roots)
    
    when applying this to specific root types, we see that (total # root types) = 1 and (total # roots) becomes the total number of roots of that specific root type.
    
            P(noun root R | root type NOUN) = 1 / (# nouns roots)
            P(verb root R | root type VERB) = 1 / (# verb roots)
            P(particle root R | root type PTCL) = 1 / (# particles)
            etc.
    
            P(verb root R | root type NOUN) = 0
            P(particle root R | root type VERB) = 0
            etc.
    
            laag(N) -> noun root
            laag(V) -> verb root
            P(laag | NOUN) = P(NOUN | laag)
    ```
    1. sample the derivational morphemes (conditional on stem type)
    ```
    P(DM | STEM TYPE) = P(STEM TYPE | DM)*P(DM) / P(STEM TYPE) -> bayes' theorem
            where P(STEM TYPE | DM) is either 0 or 1 (simplifying assumption, because there are cases where a derivational morpheme suffixes to the "wrong" type of stem)
                  P(DM) = 1 / (total # deriv morphemes)
                  P(STEM TYPE) = 1 / (total # stem types)
            therefore this probability P(DM| STEM TYPE) = P(STEM TYPE | DM)*(total # stem types) / (total # deriv morphemes)
    
    when applying this to specific derivational morpheme types, we see that (total # stem types) = 1 and (total # deriv morphemes) becomes the total number of derivational morphemes of that specific derivational morpheme type.
    
            P(nominal deriv morpheme M | stem type NOUN) = 1 / (# nominal deriv morphemes)
            P(verbal deriv morpheme M | stem type VERB) = 1 / (# verbal deriv morphemes)
            etc.

            P(verbal deriv morpheme M | stem type NOUN) = 0
            P(nominal deriv morpheme M | stem type VERB) = 0
            P(nominal deriv morpheme M | stem type DEM) = 0
            etc.
    ```
    1. sample an inflectional morpheme (uniform but type of im depends on previous morpheme N or V)
    ```
    P(IM| STEM TYPE) = P(STEM TYPE | IM)*P(IM) / P(STEM TYPE) -> bayes' theorem
            where P(STEM TYPE | IM) is either 0 or 1 (simplifying assumption)
                  P(IM) = 1 / (total # types of infl morphemes)
                  P(STEM TYPE) = 1 / (total # stem types)
            therefore this probability P(IM| STEM TYPE) = P(STEM TYPE | IM)*(total # stem types) / (total # infl morphemes)
    
    when applying this to specific inflectional morpheme types, we see that (total # stem types) = 1 and (total # infl morphemes) becomes the total number of inflectional morphemes of that specific inflectional morpheme type.
    
            P(nominal infl morpheme M | stem type NOUN) = 1 / (# nominal infl morphemes)
            P(nominal infl morpheme M | stem type DEM.PRO) = 1 / (# nominal infl morphemes)
            P(verbal infl morpheme M | stem type VERB) = 1 / (# verbal infl morphemes)
            P(verbal infl morpheme M | stem type CMPDVBL) = 1 / (# verbal infl morphemes)
            etc.
    
            P(verbal infl morpheme M | stem type NOUN) = 0
            P(nominal infl morpheme M | stem type VERB) = 0
            P(nominal infl morpheme M | stem type PTCL) = 0
            etc.
    ```

1. VARIATION (Sample Method 2A)

    1. sample a root type (prior)
    ```
    P(ROOT TYPE) = (# words with that root type) / (total # words)
    ```
    1. sample the number of derivational morphemes to include (prior)
    ```
    P(NUM DERIV) = (# words with that many deriv morphemes) / (total # words)
    ```
    1. sample a root (conditional on POS)
    ```
    P(ROOT | ROOT TYPE) = P(ROOT TYPE | ROOT)*P(ROOT) / P(ROOT TYPE) -> bayes' theorem
            where P(ROOT TYPE | ROOT) is either 0 or 1
                  P(ROOT) = (# words with that root) / (total # words) 
                  P(ROOT TYPE) = (# words with that root type) / (total # words)
            therefore this probability P(ROOT | ROOT TYPE) = P(ROOT TYPE | ROOT)*(# words with root ROOT) / (# words of ROOT TYPE)

            P(noun root R | root type NOUN) = (# words with root R) / (# words of root type NOUN)
            P('anipa' | root type NOUN) = (# words with 'anipa' as the root) / (# words with noun roots)

            P(verb root R | root type VERB) = (# words with root R) / (# words of root type VERB)
            P('qiya' | root type VERB) = (# words with 'qiya' as the root) / (# words with verb roots)
            etc.

            P(verb root R | root type NOUN) = 0
            P('qiya' | root type NOUN) = 0

            P(noun root R | root type VERB) = 0
            P('anipa' | root type VERB) = 0
            etc.
    ```
    1. sample the derivational morphemes (conditional on stem type)
    ```
    P(DM | STEM TYPE) = P(STEM TYPE | DM)*P(DM) / P(STEM TYPE) -> bayes' theorem
            where P(STEM TYPE | DM) is either 0 or 1
                  P(DM) = (# words containing DM) / (total # words) 
                  P(STEM TYPE) = (# times words end in STEM TYPE) / (total # words)
            therefore this probability P(DM| STEM TYPE) = P(STEM TYPE | DM)*(# words containing DM) / (# times words end in STEM TYPE)

        in practice, (# times words end in STEM TYPE) might be better thought of as the number of times a specific type of deriv morpheme (nominal, verbal, etc.) is permitted to suffix a.k.a. the total number of times a specific type of deriv morpheme appears.

            P(nominal deriv morpheme M | stem type NOUN) = (# words containing M) / (# times words end in stem type NOUN)
            P('squghhagh' | stem type NOUN) = (# words containing 'squghhagh') / (# times words end in stem type NOUN)

            more accurately...
              P(nominal deriv morpheme M | stem type NOUN) = (# words containing M) / (total # times a nominal deriv morpheme appears)
              P('squghhagh' | stem type NOUN) = (# words containing 'squghhagh') / (total # times a nominal deriv morpheme appears)

              P(nominal deriv morpheme M | stem type VERB) = 0
              P('squghhagh' | stem type VERB) = 0
              etc.
    ```
    1. sample an inflectional morpheme (conditional on stem type)
    ```
    P(IM | STEM TYPE) = P(STEM TYPE | IM)*P(IM) / P(STEM TYPE) -> bayes' theorem
            where P(STEM TYPE | IM) is either 0 or 1
                  P(IM) = (# words containing IM) / (total # words) 
                  P(STEM TYPE) = (# times words end in STEM TYPE) / (total # words)
            therefore this probability P(IM| STEM TYPE) = P(STEM TYPE | IM)*(# words containing IM) / (# times words end in STEM TYPE)

    in practice, (# times words end in STEM TYPE) might be better thought of as the number of times a specific type of infl morpheme (nominal, verbal, etc.) is permitted to suffix a.k.a. the total number of times a specific type of infl morpheme appears.

            P(nominal deriv morpheme M | stem type NOUN) = (# words containing M) / (total # times a nominal infl morpheme appears)
            P('squghhagh' | stem type NOUN) = (# words containing 'squghhagh') / (total # times a nominal infl morpheme appears)

            P(nominal infl morpheme M | stem type VERB) = 0
            P('[Abs.Sg]' | stem type VERB) = 0
            etc.
    ```
    1. sample the number of enclitics (prior)
    ```
    P(NUM ENCL) = (# words with that many enclitics) / (total # words)
    ```
    1. sample the enclitics (prior)
    ```
    P(ENCL) = (# words containing ENCL) / (total # words with enclitics)
    ```

1. VARIATION (Sample Method 2B)
    1. sample a starting POS (prior)
    1. sample the number of derivational morphemes to include (conditional on POS)
    ```
    P(NUM DERIV | ROOT TYPE) = P(ROOT TYPE | NUM DERIV)*P(NUM DERIV) / P(ROOT TYPE) -> bayes' theorem
            where P(ROOT TYPE | NUM DERIV) = (# words of ROOT TYPE containing NUM DERIV morphemes) / (# words containing NUM DERIV morphemes)
                  P(NUM DERIV) = (# words containing NUM DERIV morphemes) / (total # words) 
                  P(ROOT TYPE) = (# words of ROOT TYPE) / (total # words)
            therefore this probability P(NUM DERIV | ROOT TYPE) = (# words of ROOT TYPE containing NUM DERIV morphemes) / (# words of ROOT TYPE)

            P(NUM DERIV | root type NOUN) = (# words of root type NOUN containing NUM DERIV morphemes) / (# words of root type NOUN)
            P(NUM DERIV | root type VERB) = (# words of root type VERB containing NUM DERIV morphemes) / (# words of root type VERB)
            P(NUM DERIV | root type EMO) = (# words of root type EMO containing NUM DERIV morphemes) / (# words of root type EMO)
    ```
    1. sample a root (conditional on POS)
    1. sample the derivational morphemes (conditional on stem type)
    1. sample an inflectional morpheme (conditional on stem type)
    1. sample the number of enclitics (prior)
    1. sample the enclitics (prior)
    
###### NOTE:
(2A) and (2B) differ in the second step.

1.  VARIATION (Sample Method 3A)
    1. sample a starting POS (prior)
    1. sample a root (conditional on POS)
    1. sample the POS of the next morpheme (NN, NV, VV, VN, or inflectional, conditioned on the the POS of the previous morpheme)
    1. sample the actual morpheme given the sampled POS. if a derivational morpheme was chosen, repeat Step (iii). currently, no maximum as to how many times (iii) is repeated.
    1. sample an enclitic or NULL (conditional on POS of previous morpheme). if an enclitic was chosen, repeat Step (v)
    
###### NOTE

3A differs from previous sampling methods because each step is completely conditioned on the POS of the previous morpheme. we don't determine the number of derivational morphemes to include beforehand. we just keep sampling deriv morphemes until we're told to sample an infl morpheme.


### summary
content in parentheses, e.g. (exclude-unanalyzed), refer to parameter names that appear in the generating scripts.

#### two options for what corpus to use

parameter name | description
---------------|------------
(exclude-unanalyzed) | using just the output from the FST analyzer
(include-unanalyzed) | using output from the FST analyzer and my manual analyses

#### five options for getting morpheme counts

parameter name | description
---------------|------------
(random) | if there are multiple analyses, randomly select one with a uniform dist
(mixed) | 75% of the time select the shortest analysis, 25% of the time randomly an analysis using a uniform dist
(shortest) | always select the shortest analysis
(uniform-frac) | fractional counts (uniform)
(conditional-frac) | fractional counts (conditional)

#### four options for sampling
parameter name | description
---------------|------------
(1A) | uniform
(2A) | conditional (# deriv morphemes was a prior model)
(2B) | conditional (# deriv morphemes was a conditional model)
(3A) | conditional (completely conditioned on POS of previous morpheme, # deriv morphemes not determined beforehand)
   
treat postural and emotional roots the way they appear in the data. they would have their own tables/dartboards.
same with particles, demonstratives, numerals, pronouns.

use scripts to generate the underlying forms as before and then the FST to generate the corresponding surface forms.
verb roots and nouns roots will eventually need to both inflect for nominal endings.


## training regimen
neural network should improve upon the FST by being more lax about morphophonology, morphotactics, and spelling. relatively-speaking, morphophonology accounts for far fewer errors than spelling/orthography errors.

each training item is a pairing:

surface form | segmentation
-------------|-------------
p u g i m n a q r a g k i i g h u m a y a l g h i i | 12:pugime ^ 43:naqe ^ 342:ragkiigh ^ 834:uma ^ 7:yalghii ^ 23:0

input vocabularly consists of legal yupik characters. output vocabulary is yupik morphemes and caret ^

later perturb or "hallucinate" the erroneous data, such as zero derivation of postural and emotional roots which jacobson (2001) suggests is not allowed.


## TODO
- [x] run all variations using 3 million training examples -> [lane & bird (2020)](https://aclanthology.org/2020.acl-main.594/). use other settings from their paper as a baseline. rnn. shallow model. whatever else. dropout. see the OpenNMT config.yaml file for architectural settings. what can we achieve by using just the FST?

    ###### NOTE
    accuracy was calculated as (# correct analyses)/(total # analyses). these numbers need to be updated since there were some errors in the devtest set that have since been fixed (were fixed on 2021-09-22).

    get morpheme count method | sample method | date run | accuracy
    --------------------------|---------------|----------|---------
    random | 1A | 2021-03-20 | 48.66
    mixed | 1A | 2021-03-21  | 47.28
    shortest | 1A | 2021-04-06  | 47.37
    uniform-frac | 1A | 2021-03-26  | 45.32
    conditional-frac | 1A | 2021-03-29  | 45.84
    random | 2A | 2021-04-06  | 69.94
    mixed | 2A | 2021-04-07  | 69.54
    shortest | 2A | 2021-04-08  | 69.89
    uniform-frac | 2A | 2021-03-26  | 70.34
    conditional-frac | 2A | 2021-04-08  | 70.14
    random | 2B | 2021-04-09  | 69.68
    mixed | 2B | 2021-04-09  | 68.53
    ***shortest | 2B | 2021-04-10  | 70.72
    uniform-frac | 2B | 2021-03-28  | 70.32
    conditional-frac | 2B | 2021-03-31  | 69.14
    random | 3A | 2021-04-01  | 70.24
    mixed | 3A | 2021-04-02  | 69.60
    shortest | 3A | 2021-04-03  | 69.38
    uniform-frac | 3A | 2021-04-04  | 69.26
    conditional-frac | 4A | 2021-04-05  | 69.51

- [x] run all variations except for sampling method 1A with 5mil training examples

    get morpheme count method | sample method | accuracy
    --------------------------|---------------|---------
    random | 2A  | 70.87
    mixed | 2A  | 71.49
    ***shortest | 2A  | 71.76
    uniform-frac | 2A  | 70.72
    conditional-frac | 2A  | 70.97
    random | 2B  | 71.60
    mixed | 2B  | 70.96
    shortest | 2B  | 70.65
    uniform-frac | 2B  | 70.66
    conditional-frac | 2B  | 71.07
    random | 3A  | 69.84
    mixed | 3A  | 70.35
    shortest | 3A  | 70.57
    uniform-frac | 3A  | 70.60
    conditional-frac | 3A  | 70.07

- [x] conducted very cursory error analysis and found that the neural analyzer frequently messed up on closed class items, e.g. particles and demonstratives (they're generally-speaking closed class, with some exceptions). selected the best-performing 5mil system, i.e. shortest-2A-5mil and retrained from scratch a system that would memorize these closed class items. it saw each item something like ten times (in run.tape file) to ensure memorization. this system achieved an accuracy rate of 76.60% (this was run on the updated devtest set, 2021-09-22)
    
- [] conduct an in-depth error analysis and identify other patterns in what the neural analyzer is failing on

- [] how can we learn the space of FST errors? "hallucinate" the data and teach the analyzer what it's failing on, e.g. let's say it hasn't learned that there's some variability with short and long vowels. teach it that qikmighhaq and qikmighhaaq should yield the same analysis, for example. (surface forms will probably need to be manually generated somehow)

- [] hallucinate the data and use same network settings as previous runs. continue to memorize closed class items

- [] increase training data count. how much does training data count matter?

- [] vary the architecture. try a transformer.

- [] vary the architecture. try a model with additional hidden layers

- [] lower priority, but how can we efficiently validate the devtest set? perform error analysis?
