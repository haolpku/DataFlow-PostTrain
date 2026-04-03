# DataFlow-PostTrain

基于 [DataFlow](https://github.com/OpenDCAI/DataFlow) 的多领域**后训练数据合成（Pipeline）**与**评测（Evaluation）**指引。本仓库亦与 **Infinity-Instruct-2** 相关工作共用部分脚本与文档习惯；入口说明以本文件为准。

各子目录文档约定：**`pipeline.md`**（数据流水线说明）、**`eval.md`**（评测说明）。

- DataFlow 中文文档：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)
- 框架设计：[https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/](https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/)

---

## 总览表

| 目录 | 主要脚本 | `pipeline.md` | `eval.md` |
|------|----------|---------------|-----------|
| `biology/` | `dataflow_bioinstruct.py`, `dataflow_molinstruct_stream_batched.py` | [biology/pipeline.md](biology/pipeline.md) | [biology/eval.md](biology/eval.md) |
| `math/` | （说明见文档；流水线可能在其他工程） | [math/pipeline.md](math/pipeline.md) | [math/eval.md](math/eval.md) |
| `physics/` | `physics_question_generator.py`, `prompt_temp.py`, `category_fuzz.py` | [physics/pipeline.md](physics/pipeline.md) | [physics/eval.md](physics/eval.md) |
| `chemistry/` | `chemistry_question_generator.py`, `prompt_temp.py`, `category_fuzz.py` | [chemistry/pipeline.md](chemistry/pipeline.md) | [chemistry/eval.md](chemistry/eval.md) |
| `code/` | `code_code_to_sft_data_pipeline.py` | [code/pipeline.md](code/pipeline.md) | [code/eval.md](code/eval.md) |
| `computer_sicence/` | `dataflow_computer.py` | [computer_sicence/pipeline.md](computer_sicence/pipeline.md) | [computer_sicence/eval.md](computer_sicence/eval.md) |
| `data_science/` | `dataflow_datascience.py` | [data_science/pipeline.md](data_science/pipeline.md) | [data_science/eval.md](data_science/eval.md) |
| `medical/` | `zhiyou_finance_tagging.py`, `zhiyou_finance.py`, `zhiyou_medical.py` | [medical/pipeline.md](medical/pipeline.md) | [medical/eval.md](medical/eval.md) |
| 仓库根目录 | `single_turn_score_Q.py`, `single_turn_score_A.py`, `multi_turn_score.py` | 见下文「通用打分」 | — |

---

## 各领域 Pipeline 摘要

### Biology（`biology/`）

- **目标**：生物 / 化学 / 分子类指令的筛选、难化与带 CoT 的答案生成。
- **主脚本**：`dataflow_molinstruct_stream_batched.py`（分批流式，推荐作模板）；`dataflow_bioinstruct.py`（原型与 Prompt 草稿，部分步骤可能被注释）。
- **典型字段**：`instruction`；链路多为 **QuestionFilter → QuestionGenerator → AnswerGenerator → AnswerNgramFilter**（另可有 MinHash 去重等）。
- **详情**：[biology/pipeline.md](biology/pipeline.md)

### Math（`math/`）

- **目标**：数学推理数据构造、难度配比与 **CoT 清洗**（LLM Judge、分块压缩、模式精炼、LaTeX 规则规范化等）。
- **脚本**：本目录以设计说明为主；完整流水线见文档描述或外部工程。
- **数据来源（文档）**：如 `dataflow_reasoningmath_10k`、MATH、GSM8K、NuminaMath 等。
- **详情**：[math/pipeline.md](math/pipeline.md)

### Physics（`physics/`）

- **目标**：基于种子题的 LLM 变体生成；二级分类（经典力学、电磁、量子等）；`save_mode` 控制是否混合原始题。
- **核心**：`PhysicsQuestionGenerator`、`PhysicsPrompt`、`build_physics_classification_prompt`；`category_fuzz.py` 待与化学侧对齐。
- **详情**：[physics/pipeline.md](physics/pipeline.md)

### Chemistry（`chemistry/`）

- **目标**：化学题变体生成 + 二级分类；`ChemistryCategoryUtils` 做标签解析与模糊匹配。
- **核心**：`ChemistryQuestionGenerator`、`prompt_temp.py`、`category_fuzz.py`。
- **详情**：[chemistry/pipeline.md](chemistry/pipeline.md)

### Code（`code/`）

- **目标**：从 `instruction` 生成代码，将原始 `test` 转为可执行 `test_function`，多轮安全审查后 **沙盒执行**验证。
- **主脚本**：`code_code_to_sft_data_pipeline.py`。
- **输入**：至少 `instruction`、`test`；中间字段含 `generated_code`、`test_function`、`output_1/2/3` 等。
- **详情**：[code/pipeline.md](code/pipeline.md)

### Computer Science（`computer_sicence/`）

- **目标**：从论文 / 技术长上下文（`combined`）抽取冲突与瓶颈，生成复杂 CS 问题并生成结构化答案（JSON）。
- **主脚本**：`dataflow_computer.py`。
- **典型链路**：**QuestionGenerator → AnswerGenerator → AnswerNgramFilter**。
- **详情**：[computer_sicence/pipeline.md](computer_sicence/pipeline.md)

### Data Science（`data_science/`）

- **目标**：不改写问题，只精修已有样本答案：加深 `<Analyze>` / `<Understand>` 等标签内推理，保持 schema。
- **主脚本**：`dataflow_datascience.py`；`input_key="text"`，`output_key="generated_cot"`。
- **典型链路**：**AnswerGenerator → AnswerNgramFilter**。
- **详情**：[data_science/pipeline.md](data_science/pipeline.md)

### Medical & Finance（`medical/`）

- **目标**：金融任务打标（`tags`）、金融 QA 增强、医疗 Short CoT 答案生成（`generated_text`）。
- **主脚本**：`zhiyou_finance_tagging.py`、`zhiyou_finance.py`、`zhiyou_medical.py`。
- **详情**：[medical/pipeline.md](medical/pipeline.md)

### 通用打分（仓库根目录）

- **脚本**：`single_turn_score_Q.py`、`single_turn_score_A.py`、`multi_turn_score.py` — 用于对话或单轮 / 多轮样本的打分类流程（具体字段与用法以源码为准）。

---

## 各领域 Evaluation 摘要

| 领域 | 框架 / 工具 | 主要基准 | 详情 |
|------|-------------|----------|------|
| Biology | lm-evaluation-harness | GPQA Diamond | [biology/eval.md](biology/eval.md) |
| Computer Science | 第三方评测脚本 | MMLU-Pro | [computer_sicence/eval.md](computer_sicence/eval.md) |
| Data Science | OpenCompass | DS-1000 | [data_science/eval.md](data_science/eval.md) |
| Math | Qwen2.5-Math 系 fork | AIME 2024/25 pass@32、GSM8K、MATH、AMC 等 | [math/eval.md](math/eval.md) |
| Physics | OpenCompass | UGPhysics | [physics/eval.md](physics/eval.md) |
| Chemistry | OpenCompass | ChemBench | [chemistry/eval.md](chemistry/eval.md) |
| Code | EvalPlus、LiveCodeBench | HumanEval、MBPP、代码生成场景 | [code/eval.md](code/eval.md) |
| Medical / Finance | 脚本驱动（MedXpertQA、PIXIU） | 见仓库内 shell 与外部基准路径 | [medical/eval.md](medical/eval.md) |

完整命令、环境变量与路径替换说明请以各目录 **`eval.md`** 为准（`medical/eval.md` 中若含历史绝对路径，迁移时请改成本机路径）。

---

## 通用开发提示

- 先 **`compile()`** 检查 storage 与 `input_key` / `output_key` 是否一致，再 **`forward(..., resume_from_last=True)`** 便于断点续跑。
- API 密钥使用环境变量（如 **`DF_API_KEY`**），勿写入仓库；`api_url`、`model_name`、数据路径按本机修改。
- 不同实验使用不同 **`cache_path`** 与 **`file_name_prefix`**，避免缓存互相覆盖。

---

## 参考资料

- DataFlow：[https://github.com/OpenDCAI/DataFlow](https://github.com/OpenDCAI/DataFlow)
- DataFlow 中文文档：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)
