# Data Science 评测说明

数据科学 / 代码数据类能力常用 **OpenCompass** 与 **DS-1000** 等基准；以下为精简指引，完整步骤以官方文档为准。

---

## 框架与数据

| 组件 | 说明 |
|------|------|
| **OpenCompass** | 统一评测框架：[open-compass/opencompass](https://github.com/open-compass/opencompass) |
| **DS-1000** | 数据科学代码生成基准，数据与说明：[xlang-ai/DS-1000](https://github.com/xlang-ai/DS-1000) |
| **OpenCompass 文档** | DS-1000 等服务化评测说明：[OpenCompass 高级指南（代码评测服务）](https://doc.opencompass.org.cn/advanced_guides/code_eval_service.html) |

---

## 建议流程（概要）

1. 安装并配置 OpenCompass（见官方 README）。  
2. 按文档下载或挂载 **DS-1000** 数据。  
3. 在配置中指定待测模型（HF 路径或 API），运行对应 config（名称以 OpenCompass 当前版本为准，如含 `ds1000` 的数据集条目）。  

---

## 相关文档

- 仓库总览见 [Readme.md](../Readme.md)  
- 其他领域评测索引见根目录 Readme 中的「各领域 Evaluation 摘要」  
