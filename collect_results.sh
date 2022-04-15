PROBLEMS=(tc jp-jc jp-cn jp-ov)

for PROB in ${PROBLEMS[@]}; do
	echo collecting kronecker results for ${PROB}
	python src/scripts/collect_into_csv.py --input-dir kronecker_graph_results/${PROB}/ --output-name kronecker_graph_results/${PROB}.csv
done

for PROB in ${PROBLEMS[@]}; do
	echo collecting real graphs results for ${PROB}
	python src/scripts/collect_into_csv.py --input-dir real_graphs_results/${PROB}/ --output-name real_graphs_results/${PROB}.csv
done

for PROB in ${PROBLEMS[@]}; do
	echo collecting strong results for ${PROB}
	python src/scripts/collect_into_csv.py --input-dir scaling_experiments/strong_results/${PROB}/ --output-name scaling_experiments/strong_scaling_results_${PROB}.csv
done

for PROB in ${PROBLEMS[@]}; do
	echo collecting weak results for ${PROB}
	python src/scripts/collect_into_csv.py --input-dir scaling_experiments/weak_results/${PROB}/ --output-name scaling_experiments/weak_scaling_results_${PROB}.csv
done
