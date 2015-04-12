:
VOLUME=0.3
for n in todo/*.ogg ; do
    echo $n
    sox $n -r 44100 -v $VOLUME -c 1 `basename $n`
done
