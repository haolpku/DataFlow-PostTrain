# Eval Guide (Medical + Finance)

本文档基于以下脚本整理：

- `medical/medical_eval.sh`
- `medical/finance_eval.sh`

目标：完成模型服务启动、医疗任务评测（MedXpertQA）以及金融任务评测（PIXIU）。

---

## 0. 前置准备

- 确认已经有可用模型权重路径。
- 建议使用 `tmux` 分开运行：
  - 一个窗口跑模型服务；
  - 一个窗口跑推理与评测。

---

## 1. Medical Eval (MedXpertQA)

### 1.1 启动模型服务（sglang）

在一个新的 `tmux` 窗口执行：

```bash
export LD_LIBRARY_PATH=/usr/local/cuda/compat:$LD_LIBRARY_PATH
export LD_PRELOAD=/usr/local/cuda/compat/libcuda.so

cd /share/project/xiaozhiyou/DataFlow/workspace
source /share/project/miaode/miniconda3/bin/activate
conda activate sglang
```

启动前需要先修改：

- `/share/project/xiaozhiyou/DataFlow/workspace/launch_reward_server.sh`
  - 模型路径
  - 模型名（serve 的 model name）

修改完成后启动服务：

```bash
bash launch_reward_server.sh
```

同时确保在以下文件中注册同名模型：

- `/share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/config/model_info.json`

---

### 1.2 执行推理脚本

在另一个窗口执行：

```bash
cd /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval
source /share/project/xiaozhiyou/miniconda3/bin/activate
conda activate pixiu
```

执行前修改：

- `/share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/scripts/run_baai.sh`
  - `models=${1:-"qwen3_4b_instruct"}` 改为你实际 serve 的模型名
- `/share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/config/model_info.json`
  - 确认已添加同名模型配置

运行：

```bash
bash scripts/run_baai.sh
```

---

### 1.3 执行评估脚本

执行前修改：

- `/share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval/eval.py`
  - 将 `model = "qwen3_4b_instruct"` 改成你当前 serve 的模型名

然后执行：

```bash
cd /share/project/xzy_datas_models/infinity/Medical/Benchmarks/MedXpertQA/eval
source /share/project/xiaozhiyou/miniconda3/bin/activate
conda activate pixiu
python3 eval.py
```

---

## 2. Finance Eval (PIXIU)

在 `PIXIU` 路径下执行：

```bash
cd PIXIU
conda activate pixiu
```

执行前先修改：

- `/share/project/xzy_datas_models/infinity/Finance/Benchmarks/PIXIU/scripts/run_evaluation_baai.sh`
  - 修改 `--model_args` 参数
  - 将其中 `pretrained` 和 `tokenizer` 指向训练后的模型

修改完成后运行：

```bash
bash scripts/run_evaluation_baai.sh
```

---

## 3. 常见检查项

- 模型服务名必须和以下位置保持一致：
  - `launch_reward_server.sh`
  - `model_info.json`
  - `run_baai.sh`
  - `eval.py`
- `conda` 环境是否正确：
  - 服务：`sglang`
  - 评测：`pixiu`
- 若结果异常，优先检查：
  - 模型路径是否存在；
  - tokenizer 是否与模型匹配；
  - 服务是否已成功启动并可访问。
