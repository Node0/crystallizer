# Crystallizer
A Map -> Reduce powerhouse,
disguised as an insight summarization tool.

Crystallizer is a programmable, LLM-powered
general purpose data traversal and transformation tool.

Its default use-case will be as insight extraction
and cohesion across N parts of long documents (think books).

However it can be programmed to do a large number
of open-ended tasks, owing to it's templated
system and task prompt design.

![Crystallizer-Web](https://github.com/user-attachments/assets/97fd2904-10e8-4fe0-96c9-4bd06a8b195e)

## Installation

**📋 [Complete Installation Guide](INSTALLATION.md)** - Choose your preferred tool

### Quick Links by Tool:

- **🚀 [UV Installation](INSTALLATION.md#-uv-recommended---fastest)** - Fastest setup
- **📦 [Poetry Installation](INSTALLATION.md#-poetry-best-for-development)** - Best for development  
- **🐍 [Pip Installation](INSTALLATION.md#-standard-pip-universal)** - Universal compatibility

### Quick Start (pip)

**Requirements**: Python 3.11+

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python crystallizer.py --help
```

## Usage

```bash
python crystallizer.py \
  --system-prompt system_prompt.j2 \
  --haystack-path ./chat_logs \
  --connection ollama-local \
  --task-label gluon_design \
  --output-dir ./crystals
```

## Configuration

Configure each LLM connection in `config.json`:

```json
{
  "inference_service_connections": {
    "ollama-local": {
      "api_type": "ollama",
      "base_url": "http://localhost:11434",
      "default_model": "qwen2.5-coder:32b",
      "default_ctx_len": 18000
    },
    "openai-main": {
      "api_type": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "default_model": "gpt-4o-mini",
      "default_ctx_len": 128000
    }
  }
}
```

## Features

- **Token-Aware Windowing**: Automatically chunks large documents to fit LLM context limits
- **Multi-Provider Support**: Works with Ollama (local) and OpenAI (cloud) backends  
- **Template-Driven Prompts**: Jinja2 templates for custom system prompts
- **Hierarchical Processing**: 3-segment micro-windowing with merge strategies
- **Professional Logging**: Semantic progress tracking with contextual semaphores
- **Batch Processing**: Handle single files or entire directories

## License
GNU AGPLv3
