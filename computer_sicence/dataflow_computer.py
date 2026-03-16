import re
from dataflow.pipeline import StreamBatchedPipelineABC
from dataflow.serving import APILLMServing_request

from dataflow.operators.reasoning import (
    ReasoningQuestionGenerator,
    ReasoningAnswerGenerator,
)
from dataflow.operators.reasoning import ReasoningQuestionFilter, ReasoningAnswerNgramFilter
# from dataflow.operators.general_text import MinHashDeduplicateFilter
from dataflow.utils.storage import FileStorage
from dataflow.serving import APILLMServing_request
from dataflow.core import LLMServingABC
from dataflow.prompts.reasoning.diy import (
    DiyQuestionFilterPrompt,
    DiyAnswerGeneratorPrompt,
    DiyQuestionSynthesisPrompt
)
from dataflow.utils.storage import StreamBatchedFileStorage

# Synthesis: 核心逻辑 - 将简单指令“进化”为复杂推理任务
# 这里利用了我们刚才设计的 Meta-Prompt 逻辑

DIY_PROMPT_SYNTHESIS = """
You are a "Chief AI Research Architect" specialized in Computer Science. 
Your goal is to synthesize a high-quality, "reasoning-dense" instruction based on the provided Research Data.

**Source Seed Data (Reference Context):**
Full Context: {question}

**Task:**
Analyze the 'Full Context' to identify a "Technical Conflict" or "Logical Bottleneck" (e.g., a scenario where standard algorithms fail due to specific constraints like missing labels, high noise, or domain shift). 
Synthesize a NEW, complex engineering task that requires bridging **High-Level Architectural Goals** (Macro) with **Low-Level Algorithmic/Mathematical Logic** (Micro).

**Categories for the NEW Task:**
1. Conflict-Resolution Design: "Given constraint X, why does standard method Y fail, and how must we adapt Z?"
2. First-Principles Derivation: "From the perspective of statistical distribution/optimization, derive a solution for..."
3. Comparative Theoretical Analysis: "Contrast the convergence or generalization properties of..."

**Requirements for the NEW Task:**
1. It must explicitly mention a "Logical Conflict" identified from the paper.
2. It must require multi-step deduction (not just a lookup).
3. Do NOT simply paraphrase. Create a professional "Interview/Consultancy" style scenario.

**Output Format:**
[Instruction]: <The complex reasoning task/question>
[Input Context]: <Relevant technical details from the paper: e.g., mathematical constraints, specific dataset properties, or a summary of the 'Mixture Domain' problem>
"""

# Answer: 强制生成思维链 (Chain of Thought)
DIY_PROMPT_ANSWER = """
You are a world-class AI Scientist and Professor. 
Answer the following Computer Science task using a rigorous **Chain of Thought (CoT)** process.

**The Task:**
{question}

**Requirements for Reasoning Trace:**
1. **Conflict Identification**: Briefly explain the technical "deadlock" in the current scenario.
2. **Knowledge Retrieval**: Map the problem to 2-3 CS fundamentals (e.g., Statistical Moment Matching, Gradient-based Optimization, or Feature Decoupling).
3. **Deductive Derivation**: Show the step-by-step logic. Use LaTeX for any mathematical expressions (e.g., MMD formulas or Normalization equations).
4. **Conclusion**: Verify why the proposed solution successfully resolves the initial conflict.

**Output Format:**
Please output the result in the following JSON format strictly:
{{
    "reasoning_trace": "1. Conflict: ... 2. Fundamentals: ... 3. Derivation: ...",
    "output": "A concise, definitive technical solution or summary."
}}
"""

class DiyReasoning_APIPipeline(StreamBatchedPipelineABC):
    def __init__(self, llm_serving: LLMServingABC = None):
        super().__init__()
        
        # ---------------------------------------------------------------------
        # 2. 修改数据存储路径和类型
        # ---------------------------------------------------------------------

        self.storage = StreamBatchedFileStorage(
            # 指向你的具体文件路径
            first_entry_file_name="/share/project/miaode/infini/infinite_Data/ComputerScience/Dataset/keywords.jsonl",
            cache_path="/share/project/miaode/infini/training_code/DataFlow/workspace/results_for_infini/computer_instruct",
            file_name_prefix="computer_newstep_",
            # 注意: 你的文件看起来是标准JSON列表 [...]，而不是 JSONL。
            # 如果 dataflow 库只支持 jsonl，你需要先转换文件格式。
            # 这里假设库支持 'json' 模式读取列表。
            cache_type="jsonl", 
        )

        # ---------------------------------------------------------------------
        # 3. 设置 LLM (建议使用 Gemini 2.5 或强大的模型)
        # ---------------------------------------------------------------------
        self.llm_serving = APILLMServing_request(
            api_url="https://kspmas.ksyun.com/v1/chat/completions",
            model_name="claude-opus-4.5",
            max_workers=30
        )

        # Step 2: 合成 (Synthesis / Augmentation) - 生成更难的问题
        self.question_gen_step2 =  ReasoningQuestionGenerator(
            num_prompts=5,
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
        # self.minhash_deduplicator.run(
        #     storage = self.storage.step(),
        #     input_key='instruction',
        # )


        # Step 2: 生成新问题 (基于 instruction 和 input)
        self.question_gen_step2.run(
            storage = self.storage.step(),
            input_key = "combined", # 这里会将原始的 instruction 传给 prompt 中的 {instruction}
            # 注意：如果库支持，确认是否需要额外参数来传递 "input" 字段。
            # 很多 pipeline 库会自动把当前 item 的所有字段以此 dict 形式传给 template.format(**item)。
        )
        
        # Step 3: 生成答案 (CoT)
        self.answer_generator_step3.run(
            storage = self.storage.step(),
            # 这里的 input_key 应该是上一步生成的"新问题"的字段名
            # 通常 QuestionGenerator 会把生成的内容存为 "generated_question" 或类似字段
            # 你需要确认 ReasoningQuestionGenerator 的默认输出 key 是什么。
            # 假设默认输出 key 是 "generated_text" 或复用了 "instruction"
            input_key = "combined", # 这里直接用原始的 instruction 作为问题输入，或者改成 question_gen_step2 的输出 key
            output_key = "generated_cot"
        )
        
        # Step 4: 最终过滤
        self.answer_ngram_filter_step4.run(
            storage = self.storage.step(),
            input_question_key = "combined",
            input_answer_key = "generated_cot"
        )
if __name__ == "__main__":
    pl = DiyReasoning_APIPipeline()
    pl.compile()
    pl.forward(batch_size=400, resume_from_last=True)