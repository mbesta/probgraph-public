PROBLEMS=(tc)
KRON_SIZE=16
KRON_EDGES=128
OPTIONS="-g ${KRON_SIZE} -k ${KRON_EDGES} -y 0.1"

for PROB in ${PROBLEMS[@]}; do	
	echo "*******************************"
	echo "******RUNNING ${PROB} with BASELINE"
	./src/${PROB}_base ${OPTIONS}
	
	echo "******RUNNING ${PROB} with One-Hash"
	./src/${PROB}_1h ${OPTIONS} -t 0.01
	
	echo "******RUNNING ${PROB} with Bloom Filters"
	./src/${PROB}_bf ${OPTIONS} -t 0.5
done
