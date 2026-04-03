# Medical & Finance：DataFlow Pipeline 说明

本目录为**金融**（打标、QA 增强）与**医疗**（短 CoT 答案）的 DataFlow API Pipeline 脚本。全库索引见 [Readme.md](../Readme.md)，评测见 [eval.md](eval.md)。

> 运行前请自行设置 `api_url`、`model_name`、`first_entry_file_name`、`cache_path` 等；通过 **`DF_API_KEY`** 注入密钥，勿提交到公开仓库。

---

## 脚本一览

| 文件 | Pipeline 角色 | 输入字段 | 输出字段 |
|------|----------------|----------|----------|
| [zhiyou_finance_tagging.py](zhiyou_finance_tagging.py) | 金融任务域标签 | `instruction` | `tags`（JSON 列表字符串） |
| [zhiyou_finance.py](zhiyou_finance.py) | 金融 QA / 增强 | `instruction` | `generated_text` |
| [zhiyou_medical.py](zhiyou_medical.py) | 医疗 Short CoT | `instruction` | `generated_text` |

三类脚本均基于 `BatchedPipelineABC` + `BatchedFileStorage` + `APILLMServing_request`；具体类名（如 `ReasoningTaggingText`、`ReasoningAnswerText`、`ShortCoTText`）与 Prompt 类以**源码**为准。完整 Prompt 文本见各文件内 `DIY_PROMPT_*` / `GeneralAnswerGeneratorPrompt` / `GeneralShortCoTGeneratorPrompt` 等定义。

---

## 配置项说明

| 参数 | 含义 |
|------|------|
| `api_url` | Chat Completions 兼容端点 |
| `model_name` | 后端模型名 |
| `first_entry_file_name` | 入口数据（json/jsonl/csv 等） |
| `cache_path` | 中间结果与输出目录 |
| `file_name_prefix` | 分步文件前缀 |
| `cache_type` | 一般为 `jsonl` |
| `input_key` / `output_key` | 见上表 |
| `max_workers` | API 并发上限 |

---

## 运行示例

在**本目录**下执行（路径请改为你的数据与缓存）：

```bash
cd medical
export DF_API_KEY=YOUR_API_KEY

python zhiyou_finance_tagging.py
python zhiyou_finance.py
python zhiyou_medical.py
```

---

## 推荐组合

- **金融**：先 `zhiyou_finance_tagging.py` 打标，再 `zhiyou_finance.py` 生成或增强回答，便于按 `tags` 分任务分析。  
- **医疗**：直接 `zhiyou_medical.py` 为 MedQA / MedMCQA 等生成带短推理链的 `generated_text`；可多轮采样扩充风格。  
