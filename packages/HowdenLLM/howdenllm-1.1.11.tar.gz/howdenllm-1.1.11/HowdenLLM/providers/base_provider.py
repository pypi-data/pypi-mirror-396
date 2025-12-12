from abc import ABC, abstractmethod
from .provider_meta import ProviderMeta

class BaseProvider(ABC, metaclass=ProviderMeta):
    @abstractmethod
    def complete(self,  system: str, prompt: str, model: str, use_web_search_tool: bool) -> str:
        pass