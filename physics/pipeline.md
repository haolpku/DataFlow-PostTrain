# Physics：数据构造说明

物理推理向题目合成与分类，基于 DataFlow。全库索引见 [Readme.md](../Readme.md)，评测见 [eval.md](eval.md)。

---

## 核心文件

| 文件 | 作用 |
|------|------|
| `physics_question_generator.py` | 物理题生成算子 |
| `prompt_temp.py` | 物理 Prompt 模板 |
| `category_fuzz.py` | 分类结果模糊匹配（待与化学侧 `ChemistryCategoryUtils` 对齐完善） |

---

## 1. 题目合成

`PhysicsQuestionGenerator` 基于**种子题**调用 LLM 做变体；每次在若干 **diversity_mode** 组合中随机采样 `num_prompts` 种，提升题型多样性。

`PhysicsPrompt` 中典型变换包括：

1. 修改假设（理想 → 非理想：摩擦、非理想流体、相对论修正等）  
2. 跨子领域融合（如量子 + 热统、天体 + 粒子）  
3. 实验化情景（由纯推导转向实验设计与数据分析）  
4. 定量 / 定性互换  
5. 系统规模扩展（单体 → 多体、时变扰动、外场等）  

**输出模式**：`save_mode="full"` 保留原始与合成混合；`save_mode="synth"` 仅合成题。用字段 **`Synth_or_Input`** 标记来源。

---

## 2. 题目分类

`build_physics_classification_prompt` 提供**二级分类** Prompt（8 个一级、28 个二级：经典力学、热统、电磁、光学、量子、凝聚态与等离子体、相对论与粒子物理、数学与计算物理等），输出规范 JSON，便于下游统计与过滤。

---

## 3. 待办

- 难度分类 Prompt（可对齐数学侧 `ReasoningQuestionDifficultySampleEvaluator` 思路）  
- 完善物理侧 `category_fuzz.py`，对标化学 `category_fuzz.py`  

---

## 4. 数据来源（参考）

| 数据集 | 类型 | 备注 |
|--------|------|------|
| OlympicArena-Physics | 竞赛物理 | IPhO 量级 |
| SciBench-Physics | 大学物理综合 | 含求解过程 |
| SciEval-Physics | 科学评测 | 高中—大学 |
| 合成数据 | DataFlow 生成 | 基于种子题变体 |
