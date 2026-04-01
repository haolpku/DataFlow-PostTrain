# Eval Guide (Math)

评测基于 [HeRunming/Qwen2.5-Math](https://github.com/HeRunming/Qwen2.5-Math) fork，在原始框架基础上新增了 AIME 2024 / 2025 的 pass@32 计算逻辑。

---

## 1. 评测基准

| Benchmark | 指标 | 说明 |
|-----------|------|------|
| **AIME 2024** | pass@32 | 各题采样 32 次，temperature=0.6 |
| **AIME 2025** | pass@32 | 同上 |
| GSM8K | accuracy | greedy，temperature=0 |
| MATH | accuracy | greedy，temperature=0 |
| gaokao2024_mix | accuracy | greedy，temperature=0 |
| AMC 2023 | accuracy | greedy，temperature=0 |

---

## 2. 运行评测

```bash
bash evaluation/sh/run_eval_qwen2_math.sh <PROMPT_TYPE> <MODEL_NAME_OR_PATH>
```

脚本内部分两段依次执行：

**① AIME pass@32**（temperature=0.6，n_sampling=1，data_name=`aime24_avg32,aime25_avg32`）

```bash
TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --data_name "aime24_avg32,aime25_avg32" \
    --output_dir ${MODEL_NAME_OR_PATH}/math_eval \
    --split test \
    --prompt_type ${PROMPT_TYPE} \
    --num_test_sample -1 \
    --seed 0 \
    --temperature 0.6 \
    --n_sampling 1 \
    --top_p 0.95 \
    --use_vllm \
    --save_outputs \
    --overwrite
```

**② 标准 Bench**（temperature=0，data_name=`gsm8k,math,gaokao2024_mix,amc23`）

```bash
TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --data_name "gsm8k,math,gaokao2024_mix,amc23" \
    --output_dir ${MODEL_NAME_OR_PATH}/math_eval \
    --split test \
    --prompt_type ${PROMPT_TYPE} \
    --num_test_sample -1 \
    --seed 0 \
    --temperature 0 \
    --n_sampling 1 \
    --top_p 1 \
    --use_vllm \
    --save_outputs \
    --overwrite
```

结果保存在 `<MODEL_NAME_OR_PATH>/math_eval/` 目录下。

---

## 3. 常见检查项

- `PROMPT_TYPE` 需与模型训练时使用的 prompt 格式匹配（如 `qwen-boxed`、`deepseek-math` 等）；
- AIME pass@32 的置信区间较宽（30 道题），建议配合多次重跑取均值；
- 若答案提取异常，优先检查 `--prompt_type` 对应的答案解析逻辑是否与模型输出格式匹配。
