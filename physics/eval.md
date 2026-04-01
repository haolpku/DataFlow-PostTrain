# Eval Guide (Physics)

本文档说明物理方向的评测方案，基于 **OpenCompass** 框架，评测基准为 **UGPhysics**。

---

## 0. 评测框架

使用 [OpenCompass](https://github.com/open-compass/opencompass) 进行物理方向评测。

```bash
git clone https://github.com/open-compass/opencompass.git
cd opencompass
pip install -e .
```

---

## 1. 评测基准

| Benchmark | 说明 | 指标 |
|-----------|------|------|
| **UGPhysics** | 大学物理综合推理评测集，覆盖经典力学、电磁学、热力学、光学、近代物理等方向 | accuracy |

UGPhysics 面向大学本科物理水平，题目以推导计算为主，是评测模型物理推理深度的主要基准。

---

## 2. 环境准备

```bash
cd opencompass

# 安装依赖
pip install -e ".[full]"

# 确认 UGPhysics 数据已下载
ls data/ugphysics/
```

若数据目录为空，参考 OpenCompass 官方文档或 UGPhysics 原始仓库下载对应数据集。

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
    --datasets ugphysics_gen \
    --hf-type chat \
    --hf-path /path/to/your/model \
    --model-kwargs '{"tensor_parallel_size": 4}' \
    --work-dir ./outputs/physics \
    --reuse latest
```

或通过 API 方式评测（适合已部署服务的场景）：

```bash
python run.py \
    --datasets ugphysics_gen \
    --api-model your-model-name \
    --api-base http://localhost:8000/v1 \
    --work-dir ./outputs/physics
```

结果输出在 `./outputs/physics/` 目录下，汇总准确率见 `summary_*.csv`。

---

## 5. 常见检查项

- 模型服务名与 OpenCompass config 中 `model_name` 保持一致；
- UGPhysics 默认使用 `gen` 模式（生成式），需确认模型以对话格式（chat template）推理；
- 若准确率异常，优先检查答案提取规则是否匹配模型输出格式（数值+单位 vs. 纯数字）；
- 建议同时跑 `--reuse` 保留中间推理结果，方便后续 debug 或更换评分方式；
- UGPhysics 部分题目答案含量纲（如 `9.8 m/s²`），答案比对时注意单位规范化处理。
