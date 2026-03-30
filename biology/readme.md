# DataFlow-PostTrain Pipeline 脚本说明

本说明面向当前仓库中基于 [DataFlow](https://github.com/OpenDCAI/DataFlow) 编写的后训练数据合成脚本，重点介绍以下三个目录中的实现方式：

- `/Users/miaode/Study/aa/DataFlow-PostTrain/biology`
- `/Users/miaode/Study/aa/DataFlow-PostTrain/computer_sicence`
- `/Users/miaode/Study/aa/DataFlow-PostTrain/data_science`

这些脚本都遵循 DataFlow 的核心思想：将数据处理拆成一组可复用的 `Operator`，再按顺序组织成一个 `Pipeline`。根据 DataFlow 官方文档，典型 Pipeline 由 `storage`、`LLMServing`、`prompt template` 和多个 `operator.run(...)` 步骤组成，开发时通常先 `compile()` 做 key 检查，再 `forward()` 执行实际流程。

---

## 1. 这个仓库里的 Pipeline 在做什么

这个扩展仓库主要不是重写 DataFlow 框架本身，而是基于 DataFlow 已有的推理类算子，快速搭建面向不同领域的后训练数据构造脚本。当前三类方向分别是：

- `biology`：面向生物、化学、分子任务的指令筛选、难化和答案生成
- `computer_sicence`：面向计算机科学论文/技术上下文的复杂问题合成与 CoT 生成
- `data_science`：面向已有数据科学样本的答案优化与推理链增强

如果把这些脚本抽象成统一范式，基本都是下面这几层：

1. 定义 Prompt
2. 配置输入文件与缓存输出路径
3. 配置 LLM API 和模型
4. 选择若干 DataFlow 算子
5. 在 `forward()` 中按步骤串起来
6. 用 `compile()` + `forward(...)` 运行

---

## 2. 通用脚本结构

这几个脚本都复用了 DataFlow 中和“推理数据合成”最相关的组件：

- `ReasoningQuestionFilter`：筛选原始样本是否值得保留
- `ReasoningQuestionGenerator`：把原始问题改写/扩展为更复杂的新任务
- `ReasoningAnswerGenerator`：为任务生成带推理过程或最终答案
- `ReasoningAnswerNgramFilter`：过滤掉复读、低质量或高重复答案
- `FileStorage` / `StreamBatchedFileStorage`：管理输入数据和每一步缓存文件
- `APILLMServing_request`：通过 HTTP API 调用模型

一个最小可复用模板可以概括成：

```python
from dataflow.pipeline import StreamBatchedPipelineABC
from dataflow.utils.storage import StreamBatchedFileStorage
from dataflow.serving import APILLMServing_request
from dataflow.operators.reasoning import (
    ReasoningQuestionGenerator,
    ReasoningAnswerGenerator,
    ReasoningAnswerNgramFilter,
)

class MyPipeline(StreamBatchedPipelineABC):
    def __init__(self):
        super().__init__()

        self.storage = StreamBatchedFileStorage(
            first_entry_file_name="your_input.jsonl",
            cache_path="./workspace/results",
            file_name_prefix="my_domain_",
            cache_type="jsonl",
        )

        self.llm_serving = APILLMServing_request(
            api_url="https://your-api/v1/chat/completions",
            model_name="your-model",
            max_workers=30,
        )

        self.question_gen = ReasoningQuestionGenerator(
            num_prompts=1,
            llm_serving=self.llm_serving,
            prompt_template=...,
        )
        self.answer_gen = ReasoningAnswerGenerator(
            llm_serving=self.llm_serving,
            prompt_template=...,
        )
        self.answer_filter = ReasoningAnswerNgramFilter(
            min_score=0.1,
            max_score=1.0,
            ngrams=5,
        )

    def forward(self):
        self.question_gen.run(
            storage=self.storage.step(),
            input_key="instruction",
        )
        self.answer_gen.run(
            storage=self.storage.step(),
            input_key="instruction",
            output_key="generated_cot",
        )
        self.answer_filter.run(
            storage=self.storage.step(),
            input_question_key="instruction",
            input_answer_key="generated_cot",
        )

if __name__ == "__main__":
    pl = MyPipeline()
    pl.compile()
    pl.forward(batch_size=400, resume_from_last=True)
```

在这套范式里，真正决定领域差异的部分主要有三类：

- Prompt 的角色设定和输出格式
- 输入数据字段名，例如 `instruction`、`combined`、`text`
- 算子链路的长短，例如是否包含过滤、是否需要问题重写

---

## 3. 三类目录的脚本说明

### 3.1 `biology` 目录

`biology` 目录目前包含两个脚本：

- [dataflow_bioinstruct.py](/Users/miaode/Study/aa/DataFlow-PostTrain/biology/dataflow_bioinstruct.py)
- [dataflow_molinstruct_stream_batched.py](/Users/miaode/Study/aa/DataFlow-PostTrain/biology/dataflow_molinstruct_stream_batched.py)

它们服务于同一个目标：把生物/化学/分子类原始指令，升级成更适合专家级 SFT 或推理训练的数据。

#### `dataflow_bioinstruct.py`

这个脚本更像一个“实验版/单机版”原型，重点展示如何定义生物化学领域的 Prompt：

- `DIY_PROMPT_QUESTION`：判断样本是否足够专业，是否含有有效的生物或化学结构信息
- `DIY_PROMPT_SYNTHESIS`：将原始问题扩展成更复杂的跨尺度推理任务
- `DIY_PROMPT_ANSWER`：要求模型输出 `reasoning_trace` 和 `output` 两部分

Pipeline 类是 `DiyReasoning_APIPipeline`，其中已经配置了：

- `FileStorage` 作为存储层
- `APILLMServing_request` 作为 API 模型后端
- `MinHashDeduplicateFilter` 作为去重步骤
- `ReasoningQuestionFilter`
- `ReasoningQuestionGenerator`
- `ReasoningAnswerGenerator`
- `ReasoningAnswerNgramFilter`

目前这个脚本在 `forward()` 中真正启用的只有 `MinHashDeduplicateFilter`，后续几个步骤暂时被注释掉了。因此它更适合作为“Prompt 设计稿 + 流水线草稿”，便于继续补完。

#### `dataflow_molinstruct_stream_batched.py`

这是 `biology` 中更完整、也更适合大规模处理的版本。它改用了 `StreamBatchedPipelineABC` 和 `StreamBatchedFileStorage`，说明目标是流式、分批地处理较大的 JSONL 文件。

当前启用的链路为：

1. `ReasoningQuestionFilter`
2. `ReasoningQuestionGenerator`
3. `ReasoningAnswerGenerator`
4. `ReasoningAnswerNgramFilter`

对应的数据流逻辑可以理解为：

`原始生物/分子指令 -> 质量过滤 -> 难化改写 -> 生成带 CoT 的答案 -> 去重/去复读`

这个脚本最值得复用的点有：

- 使用了比较完整的领域 Prompt 设计
- 已经是标准的分步 Pipeline 写法
- 支持 `batch_size=400` 与 `resume_from_last=True`

如果后续要继续做新的生物方向合成脚本，推荐以这个文件为基础扩展，而不是从零开始写。

### 3.2 `computer_sicence` 目录

该目录当前核心脚本为：

- [dataflow_computer.py](/Users/miaode/Study/aa/DataFlow-PostTrain/computer_sicence/dataflow_computer.py)

这个脚本的定位和 `biology` 不同，它更强调“从技术上下文中抽出冲突，再生成高质量复杂问题”。

它的 Prompt 设计重点是：

- 让模型从论文或技术上下文中识别 `Technical Conflict` 或 `Logical Bottleneck`
- 把原始上下文改造成更像研究面试、技术咨询、理论分析类的问题
- 在答案阶段要求模型输出严格的 JSON，其中包含冲突分析、基础知识映射、推导过程和结论

当前启用的链路是：

1. `ReasoningQuestionGenerator`
2. `ReasoningAnswerGenerator`
3. `ReasoningAnswerNgramFilter`

输入字段不是 `instruction`，而是：

- `input_key="combined"`

这意味着上游原始数据很可能已经把标题、摘要、关键词、方法描述等多字段拼成了一个 `combined` 字段。这个设计很适合处理论文摘要、技术报告、研究综述之类的长上下文样本。

这个脚本适合复用在：

- 论文到问答的重构
- 算法冲突识别类数据合成
- 需要明确理论推导过程的计算机科学 SFT 数据构造

### 3.3 `data_science` 目录

该目录当前核心脚本为：

- [dataflow_datascience.py](/Users/miaode/Study/aa/DataFlow-PostTrain/data_science/dataflow_datascience.py)

这个脚本与前两个目录最大的不同在于：它不是先造新问题，而是直接优化已有样本的 `output`。

Prompt 的要求非常明确：

- 深化 `<Analyze>` 和 `<Understand>` 标签中的推理过程
- 修正潜在错误代码或错误推导
- 保持原有 JSON schema 不变
- 保留 `<Analyze>`、`<Understand>`、`<Answer>` 这样的标签结构

因此它更像一个“答案精修/CoT 增强器”，而不是“问题生成器”。

当前链路是：

1. `ReasoningAnswerGenerator`
2. `ReasoningAnswerNgramFilter`

输入字段为：

- `input_key="text"`

输出字段为：

- `output_key="generated_cot"`

它适合处理已有格式化数据集，例如：

- 已经是 JSON 样本，但答案质量不稳定
- 已经带标签结构，希望增强 reasoning depth
- 已经有人类写好的任务，不希望改动 instruction，只希望优化 answer

---

## 4. 三类脚本的差异总结

| 目录 | 代表脚本 | 主要目标 | 输入字段 | 典型步骤 |
| --- | --- | --- | --- | --- |
| `biology` | `dataflow_molinstruct_stream_batched.py` | 过滤原始样本并合成更难的生物/分子推理数据 | `instruction` | filter -> question gen -> answer gen -> ngram filter |
| `computer_sicence` | `dataflow_computer.py` | 从技术上下文生成复杂 CS 问题并回答 | `combined` | question gen -> answer gen -> ngram filter |
| `data_science` | `dataflow_datascience.py` | 优化已有样本输出并加深 CoT | `text` | answer gen -> ngram filter |

可以把它们理解成三种不同的数据构造策略：

- `biology`：先筛选，再难化，再回答
- `computer_sicence`：基于上下文重构问题，再回答
- `data_science`：不改问题，只精修答案

---

## 5. 如何继续写新的 Pipeline 脚本

如果你后面要在这个仓库里增加新的后训练数据合成脚本，最推荐沿着下面的顺序改：

### 第一步：先想清楚你的任务属于哪一类

- 如果原始数据噪声大，先做过滤，参考 `biology`
- 如果原始数据是上下文材料，需要生成复杂问题，参考 `computer_sicence`
- 如果原始数据已经是较成熟的 QA 样本，只需增强答案，参考 `data_science`

### 第二步：确定输入字段

这是 DataFlow 脚本里最容易出错的地方。必须先明确原始 JSONL 里到底有什么 key，例如：

- `instruction`
- `input`
- `combined`
- `text`

然后在 `run(...)` 里把 `input_key`、`input_question_key`、`input_answer_key` 对齐。DataFlow 官方文档也特别强调，`compile()` 的价值就在于提前检查这些 key 是否匹配。

### 第三步：先写 Prompt，再定算子链

一个新脚本通常至少要决定：

- 是否需要 `ReasoningQuestionFilter`
- 是否需要 `ReasoningQuestionGenerator`
- 是否只用 `ReasoningAnswerGenerator`
- 是否在最后加 `ReasoningAnswerNgramFilter`

经验上建议：

- 数据源较脏时，加过滤
- 想提升任务难度时，加问题生成
- 想稳定输出质量时，加答案生成和最终过滤

### 第四步：统一存储路径和输出前缀

每个脚本都要明确：

- `first_entry_file_name`：原始输入文件
- `cache_path`：中间结果和最终结果保存目录
- `file_name_prefix`：每个 step 的文件名前缀
- `cache_type`：通常为 `jsonl`

建议不同领域使用不同的 `cache_path` 和前缀，避免多个实验写到同一组缓存文件里。

### 第五步：保留 `compile()` 和恢复能力

推荐统一采用：

```python
pl = DiyReasoning_APIPipeline()
pl.compile()
pl.forward(batch_size=400, resume_from_last=True)
```

原因有两点：

- `compile()` 可以提前发现 key 配置错误
- `resume_from_last=True` 适合长时间 API 合成任务中断后继续跑

---

## 6. 编写这类脚本时最常改的地方

几乎每次写新脚本都会改下面这些配置：

### 6.1 数据路径

当前仓库里的脚本很多路径还是绝对路径，例如：

- `/share/project/...`

这些路径显然是实验环境专用路径，迁移到新机器或新项目时必须改成你自己的数据位置。

### 6.2 模型与 API

当前示例中使用了不同模型名，例如：

- `mgg-2`
- `mgg-7`
- `claude-opus-4.5`
- `mog-2`

以及统一风格的接口：

- `https://kspmas.ksyun.com/v1/chat/completions`

这部分需要按你实际可用的 API 网关、模型名和并发限制修改。不要把真实密钥直接写进脚本。

### 6.3 Prompt 输出格式

当前三个目录里已经体现了三种常见输出形式：

- 简单布尔判断 JSON
- 带 `reasoning_trace` 和 `output` 的 JSON
- 保留 XML 风格标签的原始 JSON 对象

建议在 Prompt 中把输出格式写死，这样更利于后处理和过滤。

### 6.4 batch size 与并发

当前脚本多使用：

- `batch_size=400`
- `max_workers=30` 或 `50`

真实运行时要根据：

- API 限速
- 样本长度
- 模型吞吐
- 单次成本

做调整。并发过高时很容易触发失败重试或空响应。

---

## 7. 推荐的 README 使用方式

如果后续这个仓库继续扩展更多领域，可以把每个新目录中的脚本都按下面四个维度补充说明：

1. 脚本要解决什么数据构造问题
2. 输入文件需要哪些字段
3. Pipeline 包含哪些 DataFlow 算子
4. 最终输出新增了哪些字段

这样读者即使不先读代码，也能快速判断：

- 我应该改哪个脚本
- 我应该准备什么格式的数据
- 我应该从哪个步骤接着扩展

---

## 8. 小结

当前仓库中的三类脚本，分别代表了三种很典型的后训练数据合成思路：

- `biology`：面向专业科学任务的筛选、难化和答案生成
- `computer_sicence`：面向技术上下文的复杂问题构造
- `data_science`：面向已有样本的输出修订和 CoT 增强

如果把它们放回 DataFlow 的整体设计里看，本质上都是围绕同一套框架展开：

- 用 `storage` 管数据
- 用 `LLMServing` 管模型调用
- 用 Prompt 决定任务形式
- 用多个 `operator.run(...)` 串成可复用的处理链

后续新增脚本时，最实用的做法就是先选一个最接近的现有目录当模板，再替换 Prompt、输入 key、输出 key 和缓存路径，即可快速形成新的领域 Pipeline。

---

## 参考资料

- DataFlow 官方仓库：[https://github.com/OpenDCAI/DataFlow](https://github.com/OpenDCAI/DataFlow)
- DataFlow 中文文档首页：[https://opendcai.github.io/DataFlow-Doc/zh/](https://opendcai.github.io/DataFlow-Doc/zh/)
- DataFlow 框架设计文档：[https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/](https://opendcai.github.io/DataFlow-Doc/zh/guide/basicinfo/framework/)
