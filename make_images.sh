

EXPS=(tc jp-jc jp-cn jp-ov)
for e in ${EXPS[@]}; do
	echo images for $e
	echo figures kroneckers
	python src/scripts/make_comparison_images.py --input-csv exp_paolo/${e}-kron.csv --image-folder kronecker_graphs_images/ --bf 0.1 --mh 0.001 --img_format pdf
	
	echo figures real
	python src/scripts/make_comparison_images.py --input-csv exp_paolo_real/${e}-real.csv --image-folder real_graphs_images/ --kron False --img_format pdf
done

python src/scripts/make_scaling_plots.py
