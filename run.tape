task digital_corpus
    :: url="git@github.com:SaintLawrenceIslandYupik/digital_corpus.git"
	:: tag=(CorpusVersion: "0.2.0")
	> sentences
	> titles
	> sentence_index
	> title_index
	> all="everything.txt"
	> stats
{
	git clone --depth 1                    \
			  --single-branch              \
		      -c advice.detachedHead=false \
			  --branch ${tag} ${url} data

	find data/ess -name "*.ess_titlepage" > ${title_index}
	find data/ess -name "*.ess_content"   > ${sentence_index}
				
	cat ${title_index}    | xargs cat | grep -v '^\s*$' > ${titles}
	cat ${sentence_index} | xargs cat | grep -v '^\s*$' > ${sentences}
	cat ${titles} ${sentences} > ${all}

	wc ${titles} ${sentences} > ${stats}
}

task analyzer
    :: url="git@github.com:SaintLawrenceIslandYupik/finite_state_morphology.git"
	:: tag=(Analyzer: "2.4")
	> lowercase
	> uppercase
{
	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${tag} ${url} repo

#	cd repo && make neural_lowercase.fomabin && make neural_uppercase.fomabin
	cd repo && make lowercase.fomabin && make uppercase.fomabin

	for f in *.fomabin ; do mv ${f} ../${f%.fomabin} ; done
}

task download_cg
	:: url="git@github.com:hayleypark/yupik_constraint_grammar.git"
	:: tag=(CG: "0.0.1")
	> script="repo/scripts/preprocess_analyses.py"
	> cg="repo/yupik.cg3"
{
	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${tag} ${url} repo
}

task flookup
	< analyzer=$uppercase@analyzer 
	< text=$all@digital_corpus
	> out
{
	cat ${text} | tr ' ' '\n' | grep -v '^[\n\t\s]*$' | flookup ${analyzer} > $out 
}

task run_cg
	< format_for_cg=$script@download_cg
	< analyses=$out@flookup
	< cg=$cg@download_cg
	> formatted
	> out
{
	python ${format_for_cg} --input_path=${analyses} > ${formatted}
	cat ${formatted} | vislcg3 --grammar ${cg} > ${out} 
}

task get_foma_py
	:: foma_py="https://raw.githubusercontent.com/mhulden/foma/master/foma/python/foma.py"
	> out
{
    wget ${foma_py} > ${out}
}

task make_word2analyses
	< cg=$out@run_cg
	< script="scripts/make_word2analyses_json.py"
	> out
{
	python3 ${script} --cg_output=${cg} --FLAG=${out}
}
	
task make_train_data
	< make_underlying="scripts/make_underlying.py"
	< make_surface="scripts/make_surface.py"
	< foma_py=$out@get_foma_py
	< word2analyses=$out@make_word2analyses
	< analyzer=$lowercase@analyzer
	> underlying
	> surface 
	> data
	> train
    > val
	> test	
	> src_train
	> src_val
	> src_test
	> tgt_train
	> tgt_val
	> tgt_test
	:: count_method=(GetCounts: "random" "mixed" "shortest" "uniform_frac" "conditional_frac")
	:: sampling_method=(SampleMethod: "1A" "2A" "2B" "3A")
	:: size=(NumSamples: 1mil=1000000 3mil=3000000)
{
	ln -s ${foma_py} foma.py

	python3 --json=${word2analyses} --count_method=${count_method} --sampling_method=${sampling_method} --num_samples=${size} > ${underlying}

	python3 --underlying=${underlying} --analyzer=${analyzer} ${make_surface} > ${surface}

	shuf -n ${size} ${surface} > ${data}

	rm -rf data
	mkdir data

    bash scripts/partition_data.sh ${data} data/${train} data/${val} data/${test}

	bash scripts/tokenize_char.sh data ${src_train} ${tgt_train} ${src_val} ${tgt_val} ${src_test} ${tgt_test}
}

#plan random_1A_3mil
#{
#	reach make_train_data via (GetCounts: "random") * (SampleMethod: "1A") * (NumSamples: 3mil)
#}
