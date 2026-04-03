# Math 评测说明

评测流程基于 [HeRunming/Qwen2.5-Math](https://github.com/HeRunming/Qwen2.5-Math) fork：在上游能力上补充 **AIME 2024 / 2025** 的 pass@32 等逻辑。以下命令需在**已克隆并配置好该仓库**的环境中执行。

---

## 1. 基准与指标

| Benchmark | 指标 | 说明 |
|-----------|------|------|
| AIME 2024 | pass@32 | 每题采样 32 次，`temperature=0.6` |
| AIME 2025 | pass@32 | 同上 |
| GSM8K | accuracy | greedy，`temperature=0` |
| MATH | accuracy | greedy，`temperature=0` |
| gaokao2024_mix | accuracy | greedy，`temperature=0` |
| AMC 2023 | accuracy | greedy，`temperature=0` |

---

## 2. 一键脚本

```bash
bash evaluation/sh/run_eval_qwen2_math.sh <PROMPT_TYPE> <MODEL_NAME_OR_PATH>
```

脚本通常先后执行两段（与仓库内 `math_eval.py` 一致）：

**① AIME pass@32**（`data_name=aime24_avg32,aime25_avg32`）

```bash
TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
    --model_name_or_path "${MODEL_NAME_OR_PATH}" \
    --data_name "aime24_avg32,aime25_avg32" \
    --output_dir "${MODEL_NAME_OR_PATH}/math_eval" \
    --split test \
    --prompt_type "${PROMPT_TYPE}" \
    --num_test_sample -1 \
    --seed 0 \
    --temperature 0.6 \
    --n_sampling 1 \
    --top_p 0.95 \
    --use_vllm \
    --save_outputs \
    --overwrite
```

**② 标准 Bench**（`data_name=gsm8k,math,gaokao2024_mix,amc23`，`temperature=0`）

```bash
TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
    --model_name_or_path "${MODEL_NAME_OR_PATH}" \
    --data_name "gsm8k,math,gaokao2024_mix,amc23" \
    --output_dir "${MODEL_NAME_OR_PATH}/math_eval" \
    --split test \
    --prompt_type "${PROMPT_TYPE}" \
    --num_test_sample -1 \
    --seed 0 \
    --temperature 0 \
    --n_sampling 1 \
    --top_p 1 \
    --use_vllm \
    --save_outputs \
    --overwrite
```

结果目录：`<MODEL_NAME_OR_PATH>/math_eval/`。

---

## 3. 排错要点

- `PROMPT_TYPE` 须与**训练 / 推理**所用模板一致（如 `qwen-boxed`、`deepseek-math`）。  
- AIME 仅约 30 题，pass@32 **方差大**，宜多次重复取均值。  
- 若分数异常，先查答案抽取逻辑是否与模型输出格式匹配。  
