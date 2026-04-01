## Infinity-Instruct-2 / math 模块说明

本目录包含数学推理方向的数据构造与增强工作，基于 DataFlow 框架实现。

---

## 1. 当前工作与计划

数学方向当前以 `reasoning_math_pipeline.py` 为基础，正在推进以下几项改进：

**难度配比调控**
基于 pipeline 中的难度分类结果（`question_difficulty` 字段），对最终训练数据按 Easy / Medium / Hard 进行定比采样，避免数据在简单题上过度集中；同时计划引入 AIME / AMC / 竞赛题库对高难度段进行补充。

**思维链清洗（CoT Cleaning）**
长 CoT 中普遍存在冗余的自我重复、无效探索和格式不规范内容，清洗后可以提升训练信号质量。目前已实现三种清洗算子（位于 `dataflow/operators/reasoning/refine/`）：

| 方法 | 算子 | 策略 | 平均压缩率 |
|------|------|------|-----------|
| A | `CoTLLMJudgeRefiner` | LLM-Judge 逐步分类（necessary / redundant / compressible）并按类处理 | ~41% |
| C | `CoTChunkCompressRefiner` | 按推理边界切 Chunk，分类后差异化压缩（参考 R1-Compress） | ~30% |
| D | `CoTPatternRefiner` | 九分类 Thinking Pattern，精确识别并删除 UNNECESSARY_EXPLORATION 等有害模式 | ~9% |

此外配套了零 LLM 调用的规则型后处理算子 `CoTMathNormRefiner`，对 A / D 输出中的 LaTeX 表达做规范化（如 `\tfrac` → `\frac`、`\sqrt x` → `\sqrt{x}`）。

以上清洗工作目前已完成在 10k 数据集上的小规模验证，全量实验及下游训练验证正在推进。

---

## 2. 数据来源

| 数据集 | 类型 | 规模 |
|--------|------|------|
| `dataflow_reasoningmath_10k` | 数学推理 Long CoT | 10k |
| MATH / MATH-500 | 竞赛数学 | 12k / 500 |
| GSM8K | 基础推理 | 8.5k |
| NuminaMath | 竞赛数学合成 | ~860k |
