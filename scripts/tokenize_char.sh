#-----------------------------------------------------
# inserts a space between each token of the input,
# where a token is either a char, a morphophonological
# symbol or a tag
#-----------------------------------------------------

#dirname=""

#if [ $1 == "devset" ]; then
#    dirname="/home/echen41/neural-experiments-thesis/make-dataset/devset-files"
#elif [ $1 == "dataset" ]; then
#    dirname="/home/echen41/neural-experiments-thesis/make-dataset/data"
#fi

for f in $1; do
#	surface=${f%.in}.char

#	sed 's,\([A-Z]\), \1,g; s,\([a-z]\), \1,g;	s, ,,' $f > $surface

	underlying=${f%.tsv}.underlying
	surface=${f%.tsv}.surface

    # tokenizes the underlying forms
	cut -f1 $f | \
	sed 's,\^, \^,g' | \
	sed 's,(, (,g' | \
	sed 's,\~, \~,g' | \
	sed 's,\([^\~]\)s,\1 s,g' | \
	sed 's,\([^\~s]\)f,\1 f,g' | \
	sed 's,\([^\~]\)h,\1 h,g' | \
	sed 's,^s,s ,' | \
	sed 's,^h,h ,' | \
	sed 's,^f,f ,' | \
	sed 's,hh,h h,' | \

	sed 's,\([adegiklmnpqrtuvyz]\), \1,g' | \
	sed 's,\([A-Z]\),\1 ,g' | \
	sed 's, ,,' | \
	sed "s,', ',g" | \
	sed 's,\[, \[,g' | \
	sed 's,+, +,g' | \
	sed 's,=, =,g' | \

	sed 's,@, @,g' | \
	sed 's,\([^@]\)\*,\1 \*,g' | \
	sed 's,\([^–]\)–,\1 –,g' | \
	sed 's,%, %,g' | \
	sed 's,:, :,g' | \
	sed 's,\/, \/,g' | \
	sed 's,\([^-]\)w,\1 w,g' | \
	sed 's,-, -,g' | \
	sed -e :1 -e 's,\(\[[^]]*\)[[:space:]],\1,g;t1' | \
	sed -e :1 -e 's,\(([^)]*\)[[:space:]],\1,g;t1' | \
    sed 's,\([0-9]\)\([a-z]\),\1 \2,g' | \
    sed 's,\([0-9]\)-,\1 -,g' | \
    sed 's,\([0-9]\)(,\1 (,g' > $underlying

    # tokenizes the surface forms, split by space
	cut -f2 $f | \
    sed 's,\([A-Z]\), \1,g' | \
	sed 's,\([a-z]\), \1,g' | \
    sed 's,ʼ, ʼ,g' | \
	sed 's,-, -,g' | \
	sed 's, ,,' | \
    sed 's,\([0-9]\)\([a-z]\),\1 \2,g' | \
    sed 's,\([0-9]\)-,\1 -,g' > $surface
done

# rename files
#if [ $1 == "devset" ]; then
#    mv $dirname/devset.surface $dirname/src-dev.txt
#    mv $dirname/devset.underlying $dirname/tgt-dev.txt
#elif [ $1 == "dataset" ]; then
mv $1/train.surface $1/src-train.txt
mv $1/train.underlying $1/tgt-train.txt
mv $1/val.surface $1/src-val.txt
mv $1/val.underlying $1/tgt-val.txt
mv $1/testset.surface $1/src-test.txt
mv $1/testset.underlying $1/tgt-test.txt
#fi
