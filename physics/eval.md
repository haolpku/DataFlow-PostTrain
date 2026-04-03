# Physics 评测说明

使用 [OpenCompass](https://github.com/open-compass/opencompass)，基准为 **UGPhysics**（大学物理综合推理）。

---

## 1. 安装框架

```bash
git clone https://github.com/open-compass/opencompass.git
cd opencompass
pip install -e .
pip install -e ".[full]"
```

确认数据目录存在（名称以当前 OpenCompass 版本为准）：

```bash
ls data/ugphysics/
```

若为空，按 OpenCompass 或 UGPhysics 官方说明下载数据。

---

## 2. 评测基准

| Benchmark | 说明 | 指标 |
|-----------|------|------|
| **UGPhysics** | 本科物理综合，含力学、电磁、热学、光学、近代物理等 | accuracy |

---

## 3. 启动推理服务（示例：vLLM）

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --served-model-name your-model-name \
    --tensor-parallel-size 4 \
    --port 8000
```

---

## 4. 运行评测

**HuggingFace 模型路径：**

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

**OpenAI 兼容 API：**

```bash
python run.py \
    --datasets ugphysics_gen \
    --api-model your-model-name \
    --api-base http://localhost:8000/v1 \
    --work-dir ./outputs/physics
```

汇总结果见 `./outputs/physics/` 下 `summary_*.csv`。

---

## 5. 排错要点

- 服务中的模型名与 config 中 `model_name` 一致。  
- `ugphysics_gen` 为生成式设定，需使用正确的 **chat template**。  
- 部分答案含**单位**，比对前宜做规范化。  
- 建议保留 `--reuse` 便于复现与 debug。  
