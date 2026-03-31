# environment setting
export LD_LIBRARY_PATH=/usr/local/cuda/compat:$LD_LIBRARY_PATH
export LD_PRELOAD=/usr/local/cuda/compat/libcuda.so
cd /share/project/xzy_datas_models/infinity/Finance/Benchmarks/PIXIU
source /share/project/xiaozhiyou/miniconda3/bin/activate
conda activate pixiu

# 需要进入下面这个文件，去修改模型的路径：/share/project/xzy_datas_models/infinity/Finance/Benchmarks/PIXIU/scripts/run_evaluation_baai.sh
# ---- > 注意：修改 --model_args 后面的参数，将pretrained和tokenizer修改成训完的模型
# ！！！执行完上述操作之后，在运行eval脚本！！！
bash scripts/run_evaluation_baai.sh