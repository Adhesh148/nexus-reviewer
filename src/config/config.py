from enum import Enum
from pydantic_settings import BaseSettings

class EnvironmentType(str, Enum):
    SANDBOX = "sandbox"
    PROD = "prod"
    
class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True

class Config(BaseConfig):
    DEBUG: int = 0
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: str = EnvironmentType.SANDBOX
    OPENAI_API_KEY: str| None = ""
    LOCALSTACK_URL: str = "http://localhost:4566"
    ENCRYPTION_KEY: str = ""
    GITHUB_API: str = "https://api.github.com"
    GITHUB_API_TOKEN: str = ""

config: Config = Config()