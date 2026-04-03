# Math：数据构造与增强说明

数学推理方向的数据构造与 **CoT 清洗** 设计说明；实现依赖 DataFlow 及扩展算子。全库索引见根目录 [Readme.md](../Readme.md)，评测见 [eval.md](eval.md)。

---

## 1. 当前方向与计划

### 难度配比

依据 Pipeline 中的难度标签（如 `question_difficulty`），对 Easy / Medium / Hard **按比例采样**，避免简单题占比过高；高难度段可结合 **AIME、AMC** 等竞赛题补充。

### 思维链清洗（CoT Cleaning）

长 CoT 中常见重复叙述、无效探索与格式问题。可在 `dataflow/operators/reasoning/refine/` 中使用（或参考）如下算子：

| 代号 | 算子 | 思路 | 文档中的压缩率（量级） |
|------|------|------|-------------------------|
| A | `CoTLLMJudgeRefiner` | LLM 逐步标注 necessary / redundant / compressible 后分类处理 | ~41% |
| C | `CoTChunkCompressRefiner` | 按推理块切分后差异化压缩（思路接近 R1-Compress） | ~30% |
| D | `CoTPatternRefiner` | 多类 Thinking Pattern，剔除如 UNNECESSARY_EXPLORATION 等 | ~9% |

另可使用**无 LLM** 的规则算子 `CoTMathNormRefiner`，规范化 LaTeX（例如 `\tfrac`→`\frac`，`\sqrt x`→`\sqrt{x}`）。

> 完整流水线文件名（如 `reasoning_math_pipeline.py`）可能位于其他工程；本仓库以说明与评测文档为主时，以你本地 DataFlow 工程为准。

---

## 2. 数据来源（参考）

| 数据集 | 类型 | 规模（约） |
|--------|------|------------|
| `dataflow_reasoningmath_10k` | 数学 Long CoT | 10k |
| MATH / MATH-500 | 竞赛数学 | 12k / 500 |
| GSM8K | 基础推理 | 8.5k |
| NuminaMath | 竞赛数学合成 | ~860k |
