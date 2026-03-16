## Infinity-Instruct-2 / medical 模块说明

本目录主要包含与 **金融 / 医疗领域指令数据构造与增强** 相关的 DataFlow pipeline 脚本，其中核心脚本位于：

- `DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_finance_tagging.py`
- `DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_finance.py`
- `DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_medical.py`

这些脚本依赖统一的 DataFlow 框架（`dataflow.pipeline`, `dataflow.operators`, `dataflow.utils.storage`, `dataflow.serving` 等），通过 HTTP API 调用大模型，对现有数据进行 **任务标签提取**、**QA 改写** 或 **数据增强**。

> 注意：示例中使用的 API 地址、模型名称、数据路径、API Key 等都需要根据实际环境修改。不要直接把真实密钥提交到公共仓库。

---

## 1. 金融任务打标签：`zhiyou_finance_tagging.py`

**功能概述**

`ReasoningTaggingText` pipeline 用于对金融领域的指令 / 问题进行 **任务域提取和分类**：

- **输入**：金融相关的指令或问题（如 `finance_alpaca.jsonl` 中的 `instruction` 字段）
- **输出**：一个 JSON 风格的字符串列表，例如 `["FinancialQuestionAnswering", "MacroEconomicAnalysis"]`
- **核心思想**：
  - 使用内置的 `DIY_PROMPT_ANSWER`，引导 LLM 从统一任务列表中选择尽可能合适的金融任务名称；
  - 如果不在列表中，则根据金融知识自定义任务名；
  - 严格要求模型只输出 `["TaskA","TaskB"]` 这样的列表格式。

**关键类与组件**

- `ReasoningTaggingText(BatchedPipelineABC)`
  - 使用 `BatchedFileStorage` 进行分批读写数据；
  - 通过 `APILLMServing_request` 调用指定的 LLM HTTP API；
  - `self.prompt = DiyQuestionSynthesisPrompt(DIY_PROMPT_ANSWER)`：使用自定义的金融任务标注 prompt；
  - `self.generator = ReasoningTrajectoryGenerator(...)`：基于推理轨迹的生成算子，用于执行实际的 tagging 推理。

**使用示例**

脚本中的默认配置：

```python
pipeline = ReasoningTaggingText(
    api_url="https://kspmas.ksyun.com/v1/chat/completions",
    model_name=<YOUR_MODEL_NAME>,  # 示例代码中为 s，需要替换为实际模型名
    first_entry_file_name="/share/project/xzy_datas_models/infinity/Finance/Datasets/finance-alpaca/finance_alpaca.jsonl",
    cache_path="/share/project/xzy_datas_models/infinity/Finance/seeds",
    file_name_prefix="finance_alpaca_tagging",
    cache_type="jsonl",
    input_key="instruction",
    output_key="tags",
    max_workers=15,
)
pipeline.compile()
pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)
```

命令行运行示例：

```bash
cd /share/project/xiaozhiyou/Infinity-Instruct-2/medical

export DF_API_KEY=YOUR_API_KEY   # 在环境变量中设置 DataFlow 调用所需的密钥
python DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_finance_tagging.py
```

运行后，会在 `cache_path` 目录下生成带有 `file_name_prefix` 前缀的中间 / 结果文件，每条数据新增一个 `tags` 字段，对应金融任务标签列表。

---

## 2. 金融 QA 改写 / 数据增强：`zhiyou_finance.py`

**功能概述**

`ReasoningAnswerText` pipeline 用于对金融领域数据进行 **QA 改写或指令数据增强**：

- **输入**：金融领域的指令或问题（如 `finance_alpaca.jsonl` 中的 `instruction` 字段）
- **输出**：大模型生成的回答 / 改写文本，写入 `generated_text` 字段
- **典型用途**：
  - 基于原始金融指令生成更高质量的回答；
  - 通过多轮生成扩充指令-回答对，实现金融领域的数据增强。

**关键类与组件**

- `ReasoningAnswerText(BatchedPipelineABC)`
  - 使用 `BatchedFileStorage` 管理批量数据；
  - 通过 `APILLMServing_request` 调用金融领域大模型；
  - `self.prompt = GeneralAnswerGeneratorPrompt()`：使用通用推理回答生成 prompt，可替换为金融专用 prompt；
  - `self.generator = ReasoningAnswerGenerator(...)`：基于 `ReasoningAnswerGenerator` 的推理答案生成算子。

**使用示例**

脚本中的默认配置：

```python
pipeline = ReasoningAnswerText(
    api_url="https://kspmas.ksyun.com/v1/chat/completions",
    model_name="gpt-5.2",
    first_entry_file_name="/share/project/xzy_datas_models/infinity/Finance/Datasets/finance-alpaca/finance_alpaca.jsonl",
    cache_path="/share/project/xzy_datas_models/infinity/synthesized/Finance",
    file_name_prefix="finance_alpaca_synth",
    cache_type="jsonl",
    input_key="instruction",
    output_key="generated_text",
    max_workers=30,
)
pipeline.compile()
pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)
```

命令行运行示例：

```bash
cd /share/project/xiaozhiyou/Infinity-Instruct-2/medical

export DF_API_KEY=YOUR_API_KEY
python DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_finance.py
```

运行后，会在 `cache_path` 下生成以 `finance_alpaca_synth` 为前缀的结果文件，每条数据新增 `generated_text` 字段（金融问答或改写结果）。

---

## 3. 医疗 QA 改写 / 数据增强：`zhiyou_medical.py`

**功能概述**

`ShortCoTText` pipeline 用于对医疗领域的数据进行 **短链路推理（Short CoT）风格的 QA 改写或数据增强**：

- **输入**：医疗领域指令 / 问题（例如 MedQA / MedMCQA 的题目）
- **输出**：大模型生成的带有简短推理过程的回答，写入 `generated_text` 字段
- **典型用途**：
  - 为医学题目生成带思考过程的答案；
  - 构造或增强医疗领域的 CoT 风格训练数据。

**关键类与组件**

- `ShortCoTText(BatchedPipelineABC)`
  - 配置 `BatchedFileStorage` 进行分批处理；
  - 使用 `APILLMServing_request` 调用医疗场景下的大模型；
  - `self.prompt = GeneralShortCoTGeneratorPrompt()`：使用通用 Short CoT 生成 prompt，可替换为医疗专用 prompt；
  - `self.generator = ReasoningTrajectoryGenerator(...)`：基于推理轨迹的生成算子，生成带简短推理过程的回答。

**使用示例**

脚本中的默认配置：

```python
pipeline = ShortCoTText(
    api_url="https://kspmas.ksyun.com/v1/chat/completions",
    model_name="gpt-5.2",
    first_entry_file_name="/share/project/xzy_datas_models/infinity/Medical/seeds/medmcqa_instruction_only.jsonl",
    cache_path="/share/project/xzy_datas_models/infinity/synthesized/Medical",
    file_name_prefix="medmcqa_synth",
    cache_type="jsonl",
    input_key="instruction",
    output_key="generated_text",
    max_workers=30,
)
pipeline.compile()
pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)
```

命令行运行示例：

```bash
cd /share/project/xiaozhiyou/Infinity-Instruct-2/medical

export DF_API_KEY=YOUR_API_KEY
python DataFlow_finance_medical/run_pipelines/api_pipelines/zhiyou_medical.py
```

运行后，会在 `cache_path` 下生成以 `medmcqa_synth` 为前缀的结果文件，每条样本新增 `generated_text` 字段（医疗 QA + 简短 CoT）。

---

## 4. 参数说明与通用注意事项

**通用参数**

三类 pipeline 均继承 `BatchedPipelineABC`，核心参数含义一致：

- `api_url`: LLM 服务的 HTTP API 地址，如 `"https://kspmas.ksyun.com/v1/chat/completions"`
- `model_name`: 模型名称（例如 `"gpt-5.2"` 或其他后端模型名）
- `first_entry_file_name`: 首个输入文件路径，支持 `json/jsonl/csv/parquet/pickle`
- `cache_path`: 中间结果缓存 / 输出目录
- `file_name_prefix`: 中间结果文件前缀，用于区分不同任务或实验
- `cache_type`: 中间结果文件格式，例如 `"jsonl"`
- `input_key`: 输入数据中作为指令 / 问题的字段名（如 `"instruction"`, `"question"`, `"input"` 等）
- `output_key`: 输出字段名，金融 / 医疗 QA 一般为 `"generated_text"`，金融 tagging 为 `"tags"`
- `max_workers`: LLM 服务的最大并发数，用于并行调用

**运行前准备**

1. 确保 DataFlow 相关 Python 包在当前环境可用；
2. 根据自己的数据路径调整：
   - `first_entry_file_name`
   - `cache_path`
   - `file_name_prefix`
3. 在环境变量中设置调用 API 所需的 Key，例如：

```bash
export DF_API_KEY=YOUR_API_KEY
```

> 千万不要把真实的 API Key 直接写在代码里并提交到公共 GitHub 仓库，可以只在本地通过环境变量注入。

**建议流程**

- 金融场景：
  - 先运行 `zhiyou_finance_tagging.py` 为样本打上任务域标签；
  - 再运行 `zhiyou_finance.py` 对样本进行 QA 改写 / 数据增强；
  - 可根据标签进行下游任务划分与分析。
- 医疗场景：
  - 直接运行 `zhiyou_medical.py` 为 MedQA / MedMCQA 等数据生成带短 CoT 的回答；
  - 可以叠加多次生成不同风格的回答，用于扩充训练集。

