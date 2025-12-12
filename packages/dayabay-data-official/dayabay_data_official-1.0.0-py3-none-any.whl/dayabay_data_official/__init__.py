from importlib.metadata import version

__version__ = version(__name__)

from .dataset import Dataset, get_path_data

__all__ = [
    "Dataset",
    "get_path_data",
    "__version__",
]
