Benchmark 的说明:

Computer Science : 
[MMLU Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro)  ： 使用方法： 直接改 base url 和 model name 就可以，非常方便 ；

Biology: 
[GPQA Dimond](https://github.com/EleutherAI/lm-evaluation-harness)
``` sh
lm-eval run --model hf --model_args pretrained=local_model_path_heere --tasks gpqa_diamond_zeroshot --num_fewshot 5；
``` 

DataScience：
使用了框架 Opencompass 
[ds_1000](https://doc.opencompass.org.cn/advanced_guides/code_eval_service.html) 数据集需要从这里下载[Here](https://github.com/xlang-ai/DS-1000)

