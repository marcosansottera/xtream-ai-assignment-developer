from __future__ import annotations as ann

from pathlib import Path

from loguru import logger


class DiamondsDataDir:
    _default_base_path = None

    class _DirectoryManager:
        def __init__(self, base_path: Path, relative_path: str):
            self._base_path = base_path
            self._path = base_path / relative_path

        @property
        def path(self) -> Path:
            if not self._path.exists():
                raise FileNotFoundError(f"Directory not found: {self._path}")
            return self._path

        def mkdir(self, exist_ok: bool=True, parents: bool=True) -> None:
            self._path.mkdir(exist_ok=exist_ok, parents=parents)

        def __getattr__(self, directory_name: str) -> DiamondsDataDir._DirectoryManager:
            new_relative_path: Path = Path(
                *list((self.path.relative_to(self._base_path) / directory_name).parts)
            )
            if not (self._base_path / new_relative_path).exists():
                logger.warning(f"Directory not found: {self._base_path / new_relative_path}")
            return DiamondsDataDir._DirectoryManager(self._base_path, new_relative_path)

    def __init__(self, relative_path: str = ""):
        base_path = self.get_default_base_path()
        self._directory = self._DirectoryManager(base_path, relative_path)
        self._directory.mkdir()

    @classmethod
    def set_default_base_path(cls, new_base_path: Path) -> None:
        cls._default_base_path = new_base_path

    @classmethod
    def get_default_base_path(cls) -> Path:
        if cls._default_base_path is None:
            cls._default_base_path = Path(__file__).parent / "data"
        return cls._default_base_path

    @property
    def path(self) -> Path:
        return self._directory.path

    def mkdir(self, exist_ok: bool=True, parents: bool=True) -> None:
        self._directory.mkdir(exist_ok=exist_ok, parents=parents)

    def __getattr__(self, directory_name: str) -> DiamondsDataDir._DirectoryManager:
        return getattr(self._directory, directory_name)
