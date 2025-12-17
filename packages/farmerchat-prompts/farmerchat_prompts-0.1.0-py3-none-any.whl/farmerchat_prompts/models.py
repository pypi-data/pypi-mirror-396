"""
Data models for prompt management
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Provider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    LLAMA = "llama"


class UseCase(str, Enum):
    """Agricultural use cases"""
    CROP_RECOMMENDATION = "crop_recommendation"
    PEST_MANAGEMENT = "pest_management"
    SOIL_ANALYSIS = "soil_analysis"
    WEATHER_ADVISORY = "weather_advisory"
    MARKET_INSIGHTS = "market_insights"


class PromptMetadata(BaseModel):
    """Metadata for a prompt template"""
    provider: Provider
    use_case: UseCase
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    description: str
    tags: list[str] = Field(default_factory=list)


class Prompt(BaseModel):
    """A prompt template with metadata"""
    metadata: PromptMetadata
    system_prompt: str
    user_prompt_template: str
    variables: Dict[str, str] = Field(default_factory=dict)
    examples: Optional[list[Dict[str, str]]] = None
    
    def format(self, **kwargs) -> str:
        """Format the user prompt with provided variables"""
        return self.user_prompt_template.format(**kwargs)
    
    def get_full_prompt(self, user_input: str) -> Dict[str, Any]:
        """
        Get a complete prompt structure ready for API calls
        
        Args:
            user_input: The user's input/query
            
        Returns:
            Dict with provider-specific structure
        """
        if self.metadata.provider == Provider.OPENAI:
            return {
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ]
            }
        elif self.metadata.provider == Provider.CLAUDE:
            return {
                "system": self.system_prompt,
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            }
        elif self.metadata.provider == Provider.LLAMA:
            return {
                "prompt": f"{self.system_prompt}\n\nUser: {user_input}\n\nAssistant:"
            }
        
    def __str__(self) -> str:
        return f"Prompt({self.metadata.provider.value}, {self.metadata.use_case.value})"
