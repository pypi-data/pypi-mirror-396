from io import UnsupportedOperation
from typing import Self

from . import FileLike, FileLikeSystem
from fnmatch import fnmatch


class InMemFile(FileLike):
    def __init__(self, name: str, mode: str, content: bytes | None = None):
        self._name = name
        self._mode = mode
        self._content = content

        self._context = None

    async def __aenter__(self) -> Self:
        self._context = self._name
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._context = None

    async def read(self, size: int = -1) -> bytes:
        if "r" not in self._mode:
            raise UnsupportedOperation(f"File {self._name} not readable")

        if self._content is None:
            raise FileNotFoundError(f"No such file or directory: '{self._name}'")

        return self._content

    async def write(self, b: bytes):
        if "+" not in self._mode and "w" not in self._mode:
            raise UnsupportedOperation(f"File {self._name} not writable")

        self._content = b


class InMemFileSystem(FileLikeSystem):
    def __init__(self):
        self._files = {}

    @property
    def template(self) -> str:
        """Template to generate the full filename"""
        return "{}"

    @template.setter
    def template(self, value: str):
        """Change template for locating the files"""
        ...

    def open(self, filename: str, mode: str = "r") -> InMemFile:
        content = None
        if filename in self._files:
            content = self._files[filename]._content

        self._files[filename] = InMemFile(filename, mode, content)
        return self._files[filename]

    async def rm(self, pattern: str):
        fns = await self.ls(pattern)
        for fn in fns:
            self._files.pop(fn)

    async def ls(self, pattern: str = "*"):
        return [
            value
            for value in self._files.keys()
            if pattern == "*" or fnmatch(value, pattern)
        ]
