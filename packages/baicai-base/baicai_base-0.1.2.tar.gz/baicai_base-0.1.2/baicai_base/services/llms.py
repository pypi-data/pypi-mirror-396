import os

from dotenv import load_dotenv

# Import ConfigManager only
from baicai_base.configs import ConfigManager, LLMConfig

# Define env_path using the static method from ConfigManager
env_path = ConfigManager.get_env_path()
# Ensure the .env file exists before trying to load it
env_path.touch(exist_ok=True)
load_dotenv(dotenv_path=env_path, override=True)  # Use override to reload if needed


# Helper function to check/prompt for API key
def ensure_api_key(provider: str):
    key_name = ""
    if provider == "groq":
        key_name = "GROQ_API_KEY"
    elif provider == "openai兼容":
        key_name = "OPENAI_API_KEY"
    # Add other providers as needed
    else:
        return  # No known key for this provider

    if not os.getenv(key_name):
        print(f"{key_name} not found in environment variables.")
        key_value = input(f"Please enter your {key_name}: ")
        if key_value:
            # Use ConfigManager to save the key
            config_manager = ConfigManager()  # Initialize manager to use its methods
            config_manager.save_key(key_name, key_value)  # Use the renamed method
            # Reload environment variables after saving
            load_dotenv(dotenv_path=ConfigManager.get_env_path(), override=True)  # Use static method for path
            # Verify it's loaded
            if not os.getenv(key_name):
                print(f"Warning: Failed to load {key_name} after saving. LLM might not work.")
        else:
            print(f"Warning: No {key_name} provided. LLM initialization might fail.")


class LLM:
    """
    Wrapper around the LangChain LLMs.

    Args:
    config_id: ID of the configuration to use. If not specified, uses the global config.
               If no global config exists, falls back to default config.
    """

    def __init__(
        self,
        config_id: str = None,  # Allow specifying a config ID
    ):
        # Load the specified config, global config, or default config
        self.config = LLMConfig.load(config_id) if config_id else LLMConfig.load()

        # Initialize the LLM client - assumes API key is already set if needed
        if self.config.provider == "groq":
            from langchain_groq import ChatGroq

            self.llm = ChatGroq(temperature=self.config.temperature, model_name=self.config.model_name)
        elif self.config.provider == "openai兼容":
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                temperature=self.config.temperature, model_name=self.config.model_name, base_url=self.config.base_url
            )
        else:
            raise ValueError(f"Invalid provider: {self.config.provider}")


if __name__ == "__main__":
    # Example: Initialize LLM with default config
    # 1. Load the config first to know the provider
    config = LLMConfig.load()  # This will use global if available, otherwise default

    # 2. Ensure API key is present *before* initializing LLM (for script/console use)
    ensure_api_key(config.provider)

    # 3. Now initialize the LLM wrapper
    llm_wrapper = LLM()  # Will use global config if available, otherwise default
    llm = llm_wrapper.llm
    try:
        print(llm.invoke("Hello, world!"))
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        print("Please ensure your API key and configuration are correct.")
