# environment setting
export LD_LIBRARY_PATH=/usr/local/cuda/compat:$LD_LIBRARY_PATH
export LD_PRELOAD=/usr/local/cuda/compat/libcuda.so

# 要先开一个serving tmux，serve一个model，在tmux环境下执行下面操作：
cd /share/project/xiaozhiyou/DataFlow/workspace
source /share/project/miaode/miniconda3/bin/activate
conda activate sglang
# 修改 /share/project/xiaozhiyou/DataFlow/workspace/launch_reward_server.sh 文件里的model路径，以及model name
# 修改完后，启动serving
bash launch_reward_server.sh
# 要求去 /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/config/model_info.json 文件里添加serve的model name

# 1. 完成模型启动服务之后，执行model inference逻辑
cd /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval
source /share/project/xiaozhiyou/miniconda3/bin/activate
conda activate pixiu
# 修改 /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/scripts/run_baai.sh 文件
# 修改 models=${1:-"qwen3_4b_instruct"} 参数，改成serve的model
# 在 /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/config/model_info.json 文件里添加serve的model name
# 修改完后，执行eval脚本
bash scripts/run_baai.sh

# 2. 执行 eval 评估逻辑
# 修改 /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/eval.py 文件
# 具体修改第7行，model = "qwen3_4b_instruct"，改成 serve 的 model name
# 可以开一个tmux，执行 eval.py 文件，查看结果
cd /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval
source /share/project/xiaozhiyou/miniconda3/bin/activate
conda activate pixiu
python3 eval.py