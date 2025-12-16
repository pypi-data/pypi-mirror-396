__all__ = [
    "version",
    "__version__",
]

try:
    from ._version import version, __version__
except ModuleNotFoundError:
    try:
        import importlib.metadata

        version = __version__ = importlib.metadata.version("pyds")
    except importlib.metadata.PackageNotFoundError:
        version = __version__ = "0.0.0"
