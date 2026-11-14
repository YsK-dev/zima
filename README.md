# Zima: everyday health advice for people over 70

A small language model that gives short, practical health advice to older people, in English.
It is Qwen2.5-1.5B-Instruct fine-tuned with LoRA on a synthetic dataset made for this project.

- **Model:** [YsK-dev/zima-qwen-geriatric-1.5b](https://huggingface.co/YsK-dev/zima-qwen-geriatric-1.5b)
- **Dataset:** [YsK-dev/geriatric-health-advice](https://huggingface.co/datasets/YsK-dev/geriatric-health-advice)

> **Not medical advice.** Zima is a learning project. Its training data was written by another
> language model and was not checked by doctors or nurses. Do not use it to decide on treatment.
> In an emergency, call your local emergency number.

## How it was built

1. **Seed examples.** Question–answer examples in `seed_data/`.
2. **Synthetic data.** `data_creation/data_creation_lightning.py` asked Qwen2.5-14B (through
   Ollama, on a cloud GPU) to write many more question–answer pairs in the style of the seeds.
   Result: 10,813 pairs in `generated_data/`. Many are copies: of the 10,778 pairs used, 4,741
   are different from each other, with 1,957 different questions.
3. **Preparation.** `training/prepare_data.py` drops answers shorter than 10 characters
   (10,778 pairs left), formats them as instruction–response prompts and splits them at random:
   9,700 for training, 1,078 held out.
4. **Fine-tuning.** `training/train_unsloth.py`: QLoRA (LoRA rank 16, alpha 32, on a 4-bit
   copy of Qwen2.5-1.5B-Instruct) with Unsloth, 3 epochs, learning rate 2e-4, batch size 8 with 4
   accumulation steps (32 pairs per update), up to 512 tokens per pair. The checkpoint with
   the lowest loss on the held-out pairs was kept. The resulting adapter is in `trained_model/`.

## Results

| Measure | Value |
|---|---|
| Perplexity on the first 100 held-out pairs | 1.51 |
| Of those 100, pairs that also appear in the training pairs | 90 |
| All held-out pairs that also appear in the training pairs | 951 of 1,078 (88%) |
| Held-out questions that also appear in the training pairs | 1,035 of 1,078 (96%) |
| Example answers saved for reading | 50 |

The perplexity and the examples are in `trained_model/evaluation_results.json`, written by
`training/evaluate_model.py`. The overlap comes from `training/check_overlap.py`, which rebuilds
the same split; two pairs count as the same when they match apart from capital letters and
punctuation.

What this means: most held-out pairs were also seen in training, so the low perplexity mostly
shows that the model learned the dataset, not that it answers new questions well. Two more things
make it lower: it is computed over the whole prompt, including the fixed template text, and the
same held-out pairs were used to pick the checkpoint. It also says nothing about whether the
advice is correct or safe.

**Next step:** remove the copies; split by question into training, validation (to pick the
checkpoint) and test parts, so that no question is in two parts; train again; and measure on the
test part, on the answer text only, next to the base model.

## Try it

The demo shows the base model and Zima side by side for the same question, so you can compare
them.

```bash
pip install -r demo/requirements.txt
python demo/app.py            # local only; add --share for a temporary public link
```

On a machine with an NVIDIA GPU it uses Unsloth with 4-bit weights; otherwise it runs on the CPU
with Transformers and PEFT (slower). `demo/requirements.txt` includes the GPU packages (Unsloth,
bitsandbytes); on a machine without an NVIDIA GPU, install `torch transformers peft gradio`
instead.

Or load the model from Hugging Face:

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "YsK-dev/zima-qwen-geriatric-1.5b",
    max_seq_length=512,
    load_in_4bit=True,
)
```

## Repository layout

```
seed_data/        seed examples
data_creation/    synthetic data generation (Qwen2.5-14B through Ollama)
generated_data/   the generated dataset (JSONL)
training/         data preparation, fine-tuning and evaluation scripts
trained_model/    the LoRA adapter, tokenizer and evaluation results
demo/             Gradio app: base model and Zima side by side
```

## Limits

- English only.
- The data was written by a language model, so it can repeat that model's mistakes.
- No test yet of whether the model sends real emergencies (chest pain, stroke signs, a fall with a
  head injury) to a doctor or emergency services.

## Licence

Apache 2.0, as stated on the Hugging Face model and dataset pages. The base model,
Qwen2.5-1.5B-Instruct, is also Apache 2.0.
