

DATE=$(date +"%m-%d-%Y");
module load anaconda3


EXPS=(tc jp-jc jp-cn jp-ov)
for e in ${EXPS[@]}; do
	echo images for $e
	echo figures kroneckers
	python src/scripts/make_figures_fixed.py --input-csv exp_paolo/${e}-${DATE}.csv --image-folder einstein_images/ --bf 0.1 --mh 0.001 --img_format pdf
	
	#echo big_krons
	#python src/scripts/make_figures_fixed.py --input-csv big_kron/big-kron-${e}-${DATE}.csv --image-folder big_kron_images/ --bf 0.1 --mh 0.001 --img_format pdf

	echo figures real
	python src/scripts/make_figures_fixed.py --input-csv exp_paolo_real/${e}-real-12-31-2021.csv --image-folder einstein_images_real/ --kron False --img_format pdf
done

python src/scripts/make_figures_fixed.py --input-csv exp_paolo/4c-${DATE}.csv --image-folder einstein_images/ --bf 0.1 --mh 0.1 --img_format pdf
