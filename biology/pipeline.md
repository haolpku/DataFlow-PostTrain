# Biology：DataFlow Pipeline 说明

本目录介绍 **生物 / 化学 / 分子** 方向的后训练数据合成脚本，基于 [DataFlow](https://github.com/OpenDCAI/DataFlow)。

- **全库总览与评测索引**：根目录 [Readme.md](../Readme.md)  
- **计算机科学上下文 Pipeline**：[computer_sicence/pipeline.md](../computer_sicence/pipeline.md)  
- **数据科学答案精修 Pipeline**：[data_science/pipeline.md](../data_science/pipeline.md)  
- **本领域评测**：[eval.md](eval.md)  

---

## 1. Pipeline 在做什么

在 DataFlow 中，数据处理被拆成可复用的 **Operator**，再串成 **Pipeline**。典型组成包括：`storage`、`LLMServing`、**Prompt**，以及多次 `operator.run(...)`。开发时建议先 **`compile()`** 检查字段 key，再 **`forward()`** 执行。

本目录脚本的共性步骤可概括为：

1. 定义领域 Prompt  
2. 配置输入 JSONL 与缓存路径  
3. 配置 LLM API 与模型名  
4. 选择算子并写入 `forward()`  
5. `compile()` + `forward(..., resume_from_last=True)`  

领域差异主要来自：**Prompt 与输出格式**、**输入字段名**（如 `instruction`）、**是否包含过滤 / 问题重写**。

---

## 2. 常用算子（推理向）

| 算子 | 作用 |
|------|------|
| `ReasoningQuestionFilter` | 判断样本是否值得保留 |
| `ReasoningQuestionGenerator` | 改写 / 扩展为更难任务 |
| `ReasoningAnswerGenerator` | 生成带推理过程或最终答案 |
| `ReasoningAnswerNgramFilter` | 抑制复读与低质量答案 |
| `FileStorage` / `StreamBatchedFileStorage` | 分步读写缓存 |
| `APILLMServing_request` | HTTP API 调用模型 |

**最小模板**（示意，字段名请按数据修改）：

```python
from dataflow.pipeline import StreamBatchedPipelineABC
from dataflow.utils.storage import StreamBatchedFileStorage
from dataflow.serving import APILLMServing_request
from dataflow.operators.reasoning import (
    ReasoningQuestionGenerator,
    ReasoningAnswerGenerator,
    ReasoningAnswerNgramFilter,
)

class MyPipeline(StreamBatchedPipelineABC):
    def __init__(self):
        super().__init__()
        self.storage = StreamBatchedFileStorage(
            first_entry_file_name="your_input.jsonl",
            cache_path="./workspace/results",
            file_name_prefix="my_domain_",
            cache_type="jsonl",
        )
        self.llm_serving = APILLMServing_request(
            api_url="https://your-api/v1/chat/completions",
            model_name="your-model",
            max_workers=30,
        )
        self.question_gen = ReasoningQuestionGenerator(
            num_prompts=1,
            llm_serving=self.llm_serving,
            prompt_template=...,
        )
        self.answer_gen = ReasoningAnswerGenerator(
            llm_serving=self.llm_serving,
            prompt_template=...,
        )
        self.answer_filter = ReasoningAnswerNgramFilter(
            min_score=0.1,
            max_score=1.0,
            ngrams=5,
        )

    def forward(self):
        self.question_gen.run(storage=self.storage.step(), input_key="instruction")
        self.answer_gen.run(
            storage=self.storage.step(),
            input_key="instruction",
            output_key="generated_cot",
        )
        self.answer_filter.run(
            storage=self.storage.step(),
            input_question_key="instruction",
            input_answer_key="generated_cot",
        )

if __name__ == "__main__":
    pl = MyPipeline()
    pl.compile()
    pl.forward(batch_size=400, resume_from_last=True)
```

---

## 3. 本目录脚本

| 文件 | 说明 |
|------|------|
| [dataflow_bioinstruct.py](dataflow_bioinstruct.py) | **原型**：展示生化领域 Prompt（如 `DIY_PROMPT_QUESTION` / `DIY_PROMPT_SYNTHESIS` / `DIY_PROMPT_ANSWER`，答案含 `reasoning_trace` 与 `output`）。含 `MinHashDeduplicateFilter`、`ReasoningQuestionFilter` 等；`forward()` 里可能仅部分步骤启用，适合作为 Prompt 与流水线草稿。 |
| [dataflow_molinstruct_stream_batched.py](dataflow_molinstruct_stream_batched.py) | **推荐主模板**：`StreamBatchedPipelineABC` + `StreamBatchedFileStorage`，适合大 JSONL。当前典型链路：`ReasoningQuestionFilter` → `ReasoningQuestionGenerator` → `ReasoningAnswerGenerator` → `ReasoningAnswerNgramFilter`。数据流：**原始指令 → 过滤 → 难化 → 带 CoT 的答案 → N-gram 过滤**。支持 `batch_size` 与 `resume_from_last`。 |

---

## 4. 与相邻目录的对比（速查）

| 目录 | 代表脚本 | 策略摘要 | 典型输入字段 |
|------|----------|----------|--------------|
| **biology**（本文） | `dataflow_molinstruct_stream_batched.py` | 过滤 → 难化 → 作答 | `instruction` |
| **computer_sicence** | `dataflow_computer.py` | 长上下文上造题再作答 | `combined` |
| **data_science** | `dataflow_datascience.py` | 只精修答案 | `text` |

---

## 5. 新脚本怎么写

1. **定类型**：脏数据先过滤、要强难度加 QuestionGenerator、只要好答案可只用 AnswerGenerator + N-gram 过滤。  
2. **对齐 key**：确认 JSONL 里是 `instruction` 还是其他，再填 `input_key` / `input_question_key` / `input_answer_key`。  
3. **隔离缓存**：不同实验使用不同 `cache_path` 与 `file_name_prefix`。  
4. **配置**：替换示例中的数据路径、API、模型名；使用 **`DF_API_KEY`** 等环境变量，勿提交密钥。  

---

## 6. 常见调参

- **路径**：示例中的集群绝对路径需改为本机路径。  
- **batch_size / max_workers**：按 API 限流与成本调整。  
- **Prompt 输出格式**：尽量固定为 JSON 或固定标签，便于解析与过滤。  

---

## 7. 新领域文档建议（`pipeline.md`）

每个新目录建议用 **`pipeline.md`** 写清四件事：**要解决的数据问题**、**输入字段**、**算子列表**、**新增输出字段**；评测另写 **`eval.md`**。

---

## 参考资料

- DataFlow：[https://github.com/OpenDCAI/DataFlow](https://github.com/OpenDCAI/DataFlow)  
- 中文文档：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)  
- 框架设计：[https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/](https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/)  
