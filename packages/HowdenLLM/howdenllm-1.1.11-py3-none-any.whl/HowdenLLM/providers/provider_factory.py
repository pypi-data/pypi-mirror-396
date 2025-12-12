import importlib
import inspect
import pkgutil
from pathlib import Path
from .provider_meta import ProviderMeta


class ProviderFactory:
    """Factory that dynamically loads provider modules and instantiates them."""

    @staticmethod
    def _load_all_providers():
        """Import every provider module dynamically within this package."""
        # Get current file and package info dynamically
        current_file = Path(inspect.getfile(ProviderFactory))
        current_dir = current_file.parent
        package_root = ProviderFactory.__module__.rsplit(".", 1)[0]

        for _, module_name, _ in pkgutil.iter_modules([str(current_dir)]):
            full_module_name = f"{package_root}.{module_name}"
            importlib.import_module(full_module_name)

    @staticmethod
    def create(provider_name: str):
        """Instantiate a provider by name using the registry."""
        ProviderFactory._load_all_providers()

        providers = ProviderMeta.get_registry()
        key = provider_name.lower()

        if key not in providers:
            raise ValueError(
                f"No provider found for '{provider_name}'. "
                f"Available: {list(providers.keys())}"
            )

        return providers[key]()
