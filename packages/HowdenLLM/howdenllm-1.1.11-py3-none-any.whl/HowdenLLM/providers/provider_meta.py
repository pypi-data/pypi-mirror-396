from abc import ABCMeta

class ProviderMeta(ABCMeta):
    """Metaclass that automatically registers all concrete Provider subclasses."""
    _registry = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        provider_name = getattr(cls, "provider", None)
        # Only register real implementations, not the abstract base
        if provider_name and not cls.__abstractmethods__:
            ProviderMeta._registry[provider_name.lower()] = cls

    @classmethod
    def get_registry(mcs):
        return dict(mcs._registry)

