# Chemistry 评测说明

使用 [OpenCompass](https://github.com/open-compass/opencompass)，基准为 **ChemBench**（化学综合推理）。

---

## 1. 安装框架

```bash
git clone https://github.com/open-compass/opencompass.git
cd opencompass
pip install -e .
pip install -e ".[full]"
```

确认数据：

```bash
ls data/chembench/
```

若为空，按 OpenCompass 或 ChemBench 官方说明准备数据。

---

## 2. 评测基准

| Benchmark | 说明 | 指标 |
|-----------|------|------|
| **ChemBench** | 反应类型、计量、结构推断、配平等多任务 | accuracy |

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
    --datasets chembench_gen \
    --hf-type chat \
    --hf-path /path/to/your/model \
    --model-kwargs '{"tensor_parallel_size": 4}' \
    --work-dir ./outputs/chemistry \
    --reuse latest
```

**OpenAI 兼容 API：**

```bash
python run.py \
    --datasets chembench_gen \
    --api-model your-model-name \
    --api-base http://localhost:8000/v1 \
    --work-dir ./outputs/chemistry
```

结果见 `./outputs/chemistry/`，汇总为 `summary_*.csv`。

---

## 5. 排错要点

- 服务模型名与 config 一致。  
- 部分子任务为 **多标签 / 多选**，抽取答案时需覆盖集合或列表格式。  
- 化学式建议**规范化**后比对（空格、大小写）。  
- 有机命名与模型输出格式不一致时，先核对 IUPAC 与解析规则。  
