"""
Configuration settings for the Advanced Research Assistant System
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    
    # System Configuration
    SYSTEM_NAME: str = os.getenv("SYSTEM_NAME", "Advanced Research Assistant")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # File Paths
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "./logs")
    
    # Model Configuration
    LLM_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Agent Configuration
    AGENT_CONFIG: Dict[str, Any] = {
        "max_iter": 5,
        "max_execution_time": 300,  # 5 minutes
        "verbose": True,
        "memory": True
    }
    
    # Tool Configuration
    TOOL_CONFIG: Dict[str, Any] = {
        "search_results_limit": 10,
        "content_max_length": 8000,
        "timeout": 30
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        required_keys = ["OPENAI_API_KEY", "SERPER_API_KEY"]
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
        
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)

# Create settings instance
settings = Settings()