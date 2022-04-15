PROBLEMS=(tc jp-jc jp-cn jp-ov)
KRON_SIZE=17
KRON_EDGES=256

for PROB in ${PROBLEMS[@]}; do
	./src/${PROB}_base -g 17 -k 256
  ./src/${PROB}_1h -g 17 -k 256 -t 0.1
  ./src/${PROB}_bf -g 17 -k 256 -t 0.01
done
