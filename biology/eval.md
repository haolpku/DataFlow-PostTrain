# Biology 评测说明

本文件仅覆盖**生物 / 生化**向常用基准；计算机科学、数据科学评测请分别见：

- [computer_sicence/eval.md](../computer_sicence/eval.md)（MMLU-Pro 等）  
- [data_science/eval.md](../data_science/eval.md)（OpenCompass、DS-1000 等）  

---

## GPQA Diamond

使用 [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) 运行 **GPQA Diamond**（零样本任务名以 harness 版本为准，下例为常见写法）。

```bash
lm_eval run \
  --model hf \
  --model_args pretrained=<本地模型路径> \
  --tasks gpqa_diamond_zeroshot \
  --num_fewshot 5
```

**注意**：将 `<本地模型路径>` 换为实际 checkpoint；`tasks` 名称若与本地 harness 版本不一致，以 `lm_eval --tasks list` 或官方说明为准。

---

## 相关链接

- 仓库总览：[Readme.md](../Readme.md)  
