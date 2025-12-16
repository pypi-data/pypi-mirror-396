import importlib.metadata

__version__ = importlib.metadata.version("varanus")
__version_info__ = tuple(
    int(num) if num.isdigit() else num for num in __version__.split(".")
)
