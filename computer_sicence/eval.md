# Computer Science 评测说明

本目录数据 Pipeline 的配套评测以 **MMLU-Pro** 等为参考；具体对接方式取决于你使用的评测框架（OpenAI 兼容 API、vLLM 等）。

---

## 推荐基准：MMLU-Pro

- **仓库**：[TIGER-AI-Lab/MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro)  
- **特点**：较 MMLU 更细粒度、难度更高，适合衡量模型在多学科选择题上的表现。  
- **使用方式**：在评测脚本中配置模型的 **base URL** 与 **model name**，与本地或远程推理服务对齐即可（以该仓库 README 为准）。  

---

## 实践建议

- 确认评测侧 `model` 名称与推理服务 `served-model-name` 一致。  
- 若结果异常，优先检查 **chat template** 与选项格式是否与训练 / 推理一致。  

---

## 相关文档

- 生物等方向评测见 [biology/eval.md](../biology/eval.md)  
- 仓库总览见 [Readme.md](../Readme.md)  
