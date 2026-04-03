# Code 评测说明（EvalPlus + LiveCodeBench）

---

## 一、EvalPlus（HumanEval / MBPP）

在 [evalplus](https://github.com/evalplus/evalplus) 仓库中评测 HumanEval 与 MBPP。

### 1. 获取代码

```bash
git clone https://github.com/evalplus/evalplus.git
cd evalplus
```

### 2. 环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

若使用 **vLLM** 后端，需额外安装对应依赖。

### 3. 运行

```bash
export MODEL=your_model_name_or_path

evalplus.evaluate --model "$MODEL" \
    --dataset mbpp \
    --backend vllm \
    --greedy

evalplus.evaluate --model "$MODEL" \
    --dataset humaneval \
    --backend vllm \
    --greedy
```

### 4. 参数简表

| 参数 | 含义 |
|------|------|
| `--model` | 模型路径或标识 |
| `--dataset` | `humaneval` / `mbpp` 等 |
| `--backend` | 推理后端（如 `vllm`） |
| `--greedy` | 贪心解码 |

入口为 `evalplus.evaluate`。

---

## 二、LiveCodeBench

用于代码生成等场景；需先按官方文档安装 **LiveCodeBench**，并在 `lcb_runner/lm_styles.py` 的 `LanguageModelList` 中注册模型。

### 1. 注册示例

```python
LanguageModel(
    "/path/to/your/Qwen3-4B-sft",
    "Qwen3-4B-sft",
    LMStyle.CodeQwenInstruct,
    datetime(2024, 6, 30),
    link="",
),
```

### 2. 运行示例

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

### 3. 参数简表

| 参数 | 含义 |
|------|------|
| `--model` | 与注册名一致的路径或标识 |
| `--scenario` | 任务场景 |
| `--evaluate` | 执行评测 |
| `--release_version` | 数据集版本 |
| `--n` | 每题采样数 |
| `--max_tokens` | 最大生成长度 |
| `--temperature` / `--top_p` | 采样参数 |
