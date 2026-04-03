# Medical & Finance 评测说明

本文档整理 **MedXpertQA**（医疗）与 **PIXIU**（金融）相关流程，并与仓库内脚本对应：

- [medical_eval.sh](medical_eval.sh)  
- [finance_eval.sh](finance_eval.sh)  

> 文中出现的**绝对路径**为历史环境示例，请全部替换为你本机的 conda、工程与基准仓库路径。

---

## 0. 前置条件

- 已准备好待测模型权重与推理环境。  
- 建议 **tmux** 分窗：一窗起模型服务，一窗跑推理与评分。  
- **服务名、模型名**须在「启动脚本 / `model_info.json` / 推理脚本 / `eval.py`」等处保持一致。

---

## 1. 医疗：MedXpertQA

### 1.1 启动推理服务（示例：SGLang）

按你环境激活 conda，并修改启动脚本中的**模型路径**与 **served model name**，例如：

```bash
# 示例：按本机修改路径与环境
conda activate sglang
bash /path/to/your/launch_reward_server.sh
```

在 MedXpertQA 评测包的 `config/model_info.json` 中注册**同名**模型。

### 1.2 推理

进入 MedXpertQA 的 `eval` 目录，修改 `scripts/run_baai.sh` 中的默认模型名、`model_info.json` 中的条目，然后：

```bash
bash scripts/run_baai.sh
```

### 1.3 评分

将 `eval.py` 中的 `model = "..."` 改为当前使用的模型标识，再执行：

```bash
python3 eval.py
```

---

## 2. 金融：PIXIU

进入 PIXIU 工程目录，激活环境后，修改 `scripts/run_evaluation_baai.sh`（或等价脚本）中的 `--model_args`，使 `pretrained` 与 `tokenizer` 指向待测模型，然后：

```bash
bash scripts/run_evaluation_baai.sh
```

---

## 3. 排错清单

- [ ] 推理服务已监听且模型名与评测配置一致  
- [ ] tokenizer 与权重匹配  
- [ ] conda 环境（如服务用 `sglang`、评测用 `pixiu`）正确  
- [ ] 无硬编码旧集群路径导致找不到文件  

---

## 相关链接

- 仓库总览：[Readme.md](../Readme.md)  
