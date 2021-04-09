#!/bin/bash

master_dir="/home/echen41/neural-experiments-thesis/make-dataset/"

output_dir="/home/echen41/neural-experiments-thesis/make-dataset/cg3-output"
if [ ! -d ${output_dir} ]; then
    mkdir ${output_dir}
fi

#---------------------
# to generate dev set
#---------------------
if [ $1 == "devset" ]; then
    folder="/home/echen41/neural-experiments-thesis/make-dataset/devset-files/texts/*"

    for text in ${folder}; do
        base=$(basename ${text} .ess_content)

        # for each text, get analyses from the FST analyzer
        cat ${text} | tr ' ' '\n' | grep -v "^[\n\t\s]*$" | flookup ${master_dir}/neural_uppercase.fomabin > ${output_dir}/${base}.analyses

        # prep the analyses for the constraint grammar
        cat ${output_dir}/${base}.analyses | python scripts/format_analyses_for_cg.py > ${output_dir}/${base}.input

        # run the constraint grammar
        cat ${output_dir}/${base}.input | vislcg3 --grammar ${master_dir}/yupik.cg3 > ${output_dir}/${base}.output
    done
#---------------------------
# to generate training sets 
#---------------------------
elif [ $1 == "dataset" ]; then
    texts="/home/echen41/digital_corpus/ess/*"

    for folder in ${texts}; do
        for text in ${folder}/ess_content/*; do
            base=$(basename ${text}.ess_content)
    
            # for each text, get analyses from the FST analyzer
            cat ${text} | tr ' ' '\n' | grep -v "^[\n\t\s]*$" | flookup ${master_dir}/neural_uppercase.fomabin > ${output_dir}/${base}.analyses
    
            # prep the analyses for the constraint grammar
            cat ${output_dir}/${base}.analyses | python scripts/format_analyses_for_cg.py > ${output_dir}/${base}.input
    
            # run the constraint grammar
            cat ${output_dir}/${base}.input | vislcg3 --grammar ${master_dir}/yupik.cg3 > ${output_dir}/${base}.output
        done
    done
fi

# concatenate constraint grammar output
cat ${output_dir}/*.output > ${master_dir}/stories.output

# cleanup
rm -rf ${output_dir}
