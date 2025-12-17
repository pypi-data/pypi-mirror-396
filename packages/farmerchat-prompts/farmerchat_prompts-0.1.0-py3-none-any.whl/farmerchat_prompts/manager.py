"""
Prompt Manager - Central interface for accessing prompts
"""

from typing import Dict, List, Optional
from .models import Prompt, Provider, UseCase
from .prompts import OPENAI_PROMPTS, CLAUDE_PROMPTS, LLAMA_PROMPTS


class PromptManager:
    """
    Central manager for accessing and managing AI prompts across providers
    
    Usage:
        manager = PromptManager()
        prompt = manager.get_prompt("openai", "crop_recommendation")
        messages = prompt.get_full_prompt("I have sandy soil in Bihar")
    """
    
    def __init__(self):
        """Initialize the prompt manager with all available prompts"""
        self._prompts: Dict[str, Dict[str, Prompt]] = {}
        self._load_prompts()
        
    def _load_prompts(self):
        """Load all prompts into the manager"""
        # Load OpenAI prompts
        for prompt in OPENAI_PROMPTS:
            provider = prompt.metadata.provider.value
            use_case = prompt.metadata.use_case.value
            if provider not in self._prompts:
                self._prompts[provider] = {}
            self._prompts[provider][use_case] = prompt
            
        # Load Claude prompts
        for prompt in CLAUDE_PROMPTS:
            provider = prompt.metadata.provider.value
            use_case = prompt.metadata.use_case.value
            if provider not in self._prompts:
                self._prompts[provider] = {}
            self._prompts[provider][use_case] = prompt
            
        # Load Llama prompts
        for prompt in LLAMA_PROMPTS:
            provider = prompt.metadata.provider.value
            use_case = prompt.metadata.use_case.value
            if provider not in self._prompts:
                self._prompts[provider] = {}
            self._prompts[provider][use_case] = prompt
    
    def get_prompt(
        self, 
        provider: str | Provider, 
        use_case: str | UseCase
    ) -> Prompt:
        """
        Get a specific prompt by provider and use case
        
        Args:
            provider: Provider name (openai, claude, llama)
            use_case: Use case name (crop_recommendation, pest_management, etc.)
            
        Returns:
            Prompt object
            
        Raises:
            ValueError: If combination doesn't exist
            
        Example:
            prompt = manager.get_prompt("openai", "crop_recommendation")
        """
        # Convert enums to strings if needed
        provider_str = provider.value if isinstance(provider, Provider) else provider
        use_case_str = use_case.value if isinstance(use_case, UseCase) else use_case
        
        # Validate provider
        if provider_str not in self._prompts:
            available = ", ".join(self._prompts.keys())
            raise ValueError(
                f"Provider '{provider_str}' not found. "
                f"Available providers: {available}"
            )
        
        # Validate use case
        if use_case_str not in self._prompts[provider_str]:
            available = ", ".join(self._prompts[provider_str].keys())
            raise ValueError(
                f"Use case '{use_case_str}' not found for provider '{provider_str}'. "
                f"Available use cases: {available}"
            )
        
        return self._prompts[provider_str][use_case_str]
    
    def get_prompts_by_provider(self, provider: str | Provider) -> List[Prompt]:
        """
        Get all prompts for a specific provider
        
        Args:
            provider: Provider name
            
        Returns:
            List of Prompt objects
            
        Example:
            openai_prompts = manager.get_prompts_by_provider("openai")
        """
        provider_str = provider.value if isinstance(provider, Provider) else provider
        
        if provider_str not in self._prompts:
            return []
        
        return list(self._prompts[provider_str].values())
    
    def get_prompts_by_use_case(self, use_case: str | UseCase) -> List[Prompt]:
        """
        Get all prompts for a specific use case across providers
        
        Args:
            use_case: Use case name
            
        Returns:
            List of Prompt objects
            
        Example:
            crop_prompts = manager.get_prompts_by_use_case("crop_recommendation")
        """
        use_case_str = use_case.value if isinstance(use_case, UseCase) else use_case
        
        prompts = []
        for provider_prompts in self._prompts.values():
            if use_case_str in provider_prompts:
                prompts.append(provider_prompts[use_case_str])
        
        return prompts
    
    def list_all_prompts(self) -> List[Dict[str, str]]:
        """
        List all available prompt combinations
        
        Returns:
            List of dicts with provider and use_case keys
            
        Example:
            all_prompts = manager.list_all_prompts()
            # [{"provider": "openai", "use_case": "crop_recommendation"}, ...]
        """
        prompts = []
        for provider, use_cases in self._prompts.items():
            for use_case in use_cases.keys():
                prompts.append({
                    "provider": provider,
                    "use_case": use_case
                })
        return prompts
    
    def validate_combination(
        self, 
        provider: str | Provider, 
        use_case: str | UseCase
    ) -> bool:
        """
        Check if a provider/use_case combination exists
        
        Args:
            provider: Provider name
            use_case: Use case name
            
        Returns:
            True if combination exists, False otherwise
            
        Example:
            exists = manager.validate_combination("openai", "crop_recommendation")
        """
        try:
            self.get_prompt(provider, use_case)
            return True
        except ValueError:
            return False
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of all available providers
        
        Returns:
            List of provider names
        """
        return list(self._prompts.keys())
    
    def get_available_use_cases(self, provider: Optional[str] = None) -> List[str]:
        """
        Get list of available use cases
        
        Args:
            provider: Optional provider name to filter by
            
        Returns:
            List of use case names
            
        Example:
            all_use_cases = manager.get_available_use_cases()
            openai_use_cases = manager.get_available_use_cases("openai")
        """
        if provider:
            provider_str = provider.value if isinstance(provider, Provider) else provider
            if provider_str in self._prompts:
                return list(self._prompts[provider_str].keys())
            return []
        
        # Get all unique use cases across providers
        use_cases = set()
        for provider_prompts in self._prompts.values():
            use_cases.update(provider_prompts.keys())
        return sorted(list(use_cases))
    
    def search_prompts(self, keyword: str) -> List[Prompt]:
        """
        Search prompts by keyword in description or tags
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching Prompt objects
            
        Example:
            pest_prompts = manager.search_prompts("pest")
        """
        keyword_lower = keyword.lower()
        matching_prompts = []
        
        for provider_prompts in self._prompts.values():
            for prompt in provider_prompts.values():
                # Search in description
                if keyword_lower in prompt.metadata.description.lower():
                    matching_prompts.append(prompt)
                    continue
                
                # Search in tags
                if any(keyword_lower in tag.lower() for tag in prompt.metadata.tags):
                    matching_prompts.append(prompt)
        
        return matching_prompts
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about available prompts
        
        Returns:
            Dict with counts
            
        Example:
            stats = manager.get_stats()
            # {"total_prompts": 15, "providers": 3, "use_cases": 5}
        """
        total = sum(len(use_cases) for use_cases in self._prompts.values())
        return {
            "total_prompts": total,
            "providers": len(self._prompts),
            "use_cases": len(self.get_available_use_cases()),
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"PromptManager("
            f"prompts={stats['total_prompts']}, "
            f"providers={stats['providers']}, "
            f"use_cases={stats['use_cases']})"
        )
