from pathlib import Path


class Dataset:
    __slots__ = [
        "_path_data",
    ]
    _path_data: Path
    _supported_extensions : tuple[str, ...] = ("hdf5", "npz", "root", "tsv")


    def __init__(self, source_type: str = "hdf5"):
        # TODO: add log info
        if source_type not in self._supported_extensions:
            raise ValueError(f"Unsupported source type: {source_type}")

        package_path = Path(__file__).parent
        self._path_data = package_path / "data" / source_type

    @property
    def path_data(self) -> Path:
        return self._path_data

def get_path_data(source_type: str = "hdf5") -> Path:
    return Dataset(source_type=source_type).path_data
