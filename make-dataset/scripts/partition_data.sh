#--------------------------
# partitions dataset into a 
#   * training set
#   * validation set
#   * test set
#--------------------------
f="/home/echen41/neural-experiments-thesis/make-dataset/data.txt"

rm -rf data
mkdir data

train=data/train.tsv
valid=data/val.tsv
testset=data/testset.tsv

total=$(wc -l < $f)

# uses a 0.8 : 0.1 : 0.1 ratio 
numTrain=$(echo "$total*0.8" | bc | xargs printf %.0f)
numValid=$(echo "($total - $numTrain) / 2" | bc | xargs printf %.0f)
numTest=$(echo "$total - $numTrain - $numValid" | bc | xargs printf %.0f)

#numValid=$(echo "$total*0.01" | bc | xargs printf %.0f)
#numTest=$(echo "$total*0.19" | bc | xargs printf %.0f)
#numTrain=$(echo "$total - $numTest - $numValid" | bc | xargs printf %.0f)

shuf -n $numTrain $f > $train

comm -23 <(sort $f) <(sort $train) | shuf -n $numValid > $valid

comm -23 <(sort $f) <(cat $train $valid | sort) > $testset

shuf -o $train < $train
shuf -o $valid < $valid
shuf -o $testset < $testset
