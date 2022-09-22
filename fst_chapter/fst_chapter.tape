global {
src_goldtest="/home/echen41/neural-experiments-thesis/goldtest/src-goldtest.txt"
}

global {
tgt_goldtest="/home/echen41/neural-experiments-thesis/goldtest/tgt-goldtest.txt"
}


task analyzer2020 
    :: url="git@github.com:SaintLawrenceIslandYupik/finite_state_morphology.git"
    :: tag=(Analyzer2020: "2.8")
    > uppercase
    > l2is
    > lexc="repo/ess.lexc"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && make uppercase.fomabin && make l2is.fomabin

    for f in *.fomabin ; do mv ${f} ../${f%.fomabin} ; done
}


task analyzer2018 
    :: url="git@github.com:dowobeha/foma.ess.git"
    :: tag=(Analyzer2018: "1.1")
    > l2s="ess.fomabin"
    > l2is="ess.lex.fomabin"
    > lexc="repo/ess.lexc"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && make ess.fomabin

    for f in *.fomabin ; do mv ${f} ..; done
}


task parser
     :: url="git@github.com:dowobeha/yupik-parser.git"
     :: tag=(Qamani2020: "1.4.0")
     > itemquulteki
{
    git clone --depth 1                \
              --single-branch          \
              -c advice.detachedHead=false \
              --branch ${tag} ${url} repo

    cd repo && swift build && mv .build/debug/itemquulteki ..
}


task scripts
    :: foma_url="https://raw.githubusercontent.com/mhulden/foma/master/foma/python/foma.py"
    :: neurexp_scripts_url="git@github.com:chenemile/neurexp-scripts-and-devtest.git"
    :: neurexp_scripts_tag=(Scripts: "0.0.9")
     > foma_py="foma.py"
     > tokenize_char="tokenize_char.sh"
     > fst_wer="get_fst_wer.py"
{
    git clone --depth 1                    \
              --single-branch              \
              -c advice.detachedHead=false \
              --branch ${neurexp_scripts_tag} ${neurexp_scripts_url} neurexp_scripts

    wget ${foma_url}

    mv neurexp_scripts/* .
}


task eval_goldtest
    < itemquulteki=@parser
    < l2s_2020=$uppercase@analyzer2020
    < l2is_2020=$l2is@analyzer2020
    < l2s_2018=$l2s@analyzer2018
    < l2is_2018=$l2is@analyzer2018
    < tokenize_char=@scripts
    < fst_script=$fst_wer@scripts
    > results_2020="2020_results/2020_accuracy.txt"
    > results_2018="2018_results/2018_accuracy.txt"
    :: src_goldtest=@
    :: tgt_goldtest=@
{
    # -----------------
    # make goldtest set 
    # -----------------
    #mkdir goldtest
    #sed -i 's/	/\n/g' | sed -i 's/^[A-Z]/\L&/g' ${goldtest_surface} 
    #sed -i 's/	/\n/g' | sed -i 's/^[A-Z]/\L&/g' ${goldtest_underlying}
    #mv ${goldtest_surface} goldtest/src-goldtest.txt
    #mv ${goldtest_underlying} goldtest/tgt-goldtest.txt

    # -------------
    # 2020 fst eval 
    # -------------
    mkdir 2020_results

    start="$(date +%s)"
    ${itemquulteki} --name="main" --l2s=${l2s_2020} --l2is=${l2is_2020} --sentences=${src_goldtest} --output-json > analyses.json
    end="$(date +%s)"

    python3 ${fst_script} analyses.json ${tgt_goldtest} > ${results_2020}

    duration=$((${end} - ${start}))
    echo "----------------------------" >> ${results_2020}
    echo "runtime (over full goldtest)" >> ${results_2020}
    echo "----------------------------" >> ${results_2020}
    echo "runtime = ${duration} seconds" >> ${results_2020}

    mv analyses.json 2020_results/2020_predictions.json

    # -------------
    # 2018 fst eval 
    # -------------
    mkdir 2018_results

    start="$(date +%s)"
    ${itemquulteki} --name="main" --l2s=${l2s_2018} --l2is=${l2is_2018} --sentences=${src_goldtest} --output-json > analyses.json
    end="$(date +%s)"

    python3 ${fst_script} analyses.json ${tgt_goldtest} > ${results_2018}

    duration=$((${end} - ${start}))
    echo "----------------------------" >> ${results_2018}
    echo "runtime (over full goldtest)" >> ${results_2018}
    echo "----------------------------" >> ${results_2018}
    echo "runtime = ${duration} seconds" >> ${results_2018}

    mv analyses.json 2018_results/2018_predictions.json
}


plan goldtest_eval_results 
{
    reach eval_goldtest
}
