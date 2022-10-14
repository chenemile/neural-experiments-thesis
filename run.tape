#TODO:
#  - how to branch prelim_experiment task?
#  - make goldtest set
#  - task that creates the virtual env and populates it (OpenNMT, PyTorch)
#  - edit train_model to use virtual env

# ----------------------------------------------------
# NOTE:
# set global variables:
#     world_size   = num GPUs to train on
#     cuda_devices = GPU IDs
#     gpu_ranks    = ...also GPU IDs??
#     n_best       = num analyses to output per word
# ----------------------------------------------------

global {
world_size="8"
}

global {
cuda_devices="0,1,2,3,4,5,6,7"
}

global {
gpu_ranks="[0,1,2,3,4,5,6,7]"
}

global {
n_best="1"
}

global {
model_dir="/home/echen41/neural-experiments-thesis/3mil-all-variations"
}

global {
src_goldtest="/home/echen41/neural-experiments-thesis/goldtest/src-goldtest.txt"
}

global {
tgt_goldtest="/home/echen41/neural-experiments-thesis/goldtest/tgt-goldtest.txt"
}

global {
logreg="/home/echen41/neural-experiments-thesis/logistic_regression.csv"
}


task digital_corpus
    :: url="git@github.com:SaintLawrenceIslandYupik/digital_corpus.git"
    :: tag=(CorpusVersion: "0.2.0")
    > sentences
    > titles
    > sentence_index
    > title_index
    > all="everything.txt"
    > stats
    > devtest_texts="devtest_texts"
    > texts_without_devtest="texts_without_devtest"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} data

    find data/ess -name "*.ess_titlepage" > ${title_index}
    find data/ess -name "*.ess_content"   > ${sentence_index}
    find data/ess -name "*.ess" >> ${sentence_index}

    cat ${title_index}    | xargs cat | grep -v '^\s*$' > ${titles}
    cat ${sentence_index} | xargs cat | grep -v '^\s*$' > ${sentences}
    cat ${titles} ${sentences} > ${all}

    # remove punctuation, numbers; trim spaces
    sed -i -e 's/[[:punct:]]//g' -e 's/[0-9]//g' -e 's/^ *//g' ${titles}
    sed -i -e 's/[[:punct:]]//g' -e 's/[0-9]//g' -e 's/^ *//g' ${sentences}

    title_token_count=$(wc -w < ${titles})
    sent_token_count=$(wc -w < ${sentences})

    title_sent_count=$(wc -l < ${titles})
    sent_sent_count=$(wc -l < ${sentences})

    title_type_count=$(cat ${titles} | tr -s ' ' '\n' | tr '[:upper:]' '[:lower:]' | sort | uniq | wc -l)
    sent_type_count=$(cat ${sentences} | tr -s ' ' '\n' | tr '[:upper:]' '[:lower:]' | sort | uniq | wc -l)

    echo 'num tokens in titles: ' ${title_token_count} > ${stats}
    echo 'num tokens in sents:  ' ${sent_token_count} >> ${stats}
    echo 'total tokens:         ' $((${title_token_count} + ${sent_token_count})) >> ${stats}

    echo '' >> ${stats}

    echo 'num types in titles: ' ${title_type_count} >> ${stats}
    echo 'num types in sents:  ' ${sent_type_count} >> ${stats}
    echo 'total types:         ' $((${title_type_count} + ${sent_type_count})) >> ${stats}

    echo '' >> ${stats}

    echo 'total num sentences: ' $((${title_sent_count} + ${sent_sent_count})) >> ${stats}

    # make devtest set and set without devtest
    # (includes all texts where i manually analyzed the words the fst couldn't handle)
    mkdir ${texts_without_devtest}
    cp data/ess/jacobson_eoc/ess_content/* ${texts_without_devtest}
    cp data/ess/level1.kallagneghet/ess_content/* ${texts_without_devtest}
    cp data/ess/level2.akiingqwaghneghet/ess_content/* ${texts_without_devtest}
    cp data/ess/level3.suluwet/ess_content/* ${texts_without_devtest}
    cp data/ess/new_testament/* ${texts_without_devtest}
    cp data/ess/sivuqam_ungipaghaatangi_I/ess_content/* ${texts_without_devtest}
    cp data/ess/sivuqam_ungipaghaatangi_II/ess_content/* ${texts_without_devtest}
    cp data/ess/sivuqam_volume1/ess_content/* ${texts_without_devtest}
    cp data/ess/sivuqam_volume2/ess_content/* ${texts_without_devtest}
    cp data/ess/sivuqam_volume3/ess_content/* ${texts_without_devtest}
    cp data/ess/ungipaghaghlanga/ess_content/* ${texts_without_devtest}

    mkdir ${devtest_texts}
    cp data/ess/unleveled_readers/ess_content/* ${devtest_texts}
    cp data/ess/nagai/ess_content/* ${devtest_texts}

    mv ${texts_without_devtest}/02_ChewingGum.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/04_RavenWolf.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/05_Tufword1.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/09_Tufword2.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/12_Iistumii.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/01_MountainOutcrop.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/03_ThoughtfulMan.ess_content ${devtest_texts}
    mv ${texts_without_devtest}/volume2.part4.text6.ess_content ${devtest_texts}

    mv ${devtest_texts}/Ayumiim_Ungipaghaatangi_I.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ayumiim_Ungipaghaatangi_II.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ayumiim_Ungipaghaatangi_III.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ayumiim_Ungipaghaatangi_IV.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ayveghllak.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Kiiluuq.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Meghem_Teghikusii.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Neghqwaaghenka.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Otayahuk_Ungazimi.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Pangeghtellghet.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Pata_Ama_Ilangi.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Patankut.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Piinleghani.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Qateperewaaghmeng_Aatkaqelghii_Yuuk.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Sivuqam_Ungipamsugi.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Teghikusam_Avaqutii.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Teketaatenkuk_Kinunkuk.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/The_Adventures_Of_Sulpik.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ungazighmiit.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Ungazighmiit_Ungipaghaatangit.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/Yupigem_Homonym-ngi.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/nagai.part1.text1.ess_content ${texts_without_devtest}
    mv ${devtest_texts}/nagai.part1.text7.ess_content ${texts_without_devtest}
}


task analyzer
    :: url="git@github.com:SaintLawrenceIslandYupik/finite_state_morphology.git"
    :: tag=(Analyzer: "2.8")
    > l2s_ess
    > uppercase_ess
    > uppercase
    > l2is
    > lexc="repo/ess.lexc"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && make l2s_ess.fomabin && make uppercase_ess.fomabin && make uppercase.fomabin && make l2is.fomabin

    for f in *.fomabin ; do mv ${f} ../${f%.fomabin} ; done
}


task parser
     :: url="git@github.com:dowobeha/yupik-parser.git"
     :: tag=(Qamani: "1.4.0")
     > itemquulteki
{
    git clone --depth 1                \
              --single-branch          \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && swift build && mv .build/debug/itemquulteki ..
}


task flookup
    < analyzer=$uppercase_ess@analyzer
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
    :: neurexp_scripts_tag=(Scripts: "0.1.2")
    :: cg_url="git@github.com:hayleypark/yupik_constraint_grammar.git"
    :: cg_tag=(CG: "0.0.1")
     > foma_py="foma.py"
     > count_methods="count_methods.py"
     > memorize_these="memorize_these.sh"
     > add_surface="add_surface.py"
     > make_underlying="make_underlying.py"
     > word2analyses="make_word2analyses_json.py"
     > partition_data="partition_data.sh"
     > sampling_methods="sampling_methods.py"
     > tokenize_char="tokenize_char.sh"
     > neural_wer="get_neural_wer.py"
     > fst_wer="get_fst_wer.py"
     > preprocess_analyses="preprocess_analyses.py"
     > cg="yupik.cg3"
     > devtest_unanalyzed="unanalyzed_devtest.tsv"
     > make_devtest="make_devtest.py"
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
    < add_surface=@scripts
    < foma_py=@scripts
    < word2analyses=$out@word2analyses
    < analyzer=$l2s_ess@analyzer
    < lexc=@analyzer
    < memorize_these=@scripts
    < partition_data=@scripts
    < tokenize_char=@scripts
    > src_train="data/src-train.txt"
    > src_val="data/src-val.txt"
    > tgt_train="data/tgt-train.txt"
    > tgt_val="data/tgt-val.txt"
    :: count_method=(GetCounts: "random" "mixed" "shortest" "uniform_frac" "conditional_frac")
    :: sampling_method=(SampleMethod: "1A" "2A" "2B" "3A")
    :: size=(NumSamples: 3mil=3000000 5mil=5000000, 10mil=10000000)
{
    # (1) construct underlying forms
    python3 ${make_underlying} --json=${word2analyses} --count_method=${count_method} --sampling_method=${sampling_method} --num_samples=${size} --output="underlying.txt"

    # (2) generate corresponding surface forms
    python2.7 ${add_surface} --underlying="underlying.txt" --surface="has_surface_too.txt" --analyzer=${analyzer}

    # (3) select num data points to train on
    shuf -n ${size} "has_surface_too.txt" > "data.txt"

    # (4) force memorization of closed class items, e.g. demonstratives, particles, pronouns, etc.
    bash ${memorize_these} ${lexc}
    for i in {1..100}; do cat "memorize.txt" >> "data.txt"; done

    # (5) train on lowercased data
    sed -i 's/^[A-Z]/\L&/g' data.txt

    # (6) partition data into training set and validation set
    ${partition_data} "data.txt"

    # (7) tokenize data
    mkdir data
    mv train.tsv val.tsv data
    ${tokenize_char} data

    # (8) cleanup
    rm underlying.txt has_surface_too.txt memorize.txt data.txt data/train.tsv data/val.tsv
}


task yaml
    < src_train=@training_data
    < src_val=@training_data
    < tgt_train=@training_data
    < tgt_val=@training_data
    > yaml="config.yaml"
    :: world_size=@
    :: gpu_ranks=@
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
    echo "world_size:" ${world_size} >> ${yaml}
    echo "gpu_ranks:" ${gpu_ranks} >> ${yaml}

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


task train_model
    < activate="/home/echen41/venv/bin/activate"
    < yaml=@yaml
    > model="./model.pt"
    > src_vocab="run/vocab.src"
    > tgt_vocab="run/vocab.tgt"
    :: size=(NumSamples: 3mil=3000000 5mil=5000000 10mil=10000000)
    :: cuda_devices=@
{
    source ${activate}

    onmt_build_vocab -config ${yaml} -n_sample ${size}

    export CUDA_VISIBLE_DEVICES="${cuda_devices}"

    onmt_train -config ${yaml}

    ln -s run/model* ${model}
}


task devtest
    < devtest_texts=@digital_corpus
    < analyzer=$uppercase_ess@analyzer
    < cg=$cg@scripts
    < format_for_cg=$preprocess_analyses@scripts
    < word2analyses=@scripts
    < unanalyzed=$devtest_unanalyzed@scripts
    < make_devtest=@scripts
    < tokenize_char=@scripts
    > src_devtest="src-devtest.txt"
    > tgt_devtest="tgt-devtest.txt"
{
    # (1) run the fst over the devtest texts
    cat ${devtest_texts}/* | tr ' ' '\n' | grep -v '^[\n\t\s]*$' | flookup ${analyzer} > analyzed.tsv

# (2) format analyses to cg format
    python ${format_for_cg} --input_path="analyzed.tsv" > formatted.txt
    cat "formatted.txt" | vislcg3 --grammar ${cg} > analyzed_cg.txt

    # (3) replace +? with manually proposed analyses
    python3 ${word2analyses} --cg_output="analyzed_cg.txt" --json_name="word2analyses.json" --unanalyzed=${unanalyzed} --unanalyzed_cg=unanalyzed_cg

    # (4) make devtest tsv
    python3 ${make_devtest} word2analyses.json --output="devtest.tsv"
    sed -i '/^+?/d' devtest.tsv
    sed -i '/.*?.*/d' devtest.tsv

    # (5) initial cleanup (so tokenize.sh doesn't also tokenize cg output)
    #rm analyzed* *.json formatted.txt unanalyzed_cg

    # (6) tokenize devtest tsv
    ${tokenize_char} .

    # (7) cleanup
    #rm devtest.tsv

    mv devtest.surface src-devtest.txt
    sed -i 's/[A-Z]/\L&/g' src-devtest.txt 

    mv devtest.underlying tgt-devtest.txt
    sed -i 's/^[A-Z]/\L&/g' tgt-devtest.txt 
}


task neural_devtest_accuracy
    < model=@train_model
    < neural_wer=@scripts
    < analyzer=$uppercase@analyzer
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    > predictions="devtest_predictions.txt"
    > accuracy="accuracy.txt"
    :: n_best=@
    :: logreg=@
{
    onmt_translate -model ${model} -src ${src_devtest} -output ${predictions} -gpu 0 -verbose -n_best ${n_best}

    python2.7 ${neural_wer} ${analyzer} ${src_devtest} ${predictions} ${tgt_devtest} ${n_best} ${logreg} > ${accuracy}

    deactivate
}


task fst_devtest_accuracy
    < itemquulteki=@parser
    < l2s=$uppercase@analyzer
    < l2is=$l2is@analyzer
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    < script=$fst_wer@scripts
    > accuracy="accuracy.txt"
{
    cat ${src_devtest} | tr -d [:blank:] > src_devtest.txt
    cat ${tgt_devtest} | tr -d [:blank:] > tgt_devtest.txt

    ${itemquulteki} --name="main" --l2s=${l2s} --l2is=${l2is} --sentences=src_devtest.txt --output-json > devtest_predictions.json

    python3 ${script} devtest_predictions.json tgt_devtest.txt > ${accuracy}
}


task prev_neural_devtest
    < neural_wer=@scripts
    < analyzer=$uppercase@analyzer
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    > results="results"
    :: model_dir=@
    :: n_best=@
    :: logreg=@
{
    mkdir results

    for dirname in ${model_dir}/*; do
        onmt_translate -model "${dirname}/model.pt" -src ${src_devtest} -output "${dirname}_predictions.txt" -gpu 0 -verbose -n_best ${n_best}

        python2.7 ${neural_wer} ${analyzer} ${src_devtest} "${dirname}_predictions.txt" ${tgt_devtest} ${n_best} ${logreg} > "${dirname}_accuracy.txt"

        mv "${dirname}_predictions.txt" ${results}
        mv "${dirname}_accuracy.txt" ${results}

    done

    #rm manual_error_analysis.csv
}


task eval_goldtest
    < itemquulteki=@parser
    < l2s=$uppercase@analyzer
    < l2is=$l2is@analyzer
    < tokenize_char=@scripts
    < fst_wer=@scripts
    < neural_wer=@scripts
    > neural_results="neural_results"
    > fst_results="fst_results/fst_accuracy.txt"
    :: src_goldtest=@
    :: tgt_goldtest=@
    :: n_best=@
    :: model_dir=@
    :: logreg=@
{
    # -----------------
    # make goldtest set 
    # -----------------
    #mkdir goldtest
    #sed -i 's/	/\n/g' | sed -i 's/^[A-Z]/\L&/g' ${goldtest_surface} 
    #sed -i 's/	/\n/g' | sed -i 's/^[A-Z]/\L&/g' ${goldtest_underlying}
    #mv ${goldtest_surface} goldtest/src-goldtest.txt
    #mv ${goldtest_underlying} goldtest/tgt-goldtest.txt

    # --------
    # fst eval 
    # --------
    mkdir fst_results

    ${itemquulteki} --name="main" --l2s=${l2s} --l2is=${l2is} --sentences=${src_goldtest} --output-json > analyses.json

    python3 ${fst_wer} analyses.json ${tgt_goldtest} > ${fst_results}

    mv analyses.json fst_results/fst_predictions.json

    # -----------
    # neural eval
    # -----------
    paste ${tgt_goldtest} ${src_goldtest} > goldtest.tsv
    ${tokenize_char} .

    mkdir ${neural_results}

    for dirname in ${model_dir}/*; do
        onmt_translate -model "${dirname}/model.pt" -src goldtest.surface -output "${dirname}_predictions.txt" -gpu 0 -verbose -n_best ${n_best}

        python2.7 ${neural_wer} ${l2s} goldtest.surface "${dirname}_predictions.txt" goldtest.underlying ${n_best} ${logreg} >> "${dirname}_accuracy.txt"

        mv "${dirname}_predictions.txt" ${neural_results}
        mv "${dirname}_accuracy.txt" ${neural_results}
    done

    # cleanup
    rm goldtest.tsv manual_error_analysis.csv
}


task prelim_experiment
    < devtest_texts=@digital_corpus
    < texts_without_devtest=@digital_corpus
    < analyzer=$uppercase_ess@analyzer
    < cg=$cg@scripts
    < format_for_cg=$preprocess_analyses@scripts
    < word2analyses=@scripts
    < make_devtest=@scripts
    < tokenize_char=@scripts
    < partition_data=@scripts
    < neural_wer=@scripts
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    > src_train="data/src-train.txt"
    > tgt_train="data/tgt-train.txt"
    > src_val="data/src-val.txt"
    > tgt_val="data/tgt-val.txt"
    > model="./model.pt"
    > predictions="devtest_predictions.txt"
    > accuracy="accuracy.txt"
    :: world_size=@
    :: gpu_ranks=@
    :: cuda_devices=@
    :: n_best=@
    :: logreg=@
{
    # ---------------------------
    # STEP 1: prep training data
    # ---------------------------
    # (a) run the fst over digital corpus
    cat ${texts_without_devtest}/* ${devtest_texts}/* | tr ' ' '\n' | grep -v '^[\n\t\s]*$' | flookup ${analyzer} \; > analyzed.tsv # whole corpus
    #cat ${texts_without_devtest}/* | tr ' ' '\n' | grep -v '^[\n\t\s]*$' | flookup ${analyzer} \; > analyzed.tsv # corpus minus devtest

    # (b) format analyses to cg format and convert to json format
    python ${format_for_cg} --input_path="analyzed.tsv" > formatted.txt
    cat "formatted.txt" | vislcg3 --grammar ${cg} > analyzed_cg.txt
    python3 ${word2analyses} --cg_output="analyzed_cg.txt" --json_name="prelim.json"

    # (c) select one analysis per word (shortest analysis, random analysis if there are multiple shortest)
    python3 ${make_devtest} "prelim.json" --output="prelim.tsv"

    # (d) delete unanalyzed words, lowercase, partition into train and val sets, tokenize
    sed -i '/^+?/d' prelim.tsv
    sed -i 's/^[A-Z]/\L&/g' prelim.tsv

    ${partition_data} prelim.tsv

    mkdir data
    mv train.tsv val.tsv data
    ${tokenize_char} data

    # cleanup
    rm analyzed* formatted.txt prelim.* data/train.tsv data/val.tsv

    # -------------------------------
    # STEP 2: set up config yaml file
    # -------------------------------
    yaml="config.yaml"

    echo "# prelim neural experiment yaml" > ${yaml}

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
    echo "        path_src: data/src-train.txt" >> ${yaml}
    echo "        path_tgt: data/tgt-train.txt" >> ${yaml}
    echo "    valid:" >> ${yaml}
    echo "        path_src: data/src-val.txt" >> ${yaml}
    echo "        path_tgt: data/tgt-val.txt" >> ${yaml}

    echo "" >> ${yaml}

    echo "# vocabulary files that were just created" >> ${yaml}
    echo "src_vocab: run/vocab.src" >> ${yaml}
    echo "tgt_vocab: run/vocab.tgt" >> ${yaml}

    echo "" >> ${yaml}

    echo "# GPUs" >> ${yaml}
    echo "world_size:" ${world_size} >> ${yaml}
    echo "gpu_ranks:" ${gpu_ranks} >> ${yaml}

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

    # -------------------
    # STEP 3: train model
    # -------------------
    num_samples=$(wc -l data/src-train.txt)
    onmt_build_vocab -config ${yaml} -n_sample ${num_samples}

    export CUDA_VISIBLE_DEVICES="${cuda_devices}"

    onmt_train -config ${yaml}

    ln -s run/model* ${model}

    # ---------------------------------
    # STEP 4: evaluate model on devtest
    # ---------------------------------
    onmt_translate -model ${model} -src ${src_devtest} -output ${predictions} -gpu 0 -verbose -n_best ${n_best}

    python2.7 ${neural_wer} ${analyzer} ${src_devtest} ${predictions} ${tgt_devtest} ${n_best} ${logreg} > ${accuracy}
}


task hyperparameter_tuning
    < src_train=@prelim_experiment
    < tgt_train=@prelim_experiment
    < src_val=@prelim_experiment
    < tgt_val=@prelim_experiment
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    < neural_wer=@scripts
    < analyzer=$uppercase_ess@analyzer
    :: cuda_devices=@
    :: world_size=@
    :: gpu_ranks=@
    :: n_best=@
    :: logreg=@
{
    declare -A small=(["embedding_dim"]=64 ["hidden_dim"]=256 ["num_layers"]=2)
    declare -A medium=(["embedding_dim"]=128 ["hidden_dim"]=512 ["num_layers"]=3)
    declare -A large=(["embedding_dim"]=256 ["hidden_dim"]=1024 ["num_layers"]=4)

    learning_rates=(0.1)

    # -------------------------------
    # STEP 1: set up config yaml file
    # -------------------------------
    for lr in ${learning_rates[@]}; do
        mkdir large-${lr}

        yaml="config.yaml"
    
        echo "# hyperparameter tuning yaml" > ${yaml}
    
        echo "" >> ${yaml}
    
        echo "# where the samples will be written" >> ${yaml}
        echo "save_data: large-${lr}/run" >> ${yaml}
        echo "# where the vocab(s) will be written" >> ${yaml}
        echo "src_vocab: large-${lr}/run/vocab.src" >> ${yaml}
        echo "tgt_vocab: large-${lr}/run/vocab.tgt" >> ${yaml}
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
        echo "src_vocab: large-${lr}/run/vocab.src" >> ${yaml}
        echo "tgt_vocab: large-${lr}/run/vocab.tgt" >> ${yaml}
    
        echo "" >> ${yaml}
    
        echo "# GPUs" >> ${yaml}
        echo "world_size:" ${world_size} >> ${yaml}
        echo "gpu_ranks:" ${gpu_ranks} >> ${yaml}
    
        echo "" >> ${yaml}
    
        echo "# hyperparams" >> ${yaml}
        echo "encoder_type: brnn" >> ${yaml}
        echo "word_vec_size: ${large[embedding_dim]}" >> ${yaml}
        echo "rnn_size: ${large[hidden_dim]}" >> ${yaml}
        echo "layers: ${large[num_layers]}" >> ${yaml}
        echo "early_stopping: 5" >> ${yaml}

        echo "" >> ${yaml}

        echo "learning_rate: ${lr}" >> ${yaml}
    
        echo "" >> ${yaml}
    
        echo "# where to save the checkpoints" >> ${yaml}
        echo "save_model: large-${lr}/run/model" >> ${yaml}
        echo "#save_checkpoint_steps: 500" >> ${yaml}
        echo "#train_steps: 1000" >> ${yaml}
        echo "#valid_steps: 10000" >> ${yaml}
        echo "keep_checkpoint: 1" >> ${yaml}
    
        # -------------------
        # STEP 3: train model
        # -------------------
        num_samples=$(wc -l ${src_train})
        onmt_build_vocab -config ${yaml} -n_sample ${num_samples}
    
        export CUDA_VISIBLE_DEVICES="${cuda_devices}"
    
        onmt_train -config ${yaml}

        # ----------------------
        # STEP 4: evaluate model 
        # ----------------------
        onmt_translate -model large-${lr}/run/model* -src ${src_devtest} -output large-${lr}_devtest_predictions.txt -gpu 0 -verbose -n_best ${n_best}

        python2.7 ${neural_wer} ${analyzer} ${src_devtest} large-${lr}_devtest_predictions.txt ${tgt_devtest} ${n_best} ${logreg} > large-${lr}_accuracy.txt
    done
}

task eval_hyperparameter_tuning
    < src_devtest=@devtest
    < tgt_devtest=@devtest
    < get_wer=$neural_wer@scripts
    < analyzer=$uppercase_ess@analyzer
    :: n_best=@
    :: logreg=@
{
   for dirname in /home/echen41/neural-experiments-thesis/tuning/*; do
       onmt_translate -model ${dirname}/run/model* -src ${src_devtest} -output ${dirname}_devtest_predictions.txt -gpu 0 -verbose -n_best ${n_best}
    
       python2.7 ${get_wer} ${analyzer} ${src_devtest} ${dirname}_devtest_predictions.txt ${tgt_devtest} ${n_best} ${logreg} > ${dirname}_accuracy.txt
   done
}

#plan make_devtest 
#{
#    reach devtest
#}

#plan run_prelim_experiment 
#{
#    reach prelim_experiment
#}

#plan neural_analyzer 
#{
#    reach neural_devtest_accuracy via (GetCounts: "conditional_frac") * (SampleMethod: "3A") * (NumSamples: 10mil)
#}

#plan fst_devtest_accuracy_results 
#{
#    reach fst_devtest_accuracy
#}

#plan prev_neural_devtest_results 
#{
#    reach prev_neural_devtest
#}

plan goldtest_eval_results 
{
    reach eval_goldtest
}

#plan tune_hyperparameters 
#{
#    reach hyperparameter_tuning
#}

#plan delete 
#{
#    reach eval_hyperparameter_tuning
#}
