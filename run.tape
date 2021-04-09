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


task flookup
	< analyzer=$uppercase@analyzer 
	< text=$all@digital_corpus
	> out
{
	cat ${text} | tr ' ' '\n' | grep -v '^[\n\t\s]*$' | flookup ${analyzer} > $out 
}

task run_cg
	< format_for_cg=$preprocess_analyses@scripts
	< analyses=$out@flookup
	< cg=$cg@scripts
	> formatted
	> out
{
	python ${format_for_cg} --input_path=${analyses} > ${formatted}
	cat ${formatted} | vislcg3 --grammar ${cg} > ${out} 
}


task scripts
	:: foma_url="https://raw.githubusercontent.com/mhulden/foma/master/foma/python/foma.py"
    :: emily_url="git@github.com:chenemile/neurexp-make-dataset-scripts.git"
    :: emily_tag=(SCRIPTS: "0.0.1")
    :: hayley_url="git@github.com:hayleypark/yupik_constraint_grammar.git"
    :: hayley_tag=(CG: "0.0.1")
     > foma_py="foma.py"
     > count_methods="count_methods.py"
     > make_surface="make_surface.py"
     > make_underlying="make_underlying.py"
     > make_word2analyses="make_word2analyses_json.py"
     > partition_data="partition_data.sh"
     > sampling_methods="sampling_methods.py"
     > tokenize_char="tokenize_char.sh"
     > preprocess_analyses="preprocess_analyses.py"
     > cg=yupik.cg3
{
	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${emily_tag} ${emily_url} emily_scripts

	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${hayley_tag} ${hayley_url} hayley_scripts

	wget ${foma_url}

	mv emily_scripts/* .
	mv hayley_scripts/scripts/* .
	mv hayley_scripts/yupik.cg3 .
}
	
task make_word2analyses
    < script=$make_word2analyses@scripts
    < cg=$out@run_cg
    > out
{
	python3 ${script} --cg_output=${cg} --json_name=${out}
}

task make_train_data
	< make_underlying=@scripts
	< make_surface=@scripts
	< foma_py=@scripts
	< word2analyses=$out@make_word2analyses
	< analyzer=$lowercase@analyzer
	< partition_data=@scripts
	< tokenize_char=@scripts
	> underlying="underlying.txt"
	> surface="surface.txt"
	> data="data.txt"
	:: count_method=(GetCounts: "random" "mixed" "shortest" "uniform_frac" "conditional_frac")
	:: sampling_method=(SampleMethod: "1A" "2A" "2B" "3A")
	:: size=(NumSamples: 1mil=1000000 3mil=3000000)
{
	python3 ${make_underlying} --json=${word2analyses} --count_method=${count_method} --sampling_method=${sampling_method} --num_samples=${size} --output=${underlying}

	python2.7 ${make_surface} --underlying=${underlying} --surface=${surface} --analyzer=${analyzer}

	shuf -n ${size} ${surface} > ${data}

    ${partition_data} ${data}

	mkdir dataset
	mv train.tsv val.tsv testset.tsv dataset

	${tokenize_char} dataset

	rm dataset/train.tsv dataset/val.tsv dataset/testset.tsv
}

plan random_1A_3mil 
{
	reach make_train_data via (GetCounts: "random") * (SampleMethod: "1A") * (NumSamples: 1mil)
}
