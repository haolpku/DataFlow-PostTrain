# Computer Science：DataFlow Pipeline 说明

本目录脚本基于 [DataFlow](https://github.com/OpenDCAI/DataFlow)，从**论文或技术长上下文**中构造计算机科学方向的复杂问答与推理数据。

**仓库总览**见根目录 [Readme.md](../Readme.md)。**评测**见同目录 [eval.md](eval.md)。

---

## 脚本

| 文件 | 作用 |
|------|------|
| [dataflow_computer.py](dataflow_computer.py) | 主 Pipeline：上下文 → 复杂问题 → 带结构化解题的答案 |

---

## 数据流与算子

**目标**：让模型从上下文中识别 **Technical Conflict** 或 **Logical Bottleneck**，将材料改写成偏研究面试、技术咨询或理论分析风格的问题；答案阶段通常要求**严格 JSON**（冲突分析、基础知识映射、推导过程、结论等）。

**当前链路**（典型）：

1. `ReasoningQuestionGenerator`
2. `ReasoningAnswerGenerator`
3. `ReasoningAnswerNgramFilter`

**输入字段**：一般为 `combined`（标题、摘要、关键词、方法等拼成的长文本），在 `run(...)` 中通过 `input_key="combined"` 指定，**不是** `instruction`。

**适用场景**：

- 论文 / 摘要 / 技术报告 → 问答重构  
- 算法或设计中的冲突、瓶颈识别类数据  
- 需要明确推导链条的 CS SFT / 推理数据  

---

## 与 Biology、Data Science 的对比

| 维度 | 本目录（CS） | `biology/` | `data_science/` |
|------|----------------|------------|-----------------|
| 策略 | 基于上下文**重写问题**再作答 | 过滤 → 难化 → 作答 | **只精修答案**，不改题 |
| 典型输入 key | `combined` | `instruction` | `text` |

---

## 开发注意

- 先 **`compile()`** 确认 JSONL 字段与 `input_key` / `output_key` 一致，再 **`forward(..., resume_from_last=True)`**。  
- 替换示例中的 `api_url`、`model_name`、`cache_path`；密钥用环境变量（如 `DF_API_KEY`），勿提交仓库。  

---

## 参考资料

- DataFlow：[https://github.com/OpenDCAI/DataFlow](https://github.com/OpenDCAI/DataFlow)  
- 中文文档：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)  
