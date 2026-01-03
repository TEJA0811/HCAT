"""
Configuration settings for the AI backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AI Model Configuration (provider-agnostic; default to Groq)
    openai_api_key: str = ""  # Not used by default; kept for compatibility
    llm_model: str = "llama-3.1-8b-instant"  # Default model: Groq llama3-8b
    llm_temperature: float = 0.6  # Balanced temperature for consistent but nuanced task assignments
    ollama_base_url: str = ""  # Retained for backward compatibility; not used by default
    
    # NestJS Backend Configuration (using Mock Server)
    nestjs_backend_url: str = "http://localhost:3000"
    
    # Server Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    # LLM timeout (seconds) for API calls
    llm_timeout: float = 180.0
    # LLM provider: 'groq' (default)
    llm_provider: str = "groq"

    # Groq configuration (set in .env when using Groq)
    groq_api_key: Optional[str] = None
    groq_api_url: Optional[str] = "https://api.groq.com/openai/v1/chat/completions"
    # Assignment scoring weights and policy
    assignment_weights: dict = {
        "skill_match": 0.35,
        "experience": 0.25,
        "completion_confidence": 0.2,
        "workload": 0.1,
        "fairness": 0.1,
        "deadline_penalty": 0.15
    }
    # Policy thresholds
    max_allowed_workload: int = 4
    prefer_experience_when_difficulty_gt: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
