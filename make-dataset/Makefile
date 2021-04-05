all: dataset

# NOTE: check file paths in make_word2analyses_json.py and run_cg.sh
#       make sure subprocess.call(["scripts/run_cg.sh", [PARAM] ]) is
#         set to the desired parameter, "devset" or "dataset"
word2analyses.json:
	python3 scripts/make_word2analyses_json.py

all-steps: word2analyses.json
	python3 scripts/make_underlying.py shortest 1A 3250000 exclude_zero
	python2.7 scripts/make_surface.py /home/echen41/neural-experiments-thesis/make-dataset/underlying.txt /home/echen41/neural-experiments-thesis/make-dataset/surface.txt
	shuf -n 3000000 surface.txt > data.txt
	bash scripts/partition_data.sh
	bash scripts/tokenize_char.sh dataset
	rm *.txt data/*.tsv


# makes 'src-train.txt', 'src-val.txt', 'src-test.txt' and
# 'tgt-train.txt', 'tgt-val.txt', 'tgt-test.txt' using the specified parameters 

# GetCounts: random, mixed, shortest, uniform-frac, conditional-frac
# SamplingMethod: 1A, 2A, 2B, 3A
# NumSamples: 1mil=1000000 3mil=3000000
dataset:
	python3 scripts/make_underlying.py [mixed 2A 3000000] exclude_zero
	python2.7 scripts/make_surface.py /home/echen41/neural-experiments-thesis/make-dataset/underlying.txt /home/echen41/neural-experiments-thesis/make-dataset/surface.txt
	shuf -n 3000000 surface.txt > data.txt
	bash scripts/partition_data.sh
	bash scripts/tokenize_char.sh dataset
	rm *.txt data/*.tsv

clean-dataset:
	rm -rf data *.output *.txt scripts/*.pyc scripts/__pycache__


# makes 'src-dev.txt' and 'tgt-dev.txt' from the texts in 'devset-files/texts' and
# optionally includes proposed analyses for all of the unanalyzed words in those texts
devset:
	#python3 scripts/make_devset.py
	python3 scripts/make_devset.py --proposed_analyses /home/echen41/neural-experiments-thesis/make-dataset/devset-files/unanalyzed.tsv
	bash scripts/tokenize_char.sh devset
	rm *.output devset-files/unanalyzed.underlying devset-files/unanalyzed.surface devset-files/devset.tsv

clean-devset:
	rm -rf *.output devset-files/*.txt scripts/*.pyc scripts/__pycache__


clean:
	rm -rf *.output *.txt devset-files/*.txt scripts/*.pyc scripts/__pycache__
