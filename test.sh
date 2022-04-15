PROBLEMS=(tc jp-jc jp-cn jp-ov 4c)
KRON_SIZE=17
KRON_EDGES=256

for PROB in ${PROBLEMS[@]}; do	
	echo "*******************************"
	echo "running ${PROB} with baseline"
	./src/${PROB}_base -g 17 -k 256
	
	echo "\n running ${PROB} with One-Hash"
	./src/${PROB}_1h -g 17 -k 256 -t 0.1
	
	echo "\n running ${PROB} with Bloom Filters"
	./src/${PROB}_bf -g 17 -k 256 -t 0.01
done
