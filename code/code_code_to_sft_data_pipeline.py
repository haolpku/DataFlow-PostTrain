import os
os.environ["DF_API_KEY"] = "xxxx"
os.environ["TMPDIR"] = "/path/to/tmp"
os.environ["TEMP"] = "/path/to/tmp"
os.environ["TMP"] = "/path/to/tmp"

from dataflow.operators.code import (
    CodeInstructionToCodeGenerator,
    CodeUnitTestSandboxEvaluator,
    CodeInstructionToUnitTestFunctionGenerator
)

from dataflow.utils.storage import BatchedFileStorage
from dataflow.serving import APILLMServing_request
from dataflow.pipeline import BatchedPipelineABC
from dataflow.operators.core_text import FormatStrPromptedGenerator
from dataflow.prompts.core_text import FormatStrPrompt

from dataflow.prompts.code import DiyCodePrompt

generate_code_with_interface_prompt_template = DiyCodePrompt(
            "You are a world-class coding assistant. Your task is to fulfill the following request precisely. "
            "Your response must contain ONLY the code that satisfies the instruction. "
            "Do not add any explanations, introductory sentences, or markdown formatting like ```python ... ```.\n\n"
            "Request: {instruction}\n\n"
            "Your function implementation interface should be:\n"
            "{interface}\n\n"
            "Generated Code:"
        )

f_str_template = (
    "You are a security-focused code auditor. "
    "Your task is to determine whether the provided test code "
    "is safe to run when it imports/calls/executes the provided code, under a strict sandbox policy.\n\n"

    "**Important**: Many tasks legitimately involve filesystem I/O or process/thread operations. "
    "You must not flag code as unsafe just because it imports or uses modules like os, pathlib, shutil, subprocess, threading, or multiprocessing. "
    "Instead, you must predict the concrete runtime effects (what files/paths/processes/threads will actually be touched) "
    "based on the combination of test + code.\n"
    "Additionally, the default temporary directory(/tmp) has already been redirected to a subdirectory inside the current working directory. "
    "Therefore, writing to temporary files/directories is allowed and does not need extra restriction, "
    "as long as the resolved temp path stays within the CWD and does not escape it.\n\n"

    "**Inputs**:\n"
    "- code: the code under test.\n"
    "- test: the test function/code that will execute or call the code.\n\n"

    "**Sandbox Policy (Must Enforce)**:\n"
    "Assume the current working directory at runtime is an empty folder.\n"
    "1. Filesystem safety:\n "
    "- The test and thecode are allowed to create / write / modify / delete files only inside the current working directory."
    "- Example allowed: with open('a.jsonl', 'w') as f: ... (creates a.jsonl in the empty current working directory).\n"
    "- They must NOT modify, write, rename, chmod, move, or delete any files outside the current working directory.\n"
    "- They may read files outside the current working directory only if necessary (e.g., reading source code), but must not write/modify/delete anything outside current working directory.\n"
    "- They must not use path tricks to escape the current working directory (e.g., ../, absolute paths like /etc/..., C:\..., symlinks, environment-dependent paths, home directories, temp directories unless explicitly inside current working directory).\n"
    "2. Process & thread safety:\n"
    "- During the test execution, neither the test nor code may kill, terminate, suspend, or interfere with unrelated processes or threads.\n"
    "- Creating subprocesses/threads may be acceptable only if they are fully owned by the test and safely cleaned up without impacting anything else, but any “kill by PID/name/pattern” behavior is unsafe.\n"
    
    "**What You Must Do**:\n"
    "- Analyze both generated_code and test to understand what will run when the test calls the code.\n"
    "- Identify any operations that could violate the policy.\n\n"

    "**Required Output Format**:\n"
    "Return ONLY a single valid JSON object (no markdown, no extra text).\n"
    "Use exactly the following top-level keys:\n"
    "{'verdict': 'SAFE/UNSAFE', 'key_reasons': ['Reason 1 ...', 'Reason 2 ...']}\n\n"

    "code:\n{code}\n"
    "test:\n{test}\n"
    "Produce the required output format."
)

format_str_prompt_template = FormatStrPrompt(
    f_str_template=f_str_template,
)

BATCH_SIZE = 2000
# START_BATCH = 0

class CodeSFTSynthesis_APIPipeline(BatchedPipelineABC):
    def __init__(self):
        super().__init__()
        
        self.storage = BatchedFileStorage(
            first_entry_file_name="/path/to/first_entry_file.jsonl",
            cache_path="./cache",
            file_name_prefix="file_name_prefix",
            cache_type="jsonl",
        )
        
        # use API server as LLM serving
        self.llm_serving_claude = APILLMServing_request(
            api_url="https://api.openai.com/v1/chat/completions",
            model_name="claude-opus-4.5",
            max_workers=100,
            connect_timeout=60.0,
            read_timeout=180.0,
            max_retries=15,
        )

        self.llm_serving_gpt = APILLMServing_request(
            api_url="https://api.openai.com/v1/chat/completions",
            model_name="gpt-5.2",
            max_workers=100,
            connect_timeout=60.0,
            read_timeout=180.0,
            max_retries=15,
        )

        self.code_generator = CodeInstructionToCodeGenerator(
            llm_serving=self.llm_serving_claude,
            prompt_template=generate_code_with_interface_prompt_template
        )
        

        self.unit_test_function_generator = CodeInstructionToUnitTestFunctionGenerator(
            llm_serving=self.llm_serving_gpt,
        )   
        self.format_str_prompted_generator_1 = FormatStrPromptedGenerator(
            llm_serving=self.llm_serving_gpt,
            prompt_template=format_str_prompt_template,
        )
        self.format_str_prompted_generator_2 = FormatStrPromptedGenerator(
            llm_serving=self.llm_serving_gpt,
            prompt_template=format_str_prompt_template,
        )
        self.format_str_prompted_generator_3 = FormatStrPromptedGenerator(
            llm_serving=self.llm_serving_gpt,
            prompt_template=format_str_prompt_template,
        )
        self.unit_test_sandbox_evaluator = CodeUnitTestSandboxEvaluator(
            language='python',
            timeout_length=5
        )

    
    def forward(self):

        self.code_generator.run(
            storage=self.storage.step(),
            input_key="instruction",
            output_key="generated_code"
        )

        self.unit_test_function_generator.run(
            storage=self.storage.step(),
            input_code_key="generated_code",
            input_unit_test_key="test",
            output_key="test_function"
        )

        self.format_str_prompted_generator_1.run(
            storage=self.storage.step(),
            output_key="output_1",
            code="generated_code",
            test="test_function"
        )

        self.format_str_prompted_generator_2.run(
            storage=self.storage.step(),
            output_key="output_2",
            code="generated_code",
            test="test_function"
        )
        self.format_str_prompted_generator_3.run(
            storage=self.storage.step(),
            output_key="output_3",
            code="generated_code",
            test="test_function"
        )

        self.unit_test_sandbox_evaluator.run(
            storage=self.storage.step(),
            input_code_key="generated_code",
            input_test_function_key="test_function"
        )


if __name__ == "__main__":
    pipeline = CodeSFTSynthesis_APIPipeline()
    pipeline.compile()
    pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)