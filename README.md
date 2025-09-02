# AI Training Dataset Generator

*Because dataset preparation shouldn't be the hardest part of fine-tuning*

## Why I Built This

Look, I'll be honest with you. I spent way too much time manually creating training datasets for fine-tuning models. You know the drill - you have all this domain knowledge sitting in PDFs, SOPs, and documents, but turning that into actual training data? That's a different beast entirely.

I was working on a medical compliance project (tissue donation stuff - pretty niche), and I needed to fine-tune a model to understand very specific regulatory requirements. Not general medical knowledge, but the exact wording of particular SOPs and how they applied to real scenarios.

After weeks of manually writing scenarios and responses, I thought "there has to be a better way." So I built this tool. It worked so well for my use case that I figured other people might be dealing with the same frustration.

## What This Actually Does

This tool takes your domain knowledge (whatever format it's in) and generates realistic training scenarios with expert-level responses. It's not magic - it uses the knowledge you already have and creates training pairs that actually make sense for your specific field.

Here's what happened when I used it:
- Fed it some medical SOPs (those PDF documents nobody wants to read)
- Got back 50+ realistic compliance scenarios with detailed, accurate responses
- Fine-tuned a model that actually understood the nuances of the regulations
- Saved probably 2-3 weeks of manual dataset creation

## Getting Started (The Real Way)

### First, install the stuff you need:

```bash
git clone this-repo
cd ai-dataset-generator
pip install -r requirements.txt
```

### Get your OpenAI API key sorted:

You'll need an OpenAI API key. Create a `.env` file:

```bash
echo "OPENAI_API_KEY=your_actual_key_here" > .env
```

Don't use the free tier if you're generating a lot of data - you'll hit rate limits fast. I learned this the hard way.

### Add your knowledge:

This is where your domain expertise comes in. The tool can handle:
- PDFs (it'll extract the text for you)
- Markdown files
- Plain text documents

Just dump your knowledge files into the `knowledge_base/` directory. I usually organize by domain:

```
knowledge_base/
├── medical/          # My original use case
├── legal/           # Friend's law firm compliance
├── financial/       # Another project
└── your_domain/     # Whatever you're working on
```

### Configure it for your domain:

The tool comes with some templates I've already set up, but you'll probably want to customize it. Here's what I did for medical compliance:

```python
from ai_dataset_generator import AIDatasetGenerator
from config import ConfigTemplates

# Start with a template
config = ConfigTemplates.medical_compliance()

# Point it to your knowledge
config.knowledge_sources = ["knowledge_base/medical/"]

# Decide how many training pairs you want
config.num_scenarios = 50  # Start small, see how it goes

# Generate the dataset
generator = AIDatasetGenerator(config)
dataset = generator.generate_dataset()
```

That's it. You'll get a `.jsonl` file ready for OpenAI's fine-tuning API.

## What I've Learned Using This

### It's not perfect on the first try
The quality depends a lot on how good your source material is. Garbage in, garbage out. I had to clean up some of my SOPs because they had inconsistent formatting.

### Start small
Don't generate 500 scenarios on your first run. Start with 10-20, see if the quality is what you want, then scale up.

### The prompts matter
The default prompts work okay, but you'll probably want to tweak them for your specific domain. I spent time getting the "expert voice" right for medical compliance.

### PDF quality varies
Some PDFs extract beautifully, others are a mess. If you have important documents that are image-based or have weird formatting, you might need to clean them up first.

## Different Domains I've Tried

### Medical Compliance (My Original Use Case)
Works great for SOPs, clinical protocols, regulatory requirements. The model learns to cite specific sections and requirements, which is crucial for compliance work.

### Legal Stuff (Helped a Friend)
Contract analysis, regulatory compliance, policy interpretation. Lawyers love citing specific statutes, and the model picks up on that pattern.

### Financial Compliance
Banking regulations, risk assessment, securities rules. Lots of "if this, then that" logic that the model handles well.

### Custom Domains
The beauty is you can adapt it to whatever field you're in. Quality assurance, safety procedures, technical documentation - if you have structured knowledge, this can probably help.

## What Files Do You Actually Need?

Let me be straight with you - there are several Python files in this project, but you don't need all of them.

### **Essential Files (You Need These)**
- `ai_dataset_generator.py` - **The main tool**. This is what actually generates your datasets.
- `config.py` - **Configuration system**. Lets you customize for different domains without editing the main code.

### **Really Helpful (But Optional)**
- `knowledge_base_utils.py` - **PDF processing**. If you have PDFs (and you probably do), this extracts text automatically. Without it, you'd need to copy/paste text manually.

### **Nice to Have (Skip If You Want Simple)**
- `get_started.py` - **Interactive setup**. Walks you through first-time setup, but you can just follow this README instead.
- `examples/quick_start_example.py` - **Usage examples**. Shows different ways to use the tool.

### **You Can Delete These**
- `legacy_tissue_dataset_generator.py` - My original version for medical compliance. Just kept it for reference.

**Bottom line**: If you want the absolute minimum, just use `ai_dataset_generator.py` and `config.py`. If you have PDFs, grab `knowledge_base_utils.py` too. Everything else is just convenience.

## The Technical Bits

Under the hood, this uses:
- **Agno framework** for the AI agent (handles the knowledge retrieval)
- **OpenAI's API** for the actual text generation
- **PyMuPDF** for PDF text extraction
- **Python** because, well, it's Python

The tool creates an AI agent that has access to your knowledge base and generates scenarios that require that knowledge to answer correctly. It's not just general knowledge - it's specifically based on your documents.

## Configuration Examples

I've included some configs I've used:

```python
# Medical compliance (my original)
config = ConfigTemplates.medical_compliance()

# Legal compliance (friend's law firm)
config = ConfigTemplates.legal_compliance()

# Custom domain (example: quality assurance)
config = ConfigTemplates.custom(
    domain="Quality Assurance",
    role="QA Expert", 
    task="quality assessment based on standards",
    knowledge_path="knowledge_base/qa/"
)
```

You can also build your own from scratch if the templates don't fit.

## Real Talk About Costs

Using OpenAI's API isn't free. For my 50-scenario medical dataset, I spent maybe $15-20 in API costs. Not terrible, but something to keep in mind. The `gpt-4o-mini` model is cheaper and works fine for most use cases.

## What You'll Get

The tool generates:
1. **Training dataset** in JSONL format (ready for OpenAI fine-tuning)
2. **Raw scenarios** in JSON (for analysis and review)
3. **Configuration file** (so you can reproduce your results)

The training pairs look like real expert conversations:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "We have a donor with a history of melanoma excised 4 years 11 months ago. All other criteria are met. What's the eligibility decision per MD-002?"
    },
    {
      "role": "assistant", 
      "content": "DECISION: REJECT\n\nRATIONALE: Per MD-002 Section 4.3.4, melanoma requires >5 years disease-free, not ≥5 years. At 4 years 11 months, this donor does not meet the >5 year requirement..."
    }
  ]
}
```

## Fine-Tuning Tips (What I Learned)

1. **Quality over quantity**: 50 good examples beats 200 mediocre ones
2. **Review before training**: Always spot-check the generated scenarios
3. **Start with base models**: I used `gpt-3.5-turbo` for my first fine-tune
4. **Test extensively**: Your fine-tuned model will be very specific to your domain

## When This Works Well

- You have structured domain knowledge (SOPs, procedures, regulations)
- You need the model to cite specific sources or sections
- You want consistent, domain-specific responses
- You're dealing with compliance or regulatory stuff

## When It Might Not Help

- Your domain knowledge is mostly tacit/experiential (hard to document)
- You need the model to be creative rather than accurate
- Your source documents are really messy or inconsistent
- You're working with very visual or hands-on domains

## Contributing

I built this for my specific need, but I've tried to make it general enough for other people to use. If you find bugs or have ideas for improvements, feel free to contribute.

Things that would be helpful:
- Support for more document formats (Word docs, web pages)
- Better text extraction from messy PDFs
- More domain-specific templates
- Examples from different fields

## License

MIT License - use it however you want. If it saves you time, great. If you improve it, even better.

## Final Thoughts

Dataset preparation used to be the most tedious part of fine-tuning for me. This tool doesn't eliminate the work entirely, but it makes it manageable. Instead of spending weeks writing training examples, I spend a few hours setting up the knowledge base and reviewing the output.

Your mileage may vary, but if you're sitting on a pile of domain-specific documents and thinking about fine-tuning, this might save you some headaches.

---

*Built by someone who got tired of manual dataset creation. Shared because maybe you're tired of it too.*