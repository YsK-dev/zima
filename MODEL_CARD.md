---
language:
- en
license: apache-2.0
library_name: transformers
tags:
- medical
- healthcare
- geriatric
- elderly-care
- health-advice
- unsloth
- qwen2.5
- lora
- fine-tuned
base_model: unsloth/Qwen2.5-1.5B-Instruct
datasets:
- YsK-dev/geriatric-health-advice
metrics:
- perplexity
model-index:
- name: Zima Geriatric Health Assistant
  results:
  - task:
      type: text-generation
    metrics:
    - name: Perplexity
      type: perplexity
      value: 1.51
    - name: Final Training Loss
      type: loss
      value: 0.32
    - name: Validation Loss
      type: loss
      value: 0.40
---

# 🏥 Zima: Geriatric Health Assistant

<div align="center">

![Zima Banner](https://img.shields.io/badge/Zima-Geriatric_Health_Assistant-blue?style=for-the-badge)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Models-yellow?style=for-the-badge)](https://huggingface.co/YsK-dev)

**A specialized AI assistant providing compassionate, actionable health guidance for elderly individuals (70+)**

[Try it Now](#quick-start) • [Dataset](https://huggingface.co/datasets/YsK-dev/geriatric-health-advice) • [Report Issues](https://github.com/YsK-dev/zima/issues)

</div>

---

## 🌟 What Makes Zima Special?

Zima is a fine-tuned **Qwen 2.5 1.5B** model specifically designed to assist elderly individuals with health-related questions. Unlike general-purpose chatbots, Zima:

✅ **Age-Appropriate Communication** - Uses clear, simple language  
✅ **Safety-First Approach** - Prioritizes user safety, knows when to recommend emergency services  
✅ **Actionable Advice** - Provides specific, implementable steps rather than generic suggestions  
✅ **Comprehensive Coverage** - Handles everything from daily wellness to first aid  
✅ **Compact & Efficient** - Only 1.5B parameters, perfect for edge deployment  

---

## 📊 Performance Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Perplexity** | 1.51 | 🏆 Excellent (< 2.0) |
| **Training Loss** | 0.32 | ✅ Converged |
| **Validation Loss** | 0.40 | ✅ No overfitting |
| **Training Samples** | 10,743 | 📚 High quality |
| **Model Size** | 71 MB (LoRA) | 🚀 Edge-ready |

---

## 🚀 Quick Start

### Installation

```bash
pip install unsloth transformers torch
```

### Basic Usage

```python
from unsloth import FastLanguageModel

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    "YsK-dev/zima-qwen-geriatric-1.5b",
    max_seq_length=512,
    dtype=None,
    load_in_4bit=True,
)

# Enable inference mode
FastLanguageModel.for_inference(model)

# Create prompt
prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
How can I prevent falls at home?

### Input:
Patient is elderly (70+), seeking advice on safety.

### Response:
"""

# Generate response
inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256, temperature=0.7)
response = tokenizer.batch_decode(outputs)[0]

print(response)
```

### Expected Output

```
Install handrails near stairs and in the bathroom. Use non-slip mats in the shower 
and bathtub. Keep floors clear of clutter. Ensure good lighting throughout your 
home, especially in hallways and near stairs. Consider using a walking aid if you 
feel unsteady. Remove loose rugs or secure them with non-slip backing.
```

---

## 💡 Use Cases

### Daily Health Guidance
- Medication reminders and management
- Nutrition and hydration advice
- Exercise recommendations for seniors
- Sleep hygiene tips

### First Aid & Emergency
- Minor injury treatment (cuts, burns, bruises)
- Fall prevention and recovery
- Recognizing when to seek emergency help
- Symptom assessment

### Mental & Emotional Well-being
- Loneliness and social isolation
- Cognitive health maintenance
- Stress management techniques
- Connection with support resources

### Chronic Condition Management
- Blood pressure monitoring
- Diabetes management tips
- Arthritis pain relief
- Medication adherence strategies

---

## 🔬 Training Details

### Base Model
- **Architecture**: Qwen 2.5 1.5B Instruct
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **Quantization**: 4-bit for efficiency

### Training Configuration
```yaml
LoRA Configuration:
  rank: 16
  alpha: 32
  dropout: 0.05
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]

Training Hyperparameters:
  batch_size: 8 (effective: 32 with gradient accumulation)
  learning_rate: 2e-4
  scheduler: cosine
  epochs: 3
  optimizer: AdamW 8-bit
  
Hardware:
  GPU: NVIDIA L4 (22GB VRAM)
  Training time: 34 minutes
  Framework: Unsloth (2x faster than standard)
```

### Dataset
- **Source**: [geriatric-health-advice](https://huggingface.co/datasets/YsK-dev/geriatric-health-advice)
- **Size**: 10,743 high-quality samples
- **Split**: 90% train / 10% validation
- **Format**: Alpaca-style instruction-following
- **Generation**: Synthetic data from Qwen 2.5 14B

---

## 📋 Example Conversations

<details>
<summary><b>Example 1: Common Cold</b></summary>

**User**: I have a cold

**Zima**: Rest and drink plenty of fluids like warm water, tea or soup. Use saline nasal spray to clear congestion. Take over-the-counter decongestants if needed. Avoid close contact with others. See your doctor for severe symptoms. Stay home until you feel better.

</details>

<details>
<summary><b>Example 2: Loneliness</b></summary>

**User**: I feel lonely

**Zima**: Try joining clubs or groups where you can meet people with similar interests. Consider volunteering to help others and connect socially. Regular phone calls can also keep relationships strong. Talk to a counselor if loneliness feels overwhelming.

</details>

<details>
<summary><b>Example 3: Medication Management</b></summary>

**User**: I keep forgetting to take my pills

**Zima**: Consider using a pill organizer and fill it weekly. Set reminders on your phone or use an alarm clock. Ask family members to help remind you. Keep your medications in a visible spot where you'll see them daily. Talk to your pharmacist about once-daily formulations if available.

</details>

---

## ⚠️ Limitations & Safety

### Important Disclaimers

> **🚨 NOT A REPLACEMENT FOR PROFESSIONAL MEDICAL CARE**
> 
> Zima is designed to provide general health guidance and support, but it:
> - Cannot diagnose medical conditions
> - Cannot prescribe medications
> - Cannot replace emergency services (911)
> - Cannot provide personalized medical treatment plans

### Known Limitations

1. **Emergency Responses**: May be verbose in critical situations (working on v2)
2. **Language**: Currently English-only
3. **Geographic Specificity**: Advice is general and may not apply to all regions
4. **Personalization**: Cannot access individual medical histories

### When to Seek Professional Help

Always contact a healthcare provider or emergency services for:
- Chest pain or difficulty breathing
- Severe bleeding that won't stop
- Loss of consciousness
- Sudden vision or speech changes
- Severe allergic reactions
- Any life-threatening emergency

---

## 🛠️ Advanced Usage

### Deployment on Edge Devices

Zima is optimized for deployment on resource-constrained devices like Raspberry Pi 5:

```bash
# Quantize to GGUF for even smaller size
python quantize_to_gguf.py --model YsK-dev/zima-qwen-geriatric-1.5b --quant q4_k_m

# Run inference on CPU
from llama_cpp import Llama
model = Llama(model_path="zima-q4_k_m.gguf")
```

### API Server

```python
from fastapi import FastAPI
from unsloth import FastLanguageModel

app = FastAPI()
model, tokenizer = FastLanguageModel.from_pretrained("YsK-dev/zima-qwen-geriatric-1.5b")

@app.post("/advice")
async def get_advice(question: str):
    # Generate response
    return {"advice": generated_text}
```

### Gradio Demo

```python
import gradio as gr
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained("YsK-dev/zima-qwen-geriatric-1.5b")

def get_advice(question):
    # Generate response logic
    return response

demo = gr.Interface(
    fn=get_advice,
    inputs=gr.Textbox(placeholder="Ask a health-related question..."),
    outputs=gr.Textbox(),
    title="🏥 Zima: Your Geriatric Health Assistant"
)

demo.launch()
```

---

## 📈 Future Roadmap

- [ ] **v2.0**: More concise emergency responses
- [ ] **Multilingual Support**: Spanish, French, German, Chinese
- [ ] **Voice Interface**: Integration with speech-to-text/text-to-speech
- [ ] **Mobile App**: iOS and Android applications
- [ ] **Telehealth Integration**: Connect with real healthcare providers
- [ ] **Personalization**: User profile and medical history awareness

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

- **Data Collection**: More diverse geriatric health scenarios
- **Evaluation**: Testing model responses for accuracy
- **Documentation**: Improving guides and examples
- **Localization**: Translations to other languages
- **Integration**: Building apps and tools using Zima

---

## 📄 License

This model is released under the **Apache 2.0 License**. You are free to:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Use for research

---

## 🙏 Acknowledgments

- **Unsloth**: For their incredible training optimizations (2x speedup!)
- **Qwen Team**: For the excellent base model
- **Lightning.ai**: For free GPU compute
- **HuggingFace**: For hosting and community

---

## 📧 Contact

- **Developer**: YsK-dev
- **Issues**: [GitHub Issues](https://github.com/YsK-dev/zima/issues)
- **Email**: [Your Email if you want to add it]
- **HuggingFace**: [@YsK-dev](https://huggingface.co/YsK-dev)

---

## 📚 Citation

If you use Zima in your research, please cite:

```bibtex
@misc{zima2025,
  author = {YsK-dev},
  title = {Zima: A Geriatric Health Assistant},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/YsK-dev/zima-qwen-geriatric-1.5b}},
}
```

---

<div align="center">

**Made with ❤️ for the elderly community**

[![Star on GitHub](https://img.shields.io/github/stars/YsK-dev/zima?style=social)](https://github.com/YsK-dev/zima)
[![Follow on HF](https://img.shields.io/badge/Follow-%40YsK--dev-yellow?logo=huggingface&style=social)](https://huggingface.co/YsK-dev)

</div>
