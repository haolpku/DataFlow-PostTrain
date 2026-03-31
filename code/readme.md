# Code SFT Synthesis API Pipeline

这是一个基于 `dataflow` 框架实现的代码合成与测试流水线，用于从指令出发自动生成代码、构造测试函数、进行安全审查，并最终在沙盒环境中执行测试。

## 整体流程

该流水线的核心目标是：针对给定的问题描述，自动生成可执行代码，并尽可能安全地验证代码行为。

主要流程如下：

1. **根据问题生成代码**

   * 输入是样本中的 `instruction`
   * 使用大模型根据问题描述和函数接口生成目标代码
   * 输出字段为 `generated_code`

2. **根据原始代码中的测试样例和生成代码，构造测试函数**

   * 输入包括：

     * 上一步生成的 `generated_code`
     * 原始样本中的测试样例 `test`
   * 通过模型将原始测试样例转换为可直接执行的测试函数
   * 输出字段为 `test_function`

3. **对生成代码和测试函数进行安全审查**

   * 将 `generated_code` 和 `test_function` 一起输入到安全审查 prompt 中
   * 让模型判断这些代码在严格沙盒策略下是否可能触发危险行为
   * 重点检查：

     * 是否会写入、修改、删除当前工作目录之外的文件
     * 是否使用路径逃逸（如 `../`、绝对路径、home 目录等）
     * 是否会终止、干扰无关进程或线程
   * 这里会重复调用 3 次审查模型，分别输出：

     * `output_1`
     * `output_2`
     * `output_3`

4. **在沙盒中执行测试函数**

   * 使用 `CodeUnitTestSandboxEvaluator`
   * 在受限环境中执行 `generated_code` 和 `test_function`
   * 对生成代码进行最终运行验证

---

## Pipeline 结构说明

### 1. 代码生成

使用：

* `CodeInstructionToCodeGenerator`

输入：

* `instruction`

输出：

* `generated_code`

该阶段通过自定义 prompt 强制模型只输出代码，不输出解释、markdown 或额外文字。

---

### 2. 测试函数生成

使用：

* `CodeInstructionToUnitTestFunctionGenerator`

输入：

* `generated_code`
* `test`

输出：

* `test_function`

这一阶段的作用是将原始数据中的测试样例转化为可执行测试函数，便于后续统一进行安全分析和沙盒执行。

---

### 3. 安全性检查

使用：

* `FormatStrPromptedGenerator`

输入：

* `generated_code`
* `test_function`

输出：

* `output_1`
* `output_2`
* `output_3`

该阶段通过安全审查 prompt 判断测试代码和目标代码的组合执行是否安全。

#### 审查重点

沙盒策略默认假设：

* 运行时当前工作目录是一个空目录
* 代码只允许在当前工作目录内创建、修改、删除文件
* 不允许写入或破坏当前目录之外的任何文件
* 不允许通过相对路径逃逸、绝对路径、符号链接等方式绕过限制
* 不允许杀死、挂起、干扰无关进程或线程

#### 输出格式

模型必须只返回如下 JSON：

```json
{
  "verdict": "SAFE/UNSAFE",
  "key_reasons": ["Reason 1 ...", "Reason 2 ..."]
}
```

---

### 4. 沙盒执行

使用：

* `CodeUnitTestSandboxEvaluator`

输入：

* `generated_code`
* `test_function`

配置：

* `language='python'`
* `timeout_length=5`

这一阶段会在沙盒中实际执行测试函数，验证代码是否能够通过测试，并控制执行时间避免长时间阻塞。

---

## 依赖模型

当前 pipeline 中配置了两个 API Serving：

### Claude

用于代码生成：

* `model_name="claude-opus-4.5"`

### GPT

用于测试函数生成和安全审查：

* `model_name="gpt-5.2"`

---

## 存储方式

使用：

* `BatchedFileStorage`

配置示例：

* `first_entry_file_name="/path/to/first_entry_file.jsonl"`
* `cache_path="./cache"`
* `file_name_prefix="file_name_prefix"`
* `cache_type="jsonl"`

流水线会按 batch 方式读取和缓存中间结果，支持断点续跑。

---

## 运行方式

```bash
python your_pipeline_file.py
```

主函数执行流程如下：

```python
if __name__ == "__main__":
    pipeline = CodeSFTSynthesis_APIPipeline()
    pipeline.compile()
    pipeline.forward(batch_size=BATCH_SIZE, resume_from_last=True)
```

其中：

* `batch_size=BATCH_SIZE`：指定每批处理数量
* `resume_from_last=True`：从上次进度继续执行

---

## 输入数据要求

输入样本中至少应包含以下字段：

* `instruction`：问题描述 / 代码生成需求
* `test`：原始测试样例

流水线会在处理过程中逐步生成以下字段：

* `generated_code`
* `test_function`
* `output_1`
* `output_2`
* `output_3`

---

## 输出结果说明

每条样本经过流水线后，通常会包含：

* **generated_code**：模型根据问题生成的代码
* **test_function**：基于原始测试样例转换出的测试函数
* **output_1 / output_2 / output_3**：三次安全审查结果
* **sandbox evaluation result**：沙盒执行结果（由 evaluator 写入对应存储结果中）

---

## 设计目的

该流水线主要用于构建更可靠的代码 SFT 数据或代码评测流程，核心思想是：

* 先生成代码
* 再补齐可执行测试
* 在执行前做安全审查
* 最后放入沙盒运行验证

这样可以在提升自动化程度的同时，降低直接执行模型生成代码带来的风险。

---

## 注意事项

1. **API Key**

   * 运行前需要正确设置 `DF_API_KEY`

2. **临时目录**

   * 建议将 `TMPDIR`、`TEMP`、`TMP` 重定向到受控目录
   * 当前代码中已经显式设置到项目工作目录下

3. **模型返回格式**

   * 安全审查阶段要求模型严格输出 JSON
   * 否则可能影响后续解析

4. **路径安全**

   * 虽然 prompt 中允许临时文件操作，但前提是临时目录解析后仍位于当前工作目录内部

5. **超时控制**

   * 沙盒执行超时时间当前设置为 5 秒
   * 可根据任务复杂度调整

---

## 示例流程概览

```text
instruction
   ↓
生成 generated_code
   ↓
结合原始 test 生成 test_function
   ↓
对 generated_code + test_function 做 3 次安全审查
   ↓
在沙盒中执行 test_function
   ↓
得到最终测试结果
```
