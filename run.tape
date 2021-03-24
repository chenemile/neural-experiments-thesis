task digital_corpus
    :: url="git@github.com:SaintLawrenceIslandYupik/digital_corpus.git"  ***DOUBLE COLON DENOTES PARAMETER
	:: tag=(CorpusVersion: "0.0.3" "0.1.0" "0.1.1") ***PAREN ARE BRANCH POINTS
	> sentences
	> titles
	> sentence_index
	> title_index
	> all="everything.txt"
	> stats ***RIGHT ANGLE BRACKET ARE OUTPUTS, IF OUTPUTS ARE USED IN OTHER DUCTTAPE TASKS, THEY NEED AN OUTPUT VARIABLE
{ **ANYTHING IN BIG CURLY BRACES IS BASH
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
	:: tag=(Analyzer: "2.3") ***MAKE ANOTHER BRANCH VALUE FOR UPDATED ANALYZER
	> g2i
	> g2is
	> g2s
	> gi2s
	> f2i
	> f2is
	> f2s
	> fi2s      
	> l2i
	> l2is
	> l2s
	> li2s
	> a2s
	> ess
{
	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${tag} ${url} repo

	cd repo && make all

	for f in *.fomabin ; do mv ${f} ../${f%.fomabin} ; done

}

task download_cg
	:: url=""
	:: tag=""
	> format_script="repo/scripts/formatting.py" #"path in hayley's repo to the script"
	> cg="repo/yupik.cg3"
{
	git clone --depth 1                    \
	  		  --single-branch              \
			  -c advice.detachedHead=false \
			  --branch ${tag} ${url} repo

}

task flookup
	< analyzer=$l2s@analyzer 
	< text=$all@digital_corpus
	> out
{
	cat ${text} | tr ' ' '\n' | grep -v "^[\n\t\s]*$" | flookup $analyzer > $out 
}

task run_cg
	< script=$format_script@download_cg
	< analyses=$out@flookup
	< cg=$cg@download_cg
	> out
{
	cat ${analyses} | vislcg3 --grammar ${cg} > ${out} 
}

# TODO: make these their own tasks
    wget ${foma_py}
	:: foma_py="https://raw.githubusercontent.com/mhulden/foma/master/foma/python/foma.py"

	< script1="make-dataset/scripts/make_word2analyses_json.py"
	python3 ${script1} ${in} > ${word2analyses}


task make_train_data
	< script2="make-dataset/scripts/make_underlying.py"
	< script3="make-dataset/scripts/make_surface.py"
	< in=$out@run_cg
	< foma_py=$out@foma
	< [ANALYZER]
	> word2analyses
	> underlying
	> surface 
	> data
	> train
    > val
	> test	
	> src_train
	> src_val
	> src_test
	:: count_methods=(GetCounts: "random" "mixed" "shortest" "uniform_frac" "conditional_frac")
	:: sample_methods=(SampleMethod: "1A" "2A" "2B" "3A")
	:: size=(NumSamples: 1mil=1000000 3mil=3000000)
{
	ln -s ${foma_py} foma.py
	python3 ${script2} ${word2analyses} ${count_methods} ${sample_methods} ${size} > ${underlying}
	python3 ${script3} ${underlying} ${analyzer} > ${surface}
	shuf -n ${size} ${surface} > ${data}
    bash scripts/partition_data.sh ${data} ${train} ${val} ${test}
	bash scripts/tokenize_char.sh ${train} ${val} ${test} ${src_train} ${src_val}...

}

plan random_1A_3mil
{
	reach make_train_data via (GetCounts: "random") * (SampleMethod: "1A") * (NumSamples: 3mil)
}

