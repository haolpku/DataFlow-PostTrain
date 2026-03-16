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



# Answer: 强制生成思维链 (Chain of Thought)
DIY_PROMPT_ANSWER = """
# Role
You are a world-class AI Data Refinement Expert specializing in high-quality SFT (Supervised Fine-Tuning) dataset engineering.

# Task Objective
Your task is to optimize the "output" content of the provided JSON data. You must enhance the logical depth and technical accuracy of the reasoning process without changing the underlying JSON schema or the internal tag-based structure.

# Input Data
{question}

# Optimization Requirements
1. **CoT Deepening**: Within the `<Analyze>` and `<Understand>` tags, expand the reasoning steps. Ensure there are no logical leaps and every deduction is grounded in the provided "instruction" and "input".
2. **Technical Accuracy**: Correct any potential bugs in code snippets or errors in logical derivation. Ensure the final result in `<Answer>` is 100% correct.
3. **Structure Preservation**: 
   - DO NOT modify the JSON keys (instruction, input, output, etc.).
   - DO NOT remove or alter the XML-style tags within the output (e.g., `<Analyze>`, `<Understand>`, `<Answer>`).
4. **Professionalism**: Use precise technical terminology and ensure the content is formatted with clean Markdown (headers, code blocks, bold text).

# Output Format
Return ONLY the optimized JSON object. Do not include any conversational filler, explanations, or Markdown code blocks outside of the JSON itself.
"""

class DiyReasoning_APIPipeline(StreamBatchedPipelineABC):
    def __init__(self, llm_serving: LLMServingABC = None):
        super().__init__()
        
        # ---------------------------------------------------------------------
        # 2. 修改数据存储路径和类型
        # ---------------------------------------------------------------------

        self.storage = StreamBatchedFileStorage(
            # 指向你的具体文件路径
            first_entry_file_name="/share/project/miaode/infini/infinite_Data/DataScience/datascience_dataflow.jsonl",
            cache_path="/share/project/miaode/infini/training_code/DataFlow/workspace/results_for_infini/ds_instruct",
            file_name_prefix="ds_",
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
            api_url="https://kspmas.ksyun.com/v1/chat/completions",
            model_name="mog-2",
            max_workers=30
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

        # Step 3: 生成答案 (CoT)
        self.answer_generator_step3.run(
            storage = self.storage.step(),
            input_key = "text", 
            output_key = "generated_cot"
        )
        
        # Step 4: 最终过滤
        self.answer_ngram_filter_step4.run(
            storage = self.storage.step(),
            input_question_key = "text",
            input_answer_key = "generated_cot"
        )
if __name__ == "__main__":
    pl = DiyReasoning_APIPipeline()
    pl.compile()
    pl.forward(batch_size=400, resume_from_last=True)