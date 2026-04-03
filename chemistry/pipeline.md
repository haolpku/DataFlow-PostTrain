# Chemistry：数据构造说明

化学推理向题目合成与分类，基于 DataFlow。全库索引见 [Readme.md](../Readme.md)，评测见 [eval.md](eval.md)。

---

## 核心文件

| 文件 | 作用 |
|------|------|
| `chemistry_question_generator.py` | 化学题生成算子 |
| `prompt_temp.py` | 化学（及物理）Prompt 模板，可与物理共用维护 |
| `category_fuzz.py` | 分类标签解析与模糊匹配（`ChemistryCategoryUtils`） |

---

## 1. 题目合成

`ChemistryQuestionGenerator` 基于种子题调用 LLM 扩展变体；从预设 **diversity_mode** 组合中随机采样 `num_prompts` 种。

`ChemistryPrompt` 中典型变换包括：

1. 改动物理化学条件（浓度、温度、压强、物种等），保持热力学 / 动力学合理性  
2. 加入实验室或工业约束（限量试剂、产率、非理想气体等）  
3. 逆向问题（由结果反推条件或未知物）  
4. 提高结构 / 机理复杂度（立体化学、选择性、多步路线）  
5. 跨子领域融合（如热力学 + 动力学、电化学 + 计量关系）  

**输出模式**：`save_mode="full"` 或 `"synth"`；**`Synth_or_Input`** 标记来源。

---

## 2. 题目分类

- `build_classification_prompt`：**7 个一级、28 个二级**类目（无机、有机、分析、物化、高分子、核化学、应用与交叉等），输出 JSON。  
- `ChemistryCategoryUtils`（`category_fuzz.py`）：优先解析 `X.Y` 编号；否则用 **rapidfuzz**（如 `WRatio`，阈值 50）模糊匹配；提供 `category_hasher` / `category_hasher_reverse` 便于编码与反查。

---

## 3. 待办

- 难度分类 Prompt（可对齐数学侧 `ReasoningQuestionDifficultySampleEvaluator` 思路）

---

## 4. 数据来源（参考）

| 数据集 | 类型 | 备注 |
|--------|------|------|
| ChemBench | 综合推理 | 无机 / 有机 / 物化等 |
| OlympicArena-Chemistry | 竞赛化学 | IChO 量级 |
| SciEval-Chemistry | 科学评测 | 高中—大学 |
| 合成数据 | DataFlow 生成 | 种子题变体 |
