# Data Science：DataFlow Pipeline 说明

本目录脚本基于 [DataFlow](https://github.com/OpenDCAI/DataFlow)，对**已有数据科学类样本**做答案侧增强：加深推理、修正错误，**不生成新题干**。

**仓库总览**见根目录 [Readme.md](../Readme.md)。**评测**见同目录 [eval.md](eval.md)。

---

## 脚本

| 文件 | 作用 |
|------|------|
| [dataflow_datascience.py](dataflow_datascience.py) | 主 Pipeline：精修 `output` / 文本中的推理与代码 |

---

## 数据流与算子

**目标**：在 Prompt 中要求模型深化 `<Analyze>`、`<Understand>` 等标签内的推理，修正错误代码或推导，**保持原有 JSON schema 与标签结构**（如 `<Analyze>`、`<Understand>`、`<Answer>`）。

**当前链路**（典型）：

1. `ReasoningAnswerGenerator`
2. `ReasoningAnswerNgramFilter`

**字段约定**：

- 输入：`input_key="text"`（整条待精修文本或结构化样本的文本形态，以你的数据为准）  
- 输出：`output_key="generated_cot"`  

**适用场景**：

- 已有 JSONL，答案质量不稳，希望加强 CoT 深度  
- 需保留题干与外层结构，只优化 answer 部分  

---

## 与 Biology、Computer Science 的对比

| 维度 | 本目录（Data Science） | `biology/` | `computer_sicence/` |
|------|------------------------|------------|-------------------|
| 策略 | **只精修答案** | 过滤 → 难化 → 作答 | 上下文上**造新题**再作答 |
| 典型输入 key | `text` | `instruction` | `combined` |

---

## 开发注意

- 先 **`compile()`** 核对 `text` / `generated_cot` 等 key 与存储步骤是否衔接。  
- `cache_path`、`file_name_prefix` 与 API 配置请按本机修改；勿在仓库中硬编码密钥。  

---

## 参考资料

- DataFlow：[https://github.com/OpenDCAI/DataFlow](https://github.com/OpenDCAI/DataFlow)  
- 中文文档：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)  
