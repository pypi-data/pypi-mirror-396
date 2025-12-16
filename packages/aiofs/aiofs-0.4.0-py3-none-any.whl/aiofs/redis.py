import logging
from dataclasses import dataclass
from typing import Any

from redis import WatchError
from redis.asyncio import ConnectionPool, Redis

from . import FileLike, FileLikeSystem

logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    host: str | None = None
    port: int | None = None
    protocol: str = "redis"
    username: str | None = None
    password: str | None = None
    vhost: str | None = None
    query: str = ""

    def uri(self):
        value = f"{self.protocol}://"
        if self.username:
            value += self.username
        if self.password:
            value += f":{self.password}"

        if value[-2:] != "//":
            value += "@"

        if self.host:
            value += self.host

        if self.port:
            value += f":{self.port}"

        if self.vhost:
            value += f"/{self.vhost}"

        if self.query:
            value += f"?{self.query}"
        return value


class RedisFileLike(FileLike):
    """Implementation of FileLike using Redis Database"""

    def __init__(
        self, pool: ConnectionPool, path: str, mode="r", expiry: None | int = None
    ):
        self._key = path.replace("/", ":")
        self._pool = pool
        self._mode = mode

        self._context = None
        self._conn = None
        self._content = b""
        self._expiry = expiry

        self._pipe_ctx = None
        self._pipe = None

    async def __aenter__(self):
        await self._open()
        return self

    async def _open(self):
        self._context = Redis(connection_pool=self._pool)
        self._conn = await self._context.__aenter__()
        if "w" in self._mode or "r+" in self._mode:
            self._pipe_ctx = self._conn.pipeline(transaction=True)
            self._pipe = await self._pipe_ctx.__aenter__()
            await self._pipe.watch(self._key)

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if self._pipe and self._pipe_ctx:
                self._pipe.multi()
                if self._content:
                    await self._pipe.set(self._key, self._content, self._expiry)
                await self._pipe.execute()
                await self._pipe_ctx.__aexit__(exc_type, exc, tb)
                self._pipe = None
                self._pipe_ctx = None
                self._content = b""
        except WatchError:
            fn = self._key.replace(":", "/")
            raise BlockingIOError(f"File '{fn}' is open by other process")
        finally:
            if self._context:
                await self._context.__aexit__(exc_type, exc, tb)
            self._context = None

    async def read(self, size: int = -1) -> bytes:
        """Read bytes from the register"""
        if self._conn is None:
            raise RuntimeError('Method "read" called out of context')

        if size < 0:
            content = await self._conn.get(self._key)
            print(content)
            if content is None:
                raise FileNotFoundError(f"Not found {self._key} at Redis")
            return content

        return b""

    async def write(self, b: bytes):
        """Write content to redis register"""
        if self._conn is None:
            raise RuntimeError('Method "write" called out of context')

        self._content += b


class RedisFileSystem(FileLikeSystem):
    """Implement a file system to get access to FileLike objects"""

    def __init__(
        self, cfg: RedisConfig, file_pattern: str = "*", expiry_s: int | None = None
    ):
        self._pool = ConnectionPool.from_url(
            cfg.uri(),
            health_check_interval=10,
            socket_timeout=10,
            socket_keepalive=True,
            socket_connect_timeout=10,
            retry_on_timeout=True,
        )
        self._pattern = file_pattern
        self._expiry = expiry_s

    def open(self, filename: str, mode: str = "r") -> RedisFileLike:
        """Return FileLike object"""
        return RedisFileLike(
            self._pool, self._pattern.replace("*", filename), mode, self._expiry
        )

    async def rm(self, pattern: str):
        fns = await self.ls(pattern)
        async with Redis(connection_pool=self._pool) as conn:
            for fn in fns:
                await conn.delete(self._pattern.replace("*", fn).replace("/", ":"))

    async def ls(self, pattern: str = "*"):
        """List all filenames following a file pattern"""
        prefix, _, sufix = self._pattern.replace("/", ":").partition("*")
        pattern = self._pattern.replace("*", pattern).replace("/", ":")
        keys = []
        async with Redis(connection_pool=self._pool) as conn:
            cursor = 0
            while True:
                # Use the SCAN command to find keys matching the pattern
                cursor, batch = await conn.scan(cursor, match=pattern, count=100)

                keys.extend(
                    [name[len(prefix) : -len(sufix) or None].decode() for name in batch]
                )
                if cursor == 0:  # Cursor 0 means the scan is complete
                    break
        return [key.replace(":", "/") for key in keys]

    async def cp(self, origin_path: str, destination_path: str):
        """Copy a filename in origin_path to destination_path"""
        return await super().cp(origin_path, destination_path)

    async def mv(self, origin_path: str, destination_path: str):
        """Move or rename the"""
        await self.cp(origin_path, destination_path)
        await self.rm(origin_path)

    async def close(self):
        await self._pool.disconnect()
