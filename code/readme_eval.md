# EvalPlus评测

本节介绍如何在 **HumanEval** 和 **MBPP** 基准测试上使用 **EvalPlus** 运行模型评估。

## 1. 克隆仓库

```bash
git clone https://github.com/evalplus/evalplus.git
cd evalplus
```

## 2. 配置环境
建议先创建一个干净的 Python 环境，然后通过源码以可编辑模式安装 EvalPlus：
```bash
python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e .
```
如果计划使用 `vllm` 后端，请根据需求在环境中安装额外依赖。

## 3. 运行评测
首先设置模型路径或模型名称：
```bash
export MODEL=your_model_name_or_path
```

MBPP基准测试
```bash
evalplus.evaluate --model $MODEL \
                  --dataset mbpp \
                  --backend vllm \
                  --greedy
```

HumanEval基准测试
```bash
evalplus.evaluate --model $MODEL \
                  --dataset humaneval \
                  --backend vllm \
                  --greedy
```

## 4. 参数说明
- `--model`: 模型路径
- `--dataset`：选择benchmark进行测试。
- `--backend`：推理后端。
- `--greedy`：在评测过程中使用贪心解码。

EvalPlus 将通过 `evalplus.evaluate` 入口生成并评估结果。


# LiveCodeBench评测

本节说明如何使用 **LiveCodeBench** 对训练完成后的模型进行评测。  
在开始评测之前，需要先完成环境配置，并将待评测模型注册到 LiveCodeBench 的模型列表中。

## 1. 环境准备

请先按照 LiveCodeBench 官方要求完成环境安装，确保相关依赖已经正确配置。  
建议在独立的 Python 环境中运行评测，避免与训练环境产生冲突。

## 2. 注册待评测模型

在运行评测前，需要先将训练好的模型添加到：

```bash
LiveCodeBench/lcb_runner/lm_styles.py
```
文件中的 LanguageModelList 里。

示例如下：
```python
LanguageModel(
    "/path/to/your/Qwen3-4B-sft",
    "Qwen3-4B-sft",
    LMStyle.CodeQwenInstruct,
    datetime(2024, 6, 30),
    link="",
),
```

## 3. 启动评测
完成模型注册后，即可使用以下命令启动 LiveCodeBench 的代码生成评测：
```bash
python -m lcb_runner.runner.main \
    --model /path/to/your/model \
    --scenario codegeneration \
    --evaluate \
    --release_version release_v6 \
    --n 1 \
    --max_tokens 4096 \
    --temperature 0.0 \
    --top_p 0.95
```

## 4. 参数说明
上述命令中的主要参数说明如下：
- `--model`：待评测模型路径，需要与注册到`LanguageModelList`中的模型一致
- `--scenario`：指定评测任务
- `--evaluate`：开启评测流程
- `--release_version`：指定所使用的 LiveCodeBench 数据版本
- `--n`：每个样本生成 n 个候选结果
- `--max_tokens`：模型生成的最大 token 数
- `--temperature`：采样温度
- `--top_p`：采样top_p