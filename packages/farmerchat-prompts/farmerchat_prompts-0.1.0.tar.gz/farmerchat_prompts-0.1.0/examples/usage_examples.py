"""
Example usage of farmerchat-prompts package

This script demonstrates how to use the package with different AI providers
"""

from farmerchat_prompts import PromptManager, Provider, UseCase


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Initialize the manager
    manager = PromptManager()
    
    # Get a specific prompt
    prompt = manager.get_prompt("openai", "crop_recommendation")
    
    print(f"Provider: {prompt.metadata.provider.value}")
    print(f"Use Case: {prompt.metadata.use_case.value}")
    print(f"Description: {prompt.metadata.description}")
    print(f"\nSystem Prompt Preview: {prompt.system_prompt[:200]}...")
    print(f"\nAvailable Variables: {list(prompt.variables.keys())}")


def example_with_openai():
    """Example with OpenAI API"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Using with OpenAI")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("openai", "crop_recommendation")
    
    # Prepare the full prompt for API call
    user_input = """I have a 2-acre farm in Araria, Bihar. 
    Soil is sandy loam with pH 6.5. 
    Canal irrigation is available. 
    I want to grow crops in the kharif season."""
    
    full_prompt = prompt.get_full_prompt(user_input)
    
    print("Ready for OpenAI API call:")
    print(f"Messages structure: {type(full_prompt['messages'])}")
    print(f"Number of messages: {len(full_prompt['messages'])}")
    
    # Example API call (commented out - requires API key)
    """
    import openai
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=full_prompt["messages"]
    )
    print(response.choices[0].message.content)
    """


def example_with_claude():
    """Example with Claude API"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Using with Claude")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("claude", "pest_management")
    
    user_input = """My tomato plants have yellow spots on leaves. 
    About 30% of plants are affected. 
    Noticed 5 days ago in Bangalore."""
    
    full_prompt = prompt.get_full_prompt(user_input)
    
    print("Ready for Claude API call:")
    print(f"System prompt length: {len(full_prompt['system'])} chars")
    print(f"Number of messages: {len(full_prompt['messages'])}")
    
    # Example API call (commented out - requires API key)
    """
    from anthropic import Anthropic
    
    client = Anthropic(api_key="your-api-key")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=full_prompt["system"],
        messages=full_prompt["messages"],
        max_tokens=2000
    )
    print(response.content[0].text)
    """


def example_with_llama():
    """Example with Llama"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Using with Llama")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("llama", "soil_analysis")
    
    user_input = "My soil pH is 5.2 and organic carbon is 0.3%. What should I do?"
    
    full_prompt = prompt.get_full_prompt(user_input)
    
    print("Ready for Llama:")
    print(f"Prompt structure: {type(full_prompt['prompt'])}")
    print(f"Prompt preview: {full_prompt['prompt'][:300]}...")
    
    # Example with local Llama (commented out)
    """
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    inputs = tokenizer(full_prompt["prompt"], return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=500)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)
    """


def example_formatting():
    """Example of formatting prompts with variables"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Formatting Prompts with Variables")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("openai", "weather_advisory")
    
    # Format with specific variables
    formatted = prompt.format(
        location="Patna, Bihar",
        current_weather="Cloudy, 32°C",
        forecast="Heavy rain expected tomorrow",
        crops="Rice, Wheat",
        growth_stage="Vegetative",
        planned_activities="Pesticide spraying",
        concerns="Rain damage"
    )
    
    print("Formatted user prompt:")
    print(formatted)


def example_exploring_prompts():
    """Example of exploring available prompts"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Exploring Available Prompts")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Get statistics
    stats = manager.get_stats()
    print(f"Total prompts: {stats['total_prompts']}")
    print(f"Providers: {stats['providers']}")
    print(f"Use cases: {stats['use_cases']}")
    
    # List all providers
    print(f"\nAvailable providers: {manager.get_available_providers()}")
    
    # List all use cases
    print(f"\nAvailable use cases: {manager.get_available_use_cases()}")
    
    # Get all prompts for a provider
    openai_prompts = manager.get_prompts_by_provider("openai")
    print(f"\nOpenAI prompts: {len(openai_prompts)}")
    for p in openai_prompts:
        print(f"  - {p.metadata.use_case.value}")
    
    # Get all prompts for a use case
    crop_prompts = manager.get_prompts_by_use_case("crop_recommendation")
    print(f"\nCrop recommendation prompts: {len(crop_prompts)}")
    for p in crop_prompts:
        print(f"  - {p.metadata.provider.value}")


def example_searching():
    """Example of searching prompts"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Searching Prompts")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Search by keyword
    pest_prompts = manager.search_prompts("pest")
    print(f"Prompts related to 'pest': {len(pest_prompts)}")
    for p in pest_prompts:
        print(f"  - {p.metadata.provider.value}/{p.metadata.use_case.value}")
    
    soil_prompts = manager.search_prompts("soil")
    print(f"\nPrompts related to 'soil': {len(soil_prompts)}")
    for p in soil_prompts:
        print(f"  - {p.metadata.provider.value}/{p.metadata.use_case.value}")


def example_validation():
    """Example of validating combinations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Validating Combinations")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Valid combinations
    print(f"openai + crop_recommendation: {manager.validate_combination('openai', 'crop_recommendation')}")
    print(f"claude + pest_management: {manager.validate_combination('claude', 'pest_management')}")
    
    # Invalid combinations
    print(f"openai + invalid: {manager.validate_combination('openai', 'invalid')}")
    print(f"invalid + crop_recommendation: {manager.validate_combination('invalid', 'crop_recommendation')}")


def example_all_use_cases():
    """Example showing all use cases for each provider"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Complete Matrix of Prompts")
    print("=" * 60)
    
    manager = PromptManager()
    
    providers = manager.get_available_providers()
    use_cases = manager.get_available_use_cases()
    
    print(f"\n{'Provider':<15} {'Use Case':<25} {'Available'}")
    print("-" * 60)
    
    for provider in providers:
        for use_case in use_cases:
            available = "✓" if manager.validate_combination(provider, use_case) else "✗"
            print(f"{provider:<15} {use_case:<25} {available}")


def example_real_world_usage():
    """Example of real-world usage pattern"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Real-World Usage Pattern")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Farmer's input from API/UI
    farmer_input = {
        "query": "What crops should I grow?",
        "location": "Araria, Bihar",
        "soil_type": "Sandy loam",
        "soil_ph": "6.5",
        "farm_size": "2 acres",
        "water_availability": "Canal irrigation",
        "additional_info": "Want to grow in kharif season"
    }
    
    # Select appropriate provider based on requirements
    # (e.g., OpenAI for speed, Claude for detailed analysis, Llama for local deployment)
    provider = "claude"  # Using Claude for detailed recommendations
    use_case = "crop_recommendation"
    
    # Get the prompt
    prompt = manager.get_prompt(provider, use_case)
    
    # Format the user prompt with farmer's data
    user_prompt = prompt.user_prompt_template.format(**farmer_input)
    
    # Get full prompt for API call
    full_prompt = prompt.get_full_prompt(user_prompt)
    
    print(f"Selected: {provider}/{use_case}")
    print(f"\nFormatted prompt length: {len(user_prompt)} chars")
    print(f"System prompt length: {len(full_prompt['system'])} chars")
    print(f"\nReady to send to {provider.upper()} API")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_with_openai()
    example_with_claude()
    example_with_llama()
    example_formatting()
    example_exploring_prompts()
    example_searching()
    example_validation()
    example_all_use_cases()
    example_real_world_usage()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
