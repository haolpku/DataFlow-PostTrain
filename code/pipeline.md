# Code：SFT 合成与沙盒验证 Pipeline

基于 DataFlow 的**代码生成 → 单测函数 → 安全审查 → 沙盒执行**流水线，用于构造更可靠的代码 SFT 数据或评测前置流程。主实现：[code_code_to_sft_data_pipeline.py](code_code_to_sft_data_pipeline.py)（Pipeline 类名以源码为准，如 `CodeSFTSynthesis_APIPipeline`）。全库索引见 [Readme.md](../Readme.md)，评测见 [eval.md](eval.md)。

---

## 流程概览

```text
instruction
  → generated_code（由 instruction 生成）
  → test_function（结合原始 test 与 generated_code）
  → output_1 / output_2 / output_3（三次安全审查 JSON）
  → 沙盒执行测试结果
```

1. **代码生成**：`CodeInstructionToCodeGenerator`，输入 `instruction`，输出 `generated_code`（Prompt 要求仅代码、无多余说明）。  
2. **测试函数**：`CodeInstructionToUnitTestFunctionGenerator`，输入 `generated_code` 与原始 `test`，输出可执行的 `test_function`。  
3. **安全审查**：`FormatStrPromptedGenerator`，输入 `generated_code` + `test_function`，并行或多次调用得到 `output_1`、`output_2`、`output_3`。模型须输出 JSON：

```json
{
  "verdict": "SAFE/UNSAFE",
  "key_reasons": ["...", "..."]
}
```

4. **沙盒执行**：`CodeUnitTestSandboxEvaluator`，在受限环境执行 `generated_code` 与 `test_function`（示例配置：`language='python'`，`timeout_length=5`）。

---

## 沙盒策略（审查关注点）

- 工作目录视为**空目录**；文件读写仅限其内。  
- 禁止通过 `../`、绝对路径、符号链接等**逃逸**到目录外。  
- 禁止干扰或终止与工作无关的进程 / 线程。  

---

## 存储与运行

- 存储：`BatchedFileStorage`（`first_entry_file_name`、`cache_path`、`file_name_prefix`、`cache_type="jsonl"`），支持断点续跑。  
- 运行示例：

```bash
export DF_API_KEY=...   # 勿提交密钥
python code/code_code_to_sft_data_pipeline.py
# 或在 code/ 目录下：python code_code_to_sft_data_pipeline.py
```

```python
if __name__ == "__main__":
    pipeline = CodeSFTSynthesis_APIPipeline()
    pipeline.compile()
    pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)
```

---

## 输入 / 输出字段

| 阶段 | 主要字段 |
|------|-----------|
| 输入 | `instruction`，`test` |
| 中间 / 输出 | `generated_code`，`test_function`，`output_1`～`output_3`，以及 evaluator 写入的沙盒结果 |

---

## 依赖模型（示例配置）

文档或源码中可能出现多Serving：例如代码生成用 **Claude**，测试与安全审查用 **GPT**；实际以你修改后的 `model_name` 为准。

---

## 注意事项

1. **`DF_API_KEY`**：通过环境变量注入。  
2. **临时目录**：建议将 `TMPDIR` / `TEMP` / `TMP` 指到受控路径（若源码中有设置，与之一致）。  
3. **审查 JSON**：解析失败时检查模型是否严格输出 JSON。  
4. **超时**：沙盒默认 5s 可按题目难度调整。  
