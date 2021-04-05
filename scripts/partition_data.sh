#--------------------------
# partitions dataset into a 
#   * training set
#   * validation set
#   * test set
#--------------------------
train=train.tsv
valid=val.tsv
testset=testset.tsv

total=$(wc -l < $1)

# uses a 0.8 : 0.1 : 0.1 ratio 
numTrain=$(echo "$total*0.8" | bc | xargs printf %.0f)
numValid=$(echo "($total - $numTrain) / 2" | bc | xargs printf %.0f)
numTest=$(echo "$total - $numTrain - $numValid" | bc | xargs printf %.0f)

#numValid=$(echo "$total*0.01" | bc | xargs printf %.0f)
#numTest=$(echo "$total*0.19" | bc | xargs printf %.0f)
#numTrain=$(echo "$total - $numTest - $numValid" | bc | xargs printf %.0f)

shuf -n $numTrain $1 > $train

comm -23 <(sort $1) <(sort $train) | shuf -n $numValid > $valid

comm -23 <(sort $1) <(cat $train $valid | sort) > $testset

shuf -o $train < $train
shuf -o $valid < $valid
shuf -o $testset < $testset
