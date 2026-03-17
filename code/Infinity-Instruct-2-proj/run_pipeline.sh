WORK=/share/project/guotianyu/Infinity-Instruct-2-proj/sandbox_work
PROJ=/share/project/guotianyu/Infinity-Instruct-2-proj

source /share/project/miaode/miniconda3/etc/profile.d/conda.sh
conda activate /share/project/guotianyu/venv/df-infi

PY=/share/project/guotianyu/venv/df-infi/bin/python


cd "$PROJ/nsjail"

./nsjail \
  --mode o \
  --time_limit 15 \
  --max_cpus 1 \
  --rlimit_as 2048 \
  --rlimit_cpu 15 \
  --rlimit_nofile 256 \
  --rlimit_nproc 64 \
  --bindmount_ro "$PROJ:$PROJ" \
  --bindmount "$WORK:$WORK" \
  --bindmount "$WORK/tmp:/tmp" \
  --cwd "$WORK" \
  -- $PY "$PROJ/DataFlow/run_pipelines/api_pipelines/code_code_to_sft_data_pipeline_test.py"