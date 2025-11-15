"""
Configuration settings for the Langchain Vision Agentic System.
Loads API keys, models, and manages project settings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    These settings are loaded from a .env file in the project root.
    """

    # API Keys
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")

    # Model Configuration
    default_llm_model: str = "gpt-4o"  # Supports vision
    default_vlm_model: str = "gpt-4o"  # Vision-Language Model
    temperature: float = 0.7
    max_tokens: int = 2000

    #Vision Settings
    max_image_size: int = 2048 #Max width/height for images
    supported_image_formats: list[str] = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]

    #Project Paths
    project_root: Path = Path(__file__).parent.parent
    test_dir: Path = project_root / "test_images"

    #Memory / Checkpointing
    use_memory: bool = True
    checkpoint_dir: Path = project_root / "checkpoints"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
    
    def validate_api_keys(self) -> dict[str, bool]:
        """Check which API keys are configured."""
        return {
            "openai": bool(self.OPENAI_API_KEY),
            "anthropic": bool(self.ANTHROPIC_API_KEY)
        }
    
    def get_available_models(self) -> list[str]:
        """Return list of available models based on configured API keys."""
        models = []
        if self.OPENAI_API_KEY:
            models.extend(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
        if self.ANTHROPIC_API_KEY:
            models.extend(["claude-sonnet-4-20250514", "claude-sonnet-3-5-20241022"])
        return models


# Global settings instance
settings = Settings()


# Convenience functions
def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def check_setup() -> bool:
    """
    Check if the project is properly set up with API keys.
    Returns True if at least one API key is configured.
    """
    api_keys = settings.validate_api_keys()
    has_keys = any(api_keys.values())
    
    if not has_keys:
        print("WARNING: No API keys configured!")
        print("Please create a .env file with at least one of:")
        print("  - OPENAI_API_KEY=your_key_here")
        print("  - ANTHROPIC_API_KEY=your_key_here")
        return False

    print("API Keys configured:")
    for provider, configured in api_keys.items():
        status = "[OK]" if configured else "[--]"
        print(f" {status} {provider.upper()}")
    
    return True


if __name__ == "__main__":
    # Test the configuration
    print("Configuration Test\n")
    check_setup()
    print(f"\nAvailable models: {settings.get_available_models()}")
    print(f"Project root: {settings.project_root}")
    print(f"Checkpoint dir: {settings.checkpoint_dir}")


    

