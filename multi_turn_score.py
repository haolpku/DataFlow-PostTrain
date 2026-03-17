import json
import argparse
import os
import pandas as pd
from vllm import LLM, SamplingParams
from tqdm import tqdm
import ray
import time
def remove_boxed(s: str) -> str:
    """去除\\boxed包装，提取内部内容"""
    if s is None:
        return "-1"  # 默认返回0分
    left = "\\boxed{"
    # 检查字符串是否以\left开头且以}结尾
    if s.startswith(left) and s.endswith("}"):
        return s[len(left):-1]
    else:
        # 如果没有boxed包装，直接返回原字符串
        return "-1"  # 默认返回-1分
def last_boxed_only_string(string: str):
    """提取字符串中最后一个LaTeX \boxed{}表达式"""
    if string is None or string == "":
        return "\\boxed{-1}"  # 返回默认值而不是None
    idx = string.rfind("\\boxed{")
    if idx < 0:
        return "\\boxed{-1}"

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0

    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    return string[idx:right_brace_idx + 1] if right_brace_idx is not None else "\\boxed{-1}"
SYSTEM_INFO = '''
You are a data quality assessment expert specializing in evaluating multi-turn conversational instructions and dialogues.'''


PROMPT = '''
Evaluate the provided multi-turn conversation based on the following criteria and structure your response as outlined below:

Evaluation Criteria:​
1. ​​​​​​Contextual Coherence:​​ Does each response appropriately address the current query while maintaining consistency with the conversation history?
2. ​​Relevance & Correctness:​​ Are all responses relevant to their respective instructions, and factually/logically correct?
3. ​​Conversational Flow:​​ Does the dialogue progress naturally? Are there any abrupt transitions, repetitions, or inconsistencies in the flow?
4. Logical Soundness:​​ Is the reasoning within and across turns logically consistent and complete?
5. Human-Like Quality:​​ Does the conversation feel natural and human-like, or are there detectable AI artifacts (e.g., generic, robotic, or nonsensical responses)?

Response Format:​
1.​​Final Score:​​ Provide a score between 1 and 3 using \boxed{}notation, where:1 = Poor (contains significant issues);2 = Fair (has some issues but is generally usable);3 = Excellent (clear, logical, human-like, and highly useful)
2.​​Turn-by-Turn Analysis:​​ Briefly evaluate each instruction-response pair.
3.Conversational Strengths/Weaknesses:​​ Highlight key strengths and any issues in coherence, flow, or logic.
4.AI Detection Note:​​ Indicate if any responses show signs of AI generation.

Conversation to Evaluate:​
{Conversation_History}
'''


ray.init(ignore_reinit_error=True, num_cpus=10, num_gpus=8, log_to_driver=True)

def main():
    # 设置参数解析
    parser = argparse.ArgumentParser(description="运行模型推理")
    parser.add_argument("--base_model", type=str, required=True, help="模型路径")
    parser.add_argument("--data_path", type=str, required=False, default = '', help="数据集路径")
    parser.add_argument("--start_index", type=int, required=False, default = '', help="起始索引")
    parser.add_argument("--end_index", type=int, required=False, default = '', help="结束索引")
    parser.add_argument("--outname", type=str, required=True, default = '', help="输出路径")
    parser.add_argument("--temperature", type=float, required=True, default = '', help="模型温度")
    args = parser.parse_args()
    
    temperature = round(args.temperature, 1)
    used_prompt = PROMPT
    # 加载JSONL数据
    data = []
    data_path = args.data_path
    with open(data_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            if line_number <= args.start_index:
                continue
            if line_number > args.end_index+1:
                break
            try:
                json_obj = json.loads(line.strip())
                data.append(json_obj)
                
            except json.JSONDecodeError:
                print(f"警告: 第 {line_number} 行不是有效的JSON格式")
                continue
    # 加载模型
    llm = LLM(model=args.base_model, tensor_parallel_size=8, max_num_seqs=64,gpu_memory_utilization=0.9,max_model_len=16384)
    sampling_params = SamplingParams(temperature=temperature, top_p=0.8, top_k=20, max_tokens=8096)
    tokenizer = llm.get_tokenizer()
    my_input = []
    for item in data:
        formatted_template = f"""{used_prompt}""".replace('{Conversation_History}', str(item["conversations"]))
        message = [{"role": "system", "content": SYSTEM_INFO}, {"role": "user", "content": formatted_template}]
        print(message)
        text = tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=True
        )
        my_input.append(text)

    print("--------------------------------------start generate---------------------------------------")
    start_time = time.time()
    outputs = llm.generate(my_input, sampling_params)
    print(f"--------------------------------------Finished in {time.time() - start_time:.2f} seconds---------------------------------------")

    # 以指定的JSONL格式准备输出数据
    output_data = []

    for i, output in enumerate(outputs):
            output_data.append({
                "id":str(args.start_index + i),
                "conversations": data[i]["conversations"],
                "instruction_score_origin":output.outputs[0].text,
                "instruction_score": str(remove_boxed(last_boxed_only_string(output.outputs[0].text))),
            })
    
    # 将输出保存为JSONL文件
    if not os.path.exists(args.outname):
        os.makedirs(args.outname)
    with open(os.path.join(args.outname,'multi_'+str(args.start_index)+'_'+str(args.end_index)+'.jsonl'), "w", encoding="utf-8") as outfile:
        for entry in output_data:
            json.dump(entry, outfile)
            outfile.write("\n")
        print("推理完成")

if __name__ == "__main__":
    main()