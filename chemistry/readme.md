## Infinity-Instruct-2 / chemistry 模块说明

本目录包含化学推理方向的数据构造工作，基于 DataFlow 框架实现。核心文件：

- `chemistry_question_generator.py`：化学题目生成算子
- `prompt_temp.py`：化学领域专用 prompt 模板（同时包含物理 prompt，二者共用同一文件）
- `category_fuzz.py`：化学题目类型模糊匹配工具

---

## 1. 当前工作与计划

**题目合成**

`ChemistryQuestionGenerator` 算子基于种子题目调用 LLM 进行变体扩充，每次从 5 种预设的变换组合（`diversity_mode`）中随机采样 `num_prompts` 种，生成多样化的化学题目。

`ChemistryPrompt.chemisry_question_generate` 定义了合成 prompt 的具体变换策略，包括：
1. 修改化学参数（浓度、温度、压强、化学物种，要求保持物理真实性）
2. 引入实验室 / 工业约束（限量试剂、实际产率、非理想气体行为等）
3. 逆向推导（给定结果反推初始条件或未知试剂）
4. 提升结构 / 机理复杂度（立体化学、选择性、多步合成路径）
5. 跨化学领域融合（热力学 + 动力学、电化学 + 化学计量学等）

生成结果同样支持 `save_mode="full"` / `"synth"` 两种模式，并通过 `Synth_or_Input` 字段标记来源。

**题目分类**

`ChemistryPrompt.build_classification_prompt` 提供二级分类 prompt，覆盖 7 个一级类目、共 28 个二级类目（无机、有机、分析、物理化学、高分子、核化学、应用与交叉化学），输出标准 JSON 格式。

`ChemistryCategoryUtils`（`category_fuzz.py`）负责对 LLM 输出的分类结果进行规范化：
- 优先按 `X.Y` 编号直接解析
- 退而使用 `rapidfuzz` 模糊匹配（`WRatio` scorer，阈值 50）
- 同时提供 `category_hasher` / `category_hasher_reverse` 实现分类标签的整数编码与反解（便于后续数据分析与过滤）

**待补充**

- 难度分类 prompt（计划对标数学方向的 `ReasoningQuestionDifficultySampleEvaluator` 设计）

---

## 2. 数据来源

| 数据集 | 类型 | 备注 |
|--------|------|------|
| ChemBench | 化学综合推理 | 覆盖无机、有机、物化等方向 |
| OlympicArena-Chemistry | 化学竞赛题 | IChO 难度 |
| SciEval-Chemistry | 化学科学评测 | 高中到大学化学 |
| 合成扩充数据 | DataFlow 生成 | 基于上述种子题目变体扩充 |
