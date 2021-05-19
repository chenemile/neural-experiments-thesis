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
    :: tag=(Analyzer: "2.6")
    > lowercase
    > uppercase
    > full_l2is
    > lexc="repo/ess.lexc"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && make lowercase.fomabin && make uppercase.fomabin && make full_l2is.fomabin

    for f in *.fomabin ; do mv ${f} ../${f%.fomabin} ; done
}


task parser
     :: url="git@github.com:dowobeha/yupik-parser.git"
     :: tag=(Qamani: "1.3.19")
     > itemquulteki
{
    git clone --depth 1                \
              --single-branch          \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && swift build && mv .build/debug/itemquulteki ..
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
    :: neurexp_scripts_url="git@github.com:chenemile/neurexp-scripts-and-devtest.git"
    :: neurexp_scripts_tag=(Scripts: "0.0.2")
    :: cg_url="git@github.com:hayleypark/yupik_constraint_grammar.git"
    :: cg_tag=(CG: "0.0.1")
     > foma_py="foma.py"
     > count_methods="count_methods.py"
     > memorize_these="memorize_these.sh"
     > make_surface="make_surface.py"
     > make_underlying="make_underlying.py"
     > word2analyses="make_word2analyses_json.py"
     > partition_data="partition_data.sh"
     > sampling_methods="sampling_methods.py"
     > tokenize_char="tokenize_char.sh"
     > get_wer="get_word_error_rate.py"
     > fst_on_devtest="get_fst_on_devtest_results.py"
     > src_devtest="devtest/src-dev.txt"
     > tgt_devtest="devtest/tgt-dev.txt"
     > preprocess_analyses="preprocess_analyses.py"
     > cg="yupik.cg3"
{
    git clone --depth 1                    \
                --single-branch              \
              -c advice.detachedHead=false \
              --branch ${neurexp_scripts_tag} ${neurexp_scripts_url} neurexp_scripts

    git clone --depth 1                    \
                --single-branch              \
              -c advice.detachedHead=false \
              --branch ${cg_tag} ${cg_url} cg_scripts

    wget ${foma_url}

    mv neurexp_scripts/* .
    mv cg_scripts/scripts/* .
    mv cg_scripts/yupik.cg3 .
}
    

task word2analyses
    < script=$word2analyses@scripts
    < cg=$out@run_cg
    > out
{
    python3 ${script} --cg_output=${cg} --json_name=${out}
}


task training_data
    < make_underlying=@scripts
    < make_surface=@scripts
    < foma_py=@scripts
    < word2analyses=$out@word2analyses
    < analyzer=$lowercase@analyzer
    < lexc=@analyzer
    < memorize_these=@scripts
    < partition_data=@scripts
    < tokenize_char=@scripts
    > underlying="underlying.txt"
    > memorize="memorize.txt"
    > surface="surface.txt"
    > data="data.txt"
    > src_train="data/src-train.txt"
    > src_val="data/src-val.txt"
    > tgt_train="data/tgt-train.txt"
    > tgt_val="data/tgt-val.txt"
    :: count_method=(GetCounts: "random" "mixed" "shortest" "uniform_frac" "conditional_frac")
    :: sampling_method=(SampleMethod: "1A" "2A" "2B" "3A")
    :: size=(NumSamples: 1mil=1000000 3mil=3000000 5mil=5000000)
{
    python3 ${make_underlying} --json=${word2analyses} --count_method=${count_method} --sampling_method=${sampling_method} --num_samples=${size} --output=${underlying}

    python2.7 ${make_surface} --underlying=${underlying} --surface=${surface} --analyzer=${analyzer}

    shuf -n ${size} ${surface} > ${data} 

    bash ${memorize_these} ${lexc}

    for i in {1..100}; do cat ${memorize} >> ${data}; done

    ${partition_data} ${data}

    mkdir data
    mv train.tsv val.tsv testset.tsv data

    ${tokenize_char} data

    rm data/train.tsv data/val.tsv data/testset.tsv
}

# TODO: task that creates the virtual env and populates it (OpenNMT, PyTorch)


task yaml
    < src_train=@training_data
    < src_val=@training_data
    < tgt_train=@training_data
    < tgt_val=@training_data
    > yaml="config.yaml"
{
    echo "# neural experiments yaml" > ${yaml}

    echo "" >> ${yaml}

    echo "# where the samples will be written" >> ${yaml}
    echo "save_data: run" >> ${yaml}
    echo "# where the vocab(s) will be written" >> ${yaml}
    echo "src_vocab: run/vocab.src" >> ${yaml}
    echo "tgt_vocab: run/vocab.tgt" >> ${yaml}
    echo "# prevent overwriting existing files" >> ${yaml}
    echo "overwrite: False" >> ${yaml}

    echo "" >> ${yaml}

    echo "# corpus opts:" >> ${yaml}
    echo "data:" >> ${yaml}
    echo "    corpus_1:" >> ${yaml}
    echo "        path_src: ${src_train}" >> ${yaml}
    echo "        path_tgt: ${tgt_train}" >> ${yaml}
    echo "    valid:" >> ${yaml}
    echo "        path_src: ${src_val}" >> ${yaml}
    echo "        path_tgt: ${tgt_val}" >> ${yaml}

    echo "" >> ${yaml}

    echo "# vocabulary files that were just created" >> ${yaml}
    echo "src_vocab: run/vocab.src" >> ${yaml}
    echo "tgt_vocab: run/vocab.tgt" >> ${yaml}

    echo "" >> ${yaml}

    echo "# GPUs" >> ${yaml}
    echo "world_size: 3" >> ${yaml}
    echo "gpu_ranks: [0,1,2]" >> ${yaml}

    echo "" >> ${yaml}

    echo "# hyperparams" >> ${yaml}
    echo "encoder_type: brnn" >> ${yaml}
    echo "early_stopping: 5" >> ${yaml}

    echo "" >> ${yaml}

    echo "# where to save the checkpoints" >> ${yaml}
    echo "save_model: run/model" >> ${yaml}
    echo "#save_checkpoint_steps: 500" >> ${yaml}
    echo "#train_steps: 1000" >> ${yaml}
    echo "#valid_steps: 10000" >> ${yaml}
    echo "keep_checkpoint: 1" >> ${yaml}
}

global {
cuda_devices="5,6,7"
}


task train_model
#    < activate="/home/echen41/venv/bin/activate"
    < yaml=@yaml
    > model="./model.pt"
    > src_vocab="run/vocab.src"
    > tgt_vocab="run/vocab.tgt"
    :: size=(NumSamples: 1mil=1000000 3mil=3000000 5mil=5000000)
    :: cuda_devices=@
{
    # activate the virtual environment
#    source ${activate}

    onmt_build_vocab -config ${yaml} -n_sample ${size}

    export CUDA_VISIBLE_DEVICES="${cuda_devices}"

    onmt_train -config ${yaml}

    ln -s run/model* ${model}
}


task devtest_predictions
    < model=@train_model
    < src_devtest=@scripts
    > predictions
{
    onmt_translate -model ${model} -src ${src_devtest} -output ${predictions} -gpu 0 -verbose -n_best 3
}


task accuracy
    < script=$get_wer@scripts
    < analyzer=$uppercase@analyzer 
    < src_devtest=@scripts
    < tgt_devtest=@scripts
    < predictions=@devtest_predictions
    > output="accuracy.txt"
{
    python2.7 ${script} ${analyzer} ${src_devtest} ${tgt_devtest} ${predictions} > ${output}
}


task fst_devtest
    < itemquulteki=@parser
    < l2s=$uppercase@analyzer
    < l2is=$full_l2is@analyzer
    < src_devtest=@scripts 
    < tgt_devtest=@scripts 
    < script=$fst_on_devtest@scripts
    > output="results.txt"
{
    cat ${src_devtest} | tr -d "[:space:]" > sentences
    cat ${tgt_devtest} | tr -d "[:space:]" > gold

    ${itemquulteki} --l2s=${l2s} --l2is=${l2is} --sentences=${sentences} --mode=all > ${parser_output}

    python3 ${script} ${parser_output} ${gold} > ${output}
}


plan shortest_2A_5mil 
{
    reach devtest_predictions via (GetCounts: "shortest") * (SampleMethod: "2A") * (NumSamples: 5mil)
}

#plan fst_devtest_results 
#{
#    reach fst_devtest
#}
