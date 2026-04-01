## Infinity-Instruct-2 / physics 模块说明

本目录包含物理推理方向的数据构造工作，基于 DataFlow 框架实现。核心文件：

- `physics_question_generator.py`：物理题目生成算子
- `prompt_temp.py`：物理领域专用 prompt 模板
- `category_fuzz.py`（TODO）：物理题目类型模糊匹配工具（参考化学方向，待补充）

---

## 1. 当前工作与计划

**题目合成**

`PhysicsQuestionGenerator` 算子基于种子题目调用 LLM 进行变体扩充，每次从 5 种预设的变换组合（`diversity_mode`）中随机采样 `num_prompts` 种，生成多样化的物理题目。

`PhysicsPrompt` 定义了合成 prompt 的具体变换策略，包括：
1. 修改物理假设（理想 → 非理想，引入摩擦、非理想流体、相对论效应等）
2. 跨领域融合（量子力学 + 热力学、天体物理 + 粒子物理等）
3. 实验情景化（从纯理论推导转向实验设计与数据分析）
4. 定量 / 定性转换（概念题 ↔ 数值计算题）
5. 系统规模扩展（单粒子 → 多体系统，引入时变微扰和外场）

生成结果支持 `save_mode="full"`（原始 + 合成混合输出）或 `save_mode="synth"`（仅输出合成题目）两种模式，并通过 `Synth_or_Input` 字段标记来源。

**题目分类**

`build_physics_classification_prompt` 提供二级分类 prompt，覆盖 8 个一级类目、28 个二级类目（经典力学、热统、电磁学、光学、量子力学、凝聚态与等离子体、相对论与粒子物理、数学与计算物理），输出标准 JSON 格式便于下游分析。

**待补充**

- 难度分类 prompt（对标化学方向，计划参照数学方向的 `ReasoningQuestionDifficultySampleEvaluator` 设计）
- 物理方向的 `category_fuzz.py`（模糊匹配分类结果规范化，对标 `ChemistryCategoryUtils`）

---

## 2. 数据来源

| 数据集 | 类型 | 备注 |
|--------|------|------|
| OlympicArena-Physics | 物理竞赛题 | IPhO 难度 |
| SciBench-Physics | 大学物理综合 | 含完整求解步骤 |
| SciEval-Physics | 物理科学评测集 | 覆盖高中到大学物理 |
| 合成扩充数据 | DataFlow 生成 | 基于上述种子题目变体扩充 |
