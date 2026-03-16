from dataflow.operators.reasoning import (
    ReasoningQuestionGenerator,
    ReasoningAnswerGenerator,
)
from dataflow.operators.reasoning import ReasoningQuestionFilter, ReasoningAnswerNgramFilter
from dataflow.operators.general_text import MinHashDeduplicateFilter
from dataflow.utils.storage import FileStorage
from dataflow.serving import APILLMServing_request
from dataflow.core import LLMServingABC
from dataflow.prompts.reasoning.diy import (
    DiyQuestionFilterPrompt,
    DiyAnswerGeneratorPrompt,
    DiyQuestionSynthesisPrompt
)

# ---------------------------------------------------------------------
# 1. 增强后的 Prompt 设计
# ---------------------------------------------------------------------

# Filter: 确保是高质量的生物医学文本
# DIY_PROMPT_QUESTION = """You are a biomedical data quality specialist.
# Please evaluate if the following content contains valid medical, biological, or chemical information suitable for scientific reasoning.
# If it is valid, set "judgement_test" to true. If it is nonsense, generic chat, or non-science, set it to false.

# After these steps, output exactly:
# {{
#     "judgement_test": true/false,
#     "error_type": "<error description or null>"
# }}
# You may include your chain of thought, but the final output must be the JSON above.

# Here is the content to evaluate:
# -------------------------------

# Input Context: {question}
# -------------------------------
# """

DIY_PROMPT_QUESTION = """You are a Senior Bio-Cheminformatics Quality Auditor. 
Your goal is to evaluate if the given scientific instruction and its context are high-quality, technically accurate, and suitable for training an expert-level LLM.

### 1. EVALUATION RUBRIC:
- **Score 5 (Expert):** Highly specialized. Contains precise structural data (SMILES/Protein sequences) or complex multi-step reasoning. Zero ambiguity.
- **Score 4 (High Quality):** Correct and professional. Covers specific domain knowledge (e.g., reaction reagents, protein localization) but may be less complex than Score 5.
- **Score 3 (Acceptable):** Factually correct but trivial or "textbook" level (e.g., simple definitions). Low informational density.
- **Score 2 (Poor/Noisy):** Contains minor scientific errors, broken formatting in SMILES/Sequences, or is too generic.
- **Score 1 (Garbage):** Nonsense, significant hallucinations, completely broken structural strings, or non-scientific chat.

### 2. AUDIT CHECKLIST:
- **Chemical Logic:** If SMILES are present, do they look syntactically correct? Are the task-related reagents or products chemically plausible?
- **Biological Logic:** For protein sequences, does the described function align with a typical biological role? Is the sequence string intact?
- **Instruction Depth:** Does the prompt provide enough information to be solvable? Avoid instructions that are too brief without sufficient context.

### JUDGEMENT RULE:
1. Conduct a brief Internal Chain of Thought (CoT).
2. If the data is professional, accurate, and complex (Score 4-5), set "judgement_test" to true.
3. If the data is trivial, generic, or contains any structural/scientific errors (Score 1-3), set "judgement_test" to false.

Output exactly this JSON format:
{{
    "judgement_test": true/false,
    "error_type": "<brief reason if false, else null>"
}}

---
### CONTENT TO EVALUATE:
{question}
---


"""

# Synthesis: 核心逻辑 - 将简单指令“进化”为复杂推理任务
# 这里利用了我们刚才设计的 Meta-Prompt 逻辑
DIY_PROMPT_SYNTHESIS = """
You are an advanced "AI Scientific Research Architect". 
Your goal is to synthesize a high-quality, "reasoning-dense" instruction based on the provided Seed Data.

**Source Seed Data:**
Original Instruction: {question}

**Task:**
Create a NEW, more complex task that bridges **Clinical/Literature Understanding** (Macro) and **Molecular/Protein Logic** (Micro).
The new task should fall into one of these categories:
1. Translational Reasoning (Text-to-Structure)
2. Mechanism Explanation (Structure-to-Text)
3. Hypothesis Generation

**Requirements for the NEW Task:**
1. It must require multi-step reasoning.
2. It should be self-contained (include necessary context in the 'Input' section of your generation).
3. Do NOT simply paraphrase the original. Expand it.

**Output Format:**
Start directly with the new problem statement.
Format:
[Instruction]: <The specific task for the model>
[Input Context]: <The context, e.g., a synthesized clinical abstract or SMILES string>
"""

# Answer: 强制生成思维链 (Chain of Thought)
DIY_PROMPT_ANSWER = """
You are an expert AI Scientist.
Please answer the following scientific task using a strict **Chain of Thought** process.

**The Task:**
{question}

**Requirements:**
1. First, perform a 'Reasoning Trace' where you analyze the biological or chemical logic step-by-step.
2. Then, provide the 'Final Answer'.

**Output Format:**
Please output the result in the following JSON format strictly:
{{
    "reasoning_trace": "Your step-by-step scientific logic here...",
    "output": "The final concise answer."
}}
"""

class DiyReasoning_APIPipeline():
    def __init__(self, llm_serving: LLMServingABC = None):
        
        # ---------------------------------------------------------------------
        # 2. 修改数据存储路径和类型
        # ---------------------------------------------------------------------

        self.storage = FileStorage(
            # 指向你的具体文件路径
            first_entry_file_name="/share/project/miaode/infini/infinite_Data/Biology/Dataset/Mol_Instructions/data/final_merged_data.jsonl",
            cache_path="/share/project/miaode/infini/training_code/DataFlow/workspace/results_for_infini/mol_instruct",
            file_name_prefix="mol_instruct_step",
            # 注意: 你的文件看起来是标准JSON列表 [...]，而不是 JSONL。
            # 如果 dataflow 库只支持 jsonl，你需要先转换文件格式。
            # 这里假设库支持 'json' 模式读取列表。
            cache_type="jsonl", 
        )

        # ---------------------------------------------------------------------
        # 3. 设置 LLM (建议使用 Gemini 2.5 或强大的模型)
        # ---------------------------------------------------------------------
        self.llm_serving = APILLMServing_request(
            # 确保这里指向支持 Gemini 或 GPT-4 级别的 API
            # api_url="https://kspmas.ksyun.com/v1", 
            api_url="https://kspmas.ksyun.com/v1/chat/completions",
            # api_url="https://api.siliconflow.cn/v1/chat/completions",
            # model_name="mgg-7", # 或者是 gemini-1.5-pro
            # model_name="mog-2",
            model_name="mgg-2",
            max_workers=50
        )
        self.minhash_deduplicator = MinHashDeduplicateFilter(num_perm=128, threshold=0.9, use_n_gram=True, ngram=5)

        # Step 1: 过滤 (Filter)
        self.question_filter_step1 = ReasoningQuestionFilter(
            system_prompt="You are a biomedical expert.",
            llm_serving=self.llm_serving,
            prompt_template=DiyQuestionFilterPrompt(DIY_PROMPT_QUESTION)
        )
        
        # Step 2: 合成 (Synthesis / Augmentation) - 生成更难的问题
        self.question_gen_step2 =  ReasoningQuestionGenerator(
            num_prompts=1,
            llm_serving=self.llm_serving,
            prompt_template=DiyQuestionSynthesisPrompt(DIY_PROMPT_SYNTHESIS)
        )
        
        # Step 3: 回答 (Answer Generation) - 生成 CoT 和答案
        self.answer_generator_step3 = ReasoningAnswerGenerator(
            llm_serving=self.llm_serving,
            prompt_template=DiyAnswerGeneratorPrompt(DIY_PROMPT_ANSWER)
        )
        
        # Step 4: 校验 (N-gram Filter) - 防止复读机
        self.answer_ngram_filter_step4 = ReasoningAnswerNgramFilter(
            min_score = 0.1,
            max_score = 1.0,
            ngrams = 5
        )
        
    def forward(self):
        # ---------------------------------------------------------------------
        # 4. 键值映射 (关键修改)
        # ---------------------------------------------------------------------
        # 原始数据包含 "instruction" 和 "input"。
        # 我们需要在 prompt 里把它们拼起来，或者传入多个 key。
        # 假设 dataflow 的 run 方法支持把所有字段传给 prompt format。
        self.minhash_deduplicator.run(
            storage = self.storage.step(),
            input_key='instruction',
        )
        
        # # Step 1: 过滤
        # self.question_filter_step1.run(
        #     storage = self.storage.step(),
        #     # 传入 instruction 作为主要检查对象，但 Prompt template 里我们用了 {input}，
        #     # 这里的 input_key 主要是指从 JSON 里取哪个字段作为主键流转。
        #     input_key = "instruction", 
        # )

        # # Step 2: 生成新问题 (基于 instruction 和 input)
        # self.question_gen_step2.run(
        #     storage = self.storage.step(),
        #     input_key = "instruction", # 这里会将原始的 instruction 传给 prompt 中的 {instruction}
        #     # 注意：如果库支持，确认是否需要额外参数来传递 "input" 字段。
        #     # 很多 pipeline 库会自动把当前 item 的所有字段以此 dict 形式传给 template.format(**item)。
        # )
        
        # # Step 3: 生成答案 (CoT)
        # self.answer_generator_step3.run(
        #     storage = self.storage.step(),
        #     # 这里的 input_key 应该是上一步生成的"新问题"的字段名
        #     # 通常 QuestionGenerator 会把生成的内容存为 "generated_question" 或类似字段
        #     # 你需要确认 ReasoningQuestionGenerator 的默认输出 key 是什么。
        #     # 假设默认输出 key 是 "generated_text" 或复用了 "instruction"
        #     input_key = "instruction", 
        #     output_key = "generated_cot"
        # )
        
        # # Step 4: 最终过滤
        # self.answer_ngram_filter_step4.run(
        #     storage = self.storage.step(),
        #     input_question_key = "instruction",
        #     input_answer_key = "generated_cot"
        # )
if __name__ == "__main__":
    pl = DiyReasoning_APIPipeline()
    pl.forward()