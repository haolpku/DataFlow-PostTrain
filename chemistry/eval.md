# Eval Guide (Chemistry)

本文档说明化学方向的评测方案，基于 **OpenCompass** 框架，评测基准为 **ChemBench**。

---

## 0. 评测框架

使用 [OpenCompass](https://github.com/open-compass/opencompass) 进行化学方向评测。

```bash
git clone https://github.com/open-compass/opencompass.git
cd opencompass
pip install -e .
```

---

## 1. 评测基准

| Benchmark | 说明 | 指标 |
|-----------|------|------|
| **ChemBench** | 化学综合推理评测集，覆盖无机、有机、物化、分析化学等方向 | accuracy |

ChemBench 包含多项化学推理任务：反应类型判断、化学计量计算、有机结构推断、方程式配平等，是目前化学方向覆盖最全面的公开评测集之一。

---

## 2. 环境准备

```bash
cd opencompass

# 安装依赖
pip install -e ".[full]"

# 确认 ChemBench 数据已下载
ls data/chembench/
```

若数据目录为空，参考 OpenCompass 官方文档或 ChemBench 原始仓库下载对应数据集。

---

## 3. 启动模型服务

在一个 `tmux` 窗口中启动模型服务（以 vLLM 为例）：

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --served-model-name your-model-name \
    --tensor-parallel-size 4 \
    --port 8000
```

---

## 4. 运行评测

在另一个 `tmux` 窗口执行：

```bash
cd opencompass

python run.py \
    --datasets chembench_gen \
    --hf-type chat \
    --hf-path /path/to/your/model \
    --model-kwargs '{"tensor_parallel_size": 4}' \
    --work-dir ./outputs/chemistry \
    --reuse latest
```

或通过 API 方式评测：

```bash
python run.py \
    --datasets chembench_gen \
    --api-model your-model-name \
    --api-base http://localhost:8000/v1 \
    --work-dir ./outputs/chemistry
```

结果输出在 `./outputs/chemistry/` 目录下，汇总准确率见 `summary_*.csv`。

---

## 5. 常见检查项

- 模型服务名与 OpenCompass config 中 `model_name` 保持一致；
- ChemBench 部分子任务为多选题（Multi-label），答案提取逻辑需覆盖选项集合格式；
- 化学式（如 `H₂O`、`CO₂`）的答案匹配建议使用规范化后比对（去空格、统一大小写）；
- 若对有机化学子任务分数有疑问，优先检查 IUPAC 命名格式与模型输出格式的匹配情况；
- 建议保留 `--reuse` 中间结果，便于按子任务分析各化学方向的得分分布。
