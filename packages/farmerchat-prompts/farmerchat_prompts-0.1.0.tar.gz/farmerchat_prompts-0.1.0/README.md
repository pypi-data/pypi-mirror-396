# FarmerChat Prompts

A Python library for managing AI prompts across multiple providers (OpenAI, Claude, Llama) with use-case specific templates optimized for agricultural applications.

## Features

- 🤖 **Multi-Provider Support**: OpenAI GPT, Anthropic Claude, and Meta Llama
- 🌾 **Agricultural Use Cases**: Crop recommendations, pest management, soil analysis, weather advisories, and market insights
- 🎯 **Optimized Prompts**: Each prompt follows provider-specific best practices
- 🔧 **Easy Integration**: Simple API to access prompts by provider and use case
- 📦 **Type Safe**: Built with Pydantic for runtime validation

## Installation

```bash
pip install farmerchat-prompts
```

## Quick Start

```python
from farmerchat_prompts import PromptManager

# Initialize the prompt manager
manager = PromptManager()

# Get a specific prompt
prompt = manager.get_prompt(
    provider="openai",
    use_case="crop_recommendation"
)

# Use with your AI client
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": "I have sandy soil in Bihar, what should I grow?"}
    ]
)
```

## Supported Providers

- **OpenAI** (`openai`): GPT-3.5, GPT-4
- **Anthropic** (`claude`): Claude 3.5 Sonnet, Claude 3 Opus
- **Meta** (`llama`): Llama 3.1, Llama 3.2

## Use Cases

1. **crop_recommendation**: Get crop suggestions based on soil, climate, and location
2. **pest_management**: Identify pests and get treatment recommendations
3. **soil_analysis**: Analyze soil properties and get improvement suggestions
4. **weather_advisory**: Provide farming advice based on weather conditions
5. **market_insights**: Get market prices and selling recommendations

## Advanced Usage

### List All Available Prompts

```python
# Get all prompts for a provider
openai_prompts = manager.get_prompts_by_provider("openai")

# Get all prompts for a use case
crop_prompts = manager.get_prompts_by_use_case("crop_recommendation")

# Get all available combinations
all_prompts = manager.list_all_prompts()
print(f"Total prompts: {len(all_prompts)}")  # 15 (3 providers × 5 use cases)
```

### Custom Variables

```python
prompt = manager.get_prompt("claude", "weather_advisory")

# Format with custom variables
formatted = prompt.format(
    location="Araria, Bihar",
    current_weather="Heavy rainfall expected",
    crops="Rice, Wheat"
)
```

### Validation

```python
# Check if a combination exists
exists = manager.validate_combination("openai", "crop_recommendation")

# Get metadata
metadata = prompt.metadata
print(f"Provider: {metadata.provider}")
print(f"Use Case: {metadata.use_case}")
print(f"Version: {metadata.version}")
```

## Prompt Engineering Details

Each provider has specific optimizations:

- **OpenAI**: Structured with clear system/user roles, concise instructions
- **Claude**: XML-tagged sections, detailed context, step-by-step reasoning
- **Llama**: Direct instructions, example-based learning, clear formatting

## Development

### Setup

```bash
git clone https://github.com/yourusername/farmerchat-prompts
cd farmerchat-prompts
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black farmerchat_prompts/
flake8 farmerchat_prompts/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Aakash - AI/ML Engineer specializing in agricultural AI systems
