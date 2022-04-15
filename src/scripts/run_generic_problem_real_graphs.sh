export problem=${1}
export BENCH_PATH=${2}
export GRAPHS_PATH=${3}
export RESULTS_DIR=${4}

THREADS=( 32 )

if [ "${problem}" = "tc" ]; then
  export BINARIES=( ${problem}_base ${problem}_bf ${problem}_1h ${problem}_doulion ${problem}_colorful )
else
  export BINARIES=( ${problem}_base ${problem}_bf ${problem}_1h)
fi

PARAM_THs=(0.00003 0.0001 0.0003 0.001 0.003 0.01 0.03 0.1 0.3 0.5 1.0 2.0)
CLUSTER=0.1

function create_launch {
  PREFIX_OUTCOME=results

  export OMP_NUM_THREADS=${T}

  script_name=___tmp_script_${BINARY}_${T}_G-${GRAPH_NAME}_${PARAM_TH}_${PARAM_K}___

  script_folder=${RESULTS_DIR}/${script_name}___exec_dir


  out_fname=${PREFIX_OUTCOME}_${BINARY}___G-${GRAPH_NAME}___TH-${PARAM_TH}___K-${PARAM_K}___T-${T}

  is_new="TRUE"
  if [[ -d "${script_folder}" ]]; then
    if [[ -f "${script_folder}/__to_gather__${out_fname}.out" ]]; then
      if [[ -s "${script_folder}/__to_gather__${out_fname}.out" ]]; then 
        echo "experiment ${out_fname} exists already. Skipping"
        is_new="FALSE"
      fi
    fi
  fi

  if [[ "${is_new}" = "TRUE" ]]; then
    mkdir ${script_folder}
    echo ./${BENCH_PATH}/${BINARY} ${ARGS}
    ./${BENCH_PATH}/${BINARY} ${ARGS} > ${script_folder}/${out_fname}.out

    grep 'SSS' ${script_folder}/${out_fname}.out >> ${script_folder}/__to_gather__${out_fname}.out
    grep 'RRR' ${script_folder}/${out_fname}.out >> ${script_folder}/__to_gather__${out_fname}.out
  fi  
}

for T in ${THREADS[@]}; do
  export OMP_NUM_THREADS=${T}
  
  for fullpath in ${GRAPHS_PATH}/*.el; do

    if test -f "${fullpath}"; then
      GRAPH_FILE=$(basename -- "$fullpath")
      GRAPH_NAME="${GRAPH_FILE%.*}"
      FILE_EXT="${fullpath##*.}"

      echo "======= Processing graph ${GRAPH_NAME}"

      for BINARY in ${BINARIES[@]}; do
        approx_scheme=$(echo ${BINARY} | cut -d'_' -f 2)
        
        if [ "${approx_scheme}" = "base" ]; then
          export ARGS="-s -f ${fullpath} -a -n 1"
          create_launch
        elif [ "${approx_scheme}" = "doulion" ]; then
          export ARGS="-s -f ${fullpath} -a -n 1 -p 0.8"
          create_launch
        elif [ "${approx_scheme}" = "colorful" ]; then
          export ARGS="-s -f ${fullpath} -a -n 1 -p 0.5"
          create_launch
        elif [ "${approx_scheme}" = "kmv" ] || [ "${approx_scheme}" = "1h" ] || [ "${approx_scheme}" = "kh" ]; then
          for PARAM_TH in ${PARAM_THs[@]}; do
            export ARGS="-s -f ${fullpath} -t ${PARAM_TH} -n 1"
            create_launch
          done
        else
          for PARAM_TH in ${PARAM_THs[@]}; do
            export ARGS="-s -f ${fullpath} -t ${PARAM_TH} -b -1 -n 1"
            create_launch
          done
        fi
      done
    fi
  done
done



