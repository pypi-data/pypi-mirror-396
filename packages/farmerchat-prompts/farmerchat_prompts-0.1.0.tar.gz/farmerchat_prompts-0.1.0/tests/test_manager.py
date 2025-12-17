"""
Tests for farmerchat-prompts package
"""

import pytest
from farmerchat_prompts import PromptManager, Provider, UseCase


class TestPromptManager:
    """Test cases for PromptManager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_initialization(self):
        """Test manager initializes correctly"""
        assert self.manager is not None
        stats = self.manager.get_stats()
        assert stats["total_prompts"] == 15  # 3 providers × 5 use cases
        assert stats["providers"] == 3
        assert stats["use_cases"] == 5
    
    def test_get_prompt_valid(self):
        """Test getting valid prompt"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        assert prompt is not None
        assert prompt.metadata.provider == Provider.OPENAI
        assert prompt.metadata.use_case == UseCase.CROP_RECOMMENDATION
    
    def test_get_prompt_with_enums(self):
        """Test getting prompt with enum values"""
        prompt = self.manager.get_prompt(
            Provider.CLAUDE, 
            UseCase.PEST_MANAGEMENT
        )
        assert prompt is not None
        assert prompt.metadata.provider == Provider.CLAUDE
    
    def test_get_prompt_invalid_provider(self):
        """Test getting prompt with invalid provider"""
        with pytest.raises(ValueError, match="Provider 'invalid' not found"):
            self.manager.get_prompt("invalid", "crop_recommendation")
    
    def test_get_prompt_invalid_use_case(self):
        """Test getting prompt with invalid use case"""
        with pytest.raises(ValueError, match="Use case 'invalid' not found"):
            self.manager.get_prompt("openai", "invalid")
    
    def test_get_prompts_by_provider(self):
        """Test getting all prompts for a provider"""
        prompts = self.manager.get_prompts_by_provider("openai")
        assert len(prompts) == 5
        assert all(p.metadata.provider == Provider.OPENAI for p in prompts)
    
    def test_get_prompts_by_use_case(self):
        """Test getting all prompts for a use case"""
        prompts = self.manager.get_prompts_by_use_case("crop_recommendation")
        assert len(prompts) == 3  # One for each provider
        assert all(
            p.metadata.use_case == UseCase.CROP_RECOMMENDATION 
            for p in prompts
        )
    
    def test_list_all_prompts(self):
        """Test listing all prompt combinations"""
        all_prompts = self.manager.list_all_prompts()
        assert len(all_prompts) == 15
        
        # Check structure
        first = all_prompts[0]
        assert "provider" in first
        assert "use_case" in first
    
    def test_validate_combination(self):
        """Test validation of provider/use_case combinations"""
        assert self.manager.validate_combination("openai", "crop_recommendation")
        assert self.manager.validate_combination(Provider.CLAUDE, UseCase.SOIL_ANALYSIS)
        assert not self.manager.validate_combination("openai", "invalid")
        assert not self.manager.validate_combination("invalid", "crop_recommendation")
    
    def test_get_available_providers(self):
        """Test getting list of providers"""
        providers = self.manager.get_available_providers()
        assert len(providers) == 3
        assert "openai" in providers
        assert "claude" in providers
        assert "llama" in providers
    
    def test_get_available_use_cases(self):
        """Test getting list of use cases"""
        use_cases = self.manager.get_available_use_cases()
        assert len(use_cases) == 5
        assert "crop_recommendation" in use_cases
        assert "pest_management" in use_cases
        
        # Test filtering by provider
        openai_cases = self.manager.get_available_use_cases("openai")
        assert len(openai_cases) == 5
    
    def test_search_prompts(self):
        """Test searching prompts by keyword"""
        # Search in description
        results = self.manager.search_prompts("pest")
        assert len(results) == 3  # One per provider
        
        # Search in tags
        results = self.manager.search_prompts("soil")
        assert len(results) >= 3
        
        # No results
        results = self.manager.search_prompts("nonexistent")
        assert len(results) == 0


class TestPrompt:
    """Test cases for Prompt model"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
        self.prompt = self.manager.get_prompt("openai", "crop_recommendation")
    
    def test_prompt_structure(self):
        """Test prompt has required fields"""
        assert self.prompt.metadata is not None
        assert self.prompt.system_prompt is not None
        assert self.prompt.user_prompt_template is not None
        assert isinstance(self.prompt.variables, dict)
    
    def test_format_method(self):
        """Test prompt formatting"""
        formatted = self.prompt.format(
            location="Bihar",
            soil_type="Loamy",
            soil_ph="6.5",
            climate="Tropical",
            water_availability="High",
            farm_size="2 acres",
            additional_info="Planning for kharif season"
        )
        assert "Bihar" in formatted
        assert "Loamy" in formatted
        assert "6.5" in formatted
    
    def test_get_full_prompt_openai(self):
        """Test getting full prompt for OpenAI"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        full = prompt.get_full_prompt("I have sandy soil, what should I grow?")
        
        assert "messages" in full
        assert len(full["messages"]) == 2
        assert full["messages"][0]["role"] == "system"
        assert full["messages"][1]["role"] == "user"
    
    def test_get_full_prompt_claude(self):
        """Test getting full prompt for Claude"""
        prompt = self.manager.get_prompt("claude", "crop_recommendation")
        full = prompt.get_full_prompt("I need crop recommendations")
        
        assert "system" in full
        assert "messages" in full
        assert full["messages"][0]["role"] == "user"
    
    def test_get_full_prompt_llama(self):
        """Test getting full prompt for Llama"""
        prompt = self.manager.get_prompt("llama", "crop_recommendation")
        full = prompt.get_full_prompt("What crops should I grow?")
        
        assert "prompt" in full
        assert "User:" in full["prompt"]
        assert "Assistant:" in full["prompt"]


class TestProviderSpecificPrompts:
    """Test provider-specific prompt characteristics"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_openai_prompt_style(self):
        """Test OpenAI prompts follow expected style"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        
        # Should have clear system prompt
        assert len(prompt.system_prompt) > 100
        assert "expert" in prompt.system_prompt.lower()
        
        # Should have user template
        assert "{location}" in prompt.user_prompt_template
        assert "{soil_type}" in prompt.user_prompt_template
    
    def test_claude_prompt_style(self):
        """Test Claude prompts follow expected style (XML tags)"""
        prompt = self.manager.get_prompt("claude", "crop_recommendation")
        
        # Should use XML tags
        assert "<role>" in prompt.system_prompt or "<expertise>" in prompt.system_prompt
        assert "<" in prompt.system_prompt and ">" in prompt.system_prompt
        
        # Should have detailed structure
        assert len(prompt.system_prompt) > 500  # Claude prompts are verbose
    
    def test_llama_prompt_style(self):
        """Test Llama prompts follow expected style (direct instructions)"""
        prompt = self.manager.get_prompt("llama", "crop_recommendation")
        
        # Should have clear ROLE and INSTRUCTIONS
        assert "ROLE:" in prompt.system_prompt
        assert "INSTRUCTIONS:" in prompt.system_prompt or "EXAMPLE" in prompt.system_prompt
        
        # Should be example-driven
        assert "EXAMPLE" in prompt.system_prompt


class TestUseCaseCoverage:
    """Test that all use cases are properly covered"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_all_use_cases_have_all_providers(self):
        """Test each use case has prompts for all providers"""
        use_cases = [
            "crop_recommendation",
            "pest_management", 
            "soil_analysis",
            "weather_advisory",
            "market_insights"
        ]
        providers = ["openai", "claude", "llama"]
        
        for use_case in use_cases:
            prompts = self.manager.get_prompts_by_use_case(use_case)
            assert len(prompts) == 3, f"{use_case} missing providers"
            
            provider_names = {p.metadata.provider.value for p in prompts}
            assert provider_names == set(providers)
    
    def test_all_providers_have_all_use_cases(self):
        """Test each provider has prompts for all use cases"""
        use_cases = {
            "crop_recommendation",
            "pest_management", 
            "soil_analysis",
            "weather_advisory",
            "market_insights"
        }
        providers = ["openai", "claude", "llama"]
        
        for provider in providers:
            prompts = self.manager.get_prompts_by_provider(provider)
            assert len(prompts) == 5, f"{provider} missing use cases"
            
            case_names = {p.metadata.use_case.value for p in prompts}
            assert case_names == use_cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
