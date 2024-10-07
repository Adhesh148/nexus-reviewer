
from pydantic import BaseModel, Field, HttpUrl
from typing import Union, Optional, Dict
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
import json
from pynamodb.attributes import UnicodeAttribute
from cryptography.fernet import Fernet

from config.config import config
from config.config import EnvironmentType

# Base configuration model
class BaseConfig(BaseModel):
    platform: str  # Should be one of 'github', 'jira', or 'confluence'

# Specific configuration models extending BaseConfig
class GithubConfig(BaseConfig):
    platform: str = 'github'
    token: str
    repoName: str

class ConfluenceConfig(BaseConfig):
    platform: str = 'confluence'
    username: str
    url: HttpUrl
    token: str

class JiraConfig(BaseConfig):
    platform: str = 'jira'
    username: str
    url: HttpUrl
    token: str
    projectKey: str

class EncryptedUnicodeAttribute(UnicodeAttribute):
    def __init__(self, encryption_key, *args, **kwargs):
        self.cipher = Fernet(encryption_key)
        super().__init__(*args, **kwargs)

    def serialize(self, value):
        encrypted_value = self.cipher.encrypt(value.encode())
        return super().serialize(encrypted_value.decode())

    def deserialize(self, value):
        decrypted_value = self.cipher.decrypt(value.encode())
        return super().deserialize(decrypted_value.decode())

class ProjectPynamoDBModel(Model):
    class Meta:
        table_name = 'projects'
        region = 'us-east-1'
        if config.ENVIRONMENT == EnvironmentType.SANDBOX:
            host = config.LOCALSTACK_URL

    project_id = UnicodeAttribute(hash_key=True)
    project_name = UnicodeAttribute()
    project_desc = UnicodeAttribute(null=True)
    _encrypted_configs = EncryptedUnicodeAttribute(encryption_key=config.ENCRYPTION_KEY)

    @property
    def configs(self) -> Dict[str, Dict[str, Union[str, int]]]:
        encrypted_data = self._encrypted_configs
        if encrypted_data:
            json_data = json.loads(encrypted_data)
            # Convert the list of configurations to a dictionary of configurations
            configs = {}
            for config_data in json_data:
                platform = config_data.get("platform")
                if platform:
                    configs[platform] = self._deserialize_config(config_data)
            return configs
        return {}

    @configs.setter
    def configs(self, value: Dict[str, Dict[str, Union[str, int]]]):
        # Convert the dictionary of configurations to a list of dictionaries
        config_list = []
        for platform, config in value.items():
            config_list.append(config)
        # Serialize configuration dictionaries to JSON
        json_data = json.dumps(config_list)
        self._encrypted_configs = json_data

    def _deserialize_config(self, data: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        platform = data.get("platform")
        if platform == 'github':
            return GithubConfig(**data).dict()
        elif platform == 'confluence':
            return ConfluenceConfig(**data).dict()
        elif platform == 'jira':
            return JiraConfig(**data).dict()
        else:
            raise ValueError(f"Unknown platform: {platform}")