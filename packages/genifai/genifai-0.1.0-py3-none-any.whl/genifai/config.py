import os
from pathlib import Path
from typing import Optional
import yaml
import sys


class Config:
    """Configuration manager"""
    
    # CONFIG_DIR = Path.home() / ".genifai"
    # CONFIG_FILE = CONFIG_DIR / "config.yaml"

    def __init__(self):
        self.genifai_api_key: Optional[str] = None
        self.claude_api_key: Optional[str] = None 
        self.azure_endpoint: Optional[str] = None 
        self.api_type: Optional[str] = None 
        self.default_language: Optional[str] = None
        self.default_framework: Optional[str] = None
        self._load()
    
    def _load(self):
        """Load configuration from file and environment"""
        self.api_type = os.environ.get("GENIFAI_API_TYPE") 
        self.genifai_api_key = os.environ.get("GENIFAI_API_KEY") 
        self.claude_api_key = os.environ.get("CLAUDE_API_KEY")  
        self.azure_endpoint = os.environ.get("AZURE_ENDPOINT")  
        
        # print(f"DEBUG Config._load():", file=sys.stderr)
        # print(f"  api_type = {repr(self.api_type)}", file=sys.stderr)
        # print(f"  genifai_api_key = {repr(self.genifai_api_key)}", file=sys.stderr)
        # print(f"  claude_api_key = {repr(self.claude_api_key)}", file=sys.stderr)
        # print(f"  azure_endpoint = {repr(self.azure_endpoint)}", file=sys.stderr)
        
        
    # def save(self):
    #     """Save configuration to file"""
    #     self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    #     config_data = {
    #         "genifai_api_key": self.genifai_api_key, 
    #         "claude_api_key": self.claude_api_key, 
    #         "azure_endpoint": self.azure_endpoint, 
    #         "api_type": self.api_type,  
    #     }
        
    #     if self.default_language:
    #         config_data["default_language"] = self.default_language
    #     if self.default_framework:
    #         config_data["default_framework"] = self.default_framework
        
    #     with open(self.CONFIG_FILE, 'w') as f:
    #         yaml.dump(config_data, f, default_flow_style=False)
    
    
    def is_claude_configured(self) -> bool:
        """Check if API key is configured"""
        #return self.genifai_api_key is not None
        return self.claude_api_key is not None

    def is_genifai_configured(self) -> bool:
        """Check if API key is configured"""
        return self.genifai_api_key is not None

    
    def get_language(self, cli_option: Optional[str] = None) -> str:
        """
        Get language with priority: CLI option > ENV > Config file
        
        Args:
            cli_option: Language specified via --language option
            
        Returns:
            Language code (e.g., 'python', 'javascript')
            
        Raises:
            ValueError: If language is not specified anywhere
        """

        # 1. CLI option (highest priority)
        if cli_option:
            return cli_option
        
        # 2. Environment variable
        env_lang = os.environ.get("GENIFAI_LANGUAGE")
        if env_lang:
            return env_lang
        
        # 3. Config file
        if self.default_language:
            return self.default_language
        
        # 4. Error
        raise ValueError(
            "Language not specified. Use one of:\n"
            "  1. --language option: genifai generate --language python\n"
            "  2. Environment variable: export GENIFAI_LANGUAGE=python\n"
            # "  3. Config file: genifai configure --default-language python"
        )

    
    def get_framework(self, cli_option: Optional[str] = None, language: Optional[str] = None) -> Optional[str]:
        """
        Get framework with priority: CLI option > ENV > Config file > Language default
        
        Args:
            cli_option: Framework specified via --framework option
            language: Language to get default framework for
            
        Returns:
            Framework name or None
        """
        # 1. CLI option
        if cli_option:
            return cli_option
        
        # 2. Environment variable
        env_framework = os.environ.get("GENIFAI_FRAMEWORK")
        if env_framework:
            return env_framework
        
        # 3. Config file
        if self.default_framework:
            return self.default_framework
        
        # 4. Language default (handled in cli.py)
        return None


BASE_URL = "https://api.genifai.dev/v1"
# BASE_URL = "http://127.0.0.1:8000/v1"

# Language configurations
LANGUAGE_CONFIGS = {
    'c': {'display_name': 'C', 'default_framework': 'cunit'},
}