---
language:
- en
license: apache-2.0
size_categories:
- 10K<n<100K
task_categories:
- text-generation
- question-answering
tags:
- medical
- healthcare
- geriatric
- elderly-care
- health-advice
- synthetic
- alpaca
pretty_name: Geriatric Health Advice Dataset
configs:
- config_name: default
  data_files:
  - split: train
    path: geriatric_health_data.jsonl
---

# 🏥 Geriatric Health Advice Dataset

<div align="center">

![Dataset Banner](https://img.shields.io/badge/Dataset-Geriatric_Health_Advice-blue?style=for-the-badge)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Samples](https://img.shields.io/badge/Samples-10,813-orange?style=for-the-badge)]()

**High-quality synthetic dataset for training AI assistants to provide geriatric health guidance**

</div>

---

## 🌟 Overview

This dataset contains **10,813 high-quality instruction-response pairs** focused on geriatric health advice for elderly individuals (70+).

### Key Features

✅ **Comprehensive Coverage** - 20+ health categories  
✅ **Safety-Conscious** - Appropriate escalation to emergency services  
✅ **Age-Appropriate** - Clear, simple language for elderly users  
✅ **Actionable Advice** - Specific steps, not generic suggestions  
✅ **Alpaca Format** - Ready for instruction fine-tuning  

---

### 📊 Dataset Statistics

| Attribute | Value |
|-----------|-------|
| Total Samples | 10,743 |
| Format | JSONL (Alpaca-style) |
| Language | English |
| Average Instruction Length | ~15 words |
| Average Response Length | ~80 words |
| Quality Filtered | Yes (70 low-quality samples removed) |

---

## 📋 Data Structure

Each sample follows the Alpaca instruction format:

```json
{
  "instruction": "How can I prevent falls at home?",
  "input": "Patient is elderly (70+), seeking advice on safety.",
  "output": "Install handrails near stairs and in the bathroom. Use non-slip mats in the shower and bathtub. Keep floors clear of clutter. Ensure good lighting throughout your home, especially in hallways and stairs. Consider using a walking aid if you feel unsteady."
}
```

### Fields

- **instruction** (string): The health-related question or concern
- **input** (string): [Optional] Additional context about the patient
- **output** (string): Detailed, actionable health advice

---

## 🏷️ Topics Covered

### Daily Health & Wellness
- 💊 Medication management and reminders
- 🥗 Nutrition and hydration guidelines
- 🏃 Exercise recommendations for seniors
- 😴 Sleep hygiene and rest

### First Aid & Emergency
- 🩹 Minor injury treatment (cuts, burns, bruises)
- 🚨 Emergency response (when to call 911)
- 🤕 Fall prevention and recovery
- 🌡️ Symptom assessment

### Mental & Emotional Health
- 💙 Loneliness and social isolation
- 🧠 Cognitive health maintenance
- 😌 Stress and anxiety management
- 🤝 Connection with support resources

### Chronic Conditions
- 🩺 Blood pressure monitoring
- 💉 Diabetes management
- 🦴 Arthritis pain relief
- 💗 Heart health guidance

### Preventive Care
- 🏠 Home safety modifications
- 🚶 Mobility and balance exercises
- 👁️ Vision and hearing care
- 💪 Maintaining independence

---

## 📁 Data Samples

<details>
<summary><b>Sample 1: Fall Prevention</b></summary>

```json
{
  "instruction": "How can I prevent falls at home?",
  "input": "",
  "output": "Install handrails near stairs and in the bathroom. Use non-slip mats in the shower. Keep floors clear of clutter and ensure good lighting throughout your home, especially in hallways."
}
```

</details>

<details>
<summary><b>Sample 2: Medication Adherence</b></summary>

```json
{
  "instruction": "I keep forgetting to take my pills",
  "input": "Patient is elderly (70+), seeking advice on medication management.",
  "output": "Consider using a pill organizer and fill it weekly. Set reminders on your phone or use an alarm clock. Ask family members to help remind you. Keep medications in a visible spot."
}
```

</details>

<details>
<summary><b>Sample 3: Loneliness</b></summary>

```json
{
  "instruction": "I feel lonely",
  "input": "Patient is elderly (70+), seeking advice on emotional well-being.",
  "output": "Try joining clubs or groups where you can meet people with similar interests. Consider volunteering to help others and connect socially. Regular phone calls can also keep relationships strong. Talk to a counselor if loneliness feels overwhelming."
}
```

</details>

<details>
<summary><b>Sample 4: Emergency - Deep Cut</b></summary>

```json
{
  "instruction": "I cut my hand deeply with a knife and it will not stop bleeding.",
  "input": "Patient is elderly (70+), seeking immediate first aid guidance.",
  "output": "Call 911 or your local emergency number immediately. While waiting for help, use a clean cloth or sterile gauze to apply firm, continuous pressure directly to the wound. Do not lift the cloth to check the wound. If the cloth soaks through, place another one on top and keep pressing. Keep your hand elevated above the level of your heart."
}
```

</details>

---

## 🔬 Data Generation Process

### Step 1: Seed Data Creation
- Initial seed topics and scenarios defined
- Focus on common geriatric health concerns
- Balance between routine care and emergencies

### Step 2: Synthetic Generation
- **Model**: Qwen 2.5 14B Instruct
- **Platform**: Lightning.ai (NVIDIA L40 GPU)
- **Prompt Engineering**: Carefully crafted system prompt emphasizing:
  - Specific, actionable advice
  - Age-appropriate language
  - Safety consciousness
  - Multiple concrete steps per response

### Step 3: Quality Filtering
- Automatic removal of samples with:
  - Missing or empty outputs
  - Extremely short responses (< 10 characters)
  - Invalid JSON formatting
- **Result**: 10,743 valid samples (70 filtered out)

### Step 4: Validation
- Manual review of sample outputs
- Distribution analysis across topics
- Safety review for emergency scenarios

---

## 📥 Download

### Using Datasets Library

```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("YsK-dev/geriatric-health-advice")

# Access splits
print(f"Total samples: {len(dataset['train'])}")

# View sample
print(dataset['train'][0])
```

### Direct Download

```bash
# Download JSONL file
wget https://huggingface.co/datasets/YsK-dev/geriatric-health-advice/resolve/main/geriatric_health_data.jsonl
```

---

## 🎯 Intended Use

### Primary Use Cases

1. **Fine-tuning Language Models**
   - Train models to provide geriatric health advice
   - Improve existing healthcare chatbots
   - Create specialized eldercare assistants

2. **Research**
   - Study synthetic data quality
   - Analyze health advice generation
   - Benchmark model performance on healthcare tasks

3. **Education & Training**
   - Train caregivers and healthcare workers
   - Create educational tools for elderly care
   - Develop healthcare curriculum materials

### Trained Models

This dataset was used to train:
- **[Zima Geriatric Health Assistant](https://huggingface.co/YsK-dev/zima-qwen-geriatric-1.5b)** (Qwen 2.5 1.5B)
  - Perplexity: 1.51
  - Validation Loss: 0.40
  - Production-ready for deployment

---

## ⚠️ Limitations & Considerations

### Important Disclaimers

> **🚨 MEDICAL DISCLAIMER**
> 
> This dataset is for training AI models and research purposes only. It:
> - Is NOT a substitute for professional medical advice
> - Should NOT be used for self-diagnosis
> - Cannot replace emergency medical services
> - Contains general guidance, not personalized treatment

### Known Limitations

1. **Synthetic Data**: Generated by AI, not reviewed by medical professionals
2. **English Only**: Currently no multilingual support
3. **Geographic Limitations**: Advice may not apply to all healthcare systems
4. **Currency**: Medical best practices may evolve; dataset is from 2024
5. **Completeness**: Cannot cover every possible geriatric health scenario

### Bias Considerations

- **Age Focus**: Specifically for 70+ demographic
- **Cultural Context**: May reflect Western healthcare practices
- **Language Simplicity**: Deliberately simplified for elderly comprehension
- **Emergency Bias**: May over-emphasize calling emergency services

---



### How to Contribute

1. **Data Quality**
   - Report errors or inaccuracies
   - Suggest improvements to responses
   - Flag unsafe or inappropriate content

2. **Expansion**
   - Contribute new scenarios
   - Add multilingual translations
   - Include region-specific guidance

3. **Validation**
   - Medical professional review
   - Real-world testing feedback
   - User experience reports

**Contact**: Open an issue on [GitHub](https://github.com/YsK-dev/zima/issues)

---

## 📊 Evaluation Results

Models trained on this dataset have achieved:

| Metric | Zima (Qwen 1.5B) | Notes |
|--------|------------------|-------|
| Perplexity | 1.51 | Excellent (< 2.0) |
| Training Loss | 0.32 | Well-converged |
| Validation Loss | 0.40 | No overfitting |
| Sample Quality | 95%+ | Manual review |

See [evaluation results](evaluation_results.json) for detailed outputs.

---

## 🔄 Dataset Versions

### Current: v1.0 (2024-12-31)
- Initial release
- 10,743 samples
- English only
- Qwen 2.5 14B generated


## 📥 Download & Usage

### Using Datasets Library

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("YsK-dev/geriatric-health-advice")

# View sample
print(f"Total samples: {len(dataset['train'])}")
print(dataset['train'][0])
```

### Direct Download

```bash
# Using wget
wget https://huggingface.co/datasets/YsK-dev/geriatric-health-advice/resolve/main/geriatric_health_data.jsonl

# Using curl
curl -L -o geriatric_health_data.jsonl https://huggingface.co/datasets/YsK-dev/geriatric-health-advice/resolve/main/geriatric_health_data.jsonl
```

---

## 🏷️ Topics Covered

- 💊 Medication management
- 🥗 Nutrition and hydration
- 🏃 Exercise for seniors
- 🩹 First aid guidance
- 💙 Loneliness and mental health
- 🏠 Home safety modifications
- 🦴 Chronic condition management

---

## 🔬 Data Generation

- **Model**: Qwen 2.5 14B Instruct
- **Platform**: Lightning.ai (NVIDIA L40 GPU)
- **Quality Filtering**: Removed samples with empty/short outputs

---

## ⚠️ Disclaimer

> **🚨 MEDICAL DISCLAIMER**: This dataset is for AI training purposes only. Not a substitute for professional medical advice.

---

## 📚 Citation

```bibtex
@misc{geriatric_health_advice2025,
  author = {YsK-dev},
  title = {Geriatric Health Advice Dataset},
  year = {2025},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/datasets/YsK-dev/geriatric-health-advice}},
}
```

---

## 🔗 Related

- **Trained Model**: [YsK-dev/zima-qwen-geriatric-1.5b](https://huggingface.co/YsK-dev/zima-qwen-geriatric-1.5b)

---

<div align="center">

**Made with ❤️ for the elderly community**

</div>
