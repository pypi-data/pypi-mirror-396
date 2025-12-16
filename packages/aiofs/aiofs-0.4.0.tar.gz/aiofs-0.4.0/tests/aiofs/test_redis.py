import os
import pytest

from aiofs.redis import RedisFileSystem, RedisConfig

FILENAME = "filename"


@pytest.fixture
async def client(request, redis_config):
    pattern = request.params if hasattr(request, "param") else "*"
    fs = RedisFileSystem(redis_config, pattern)
    yield fs
    await fs.rm(FILENAME)
    await fs.close()


# Parametrize the class
class A_RedisFileLike:

    async def should_persist_content(self, client):
        f = client.open(FILENAME, "w")
        async with f:
            await f.write(b"content")

        f = client.open(FILENAME)
        async with f:
            assert await f.read() == b"content"

    async def should_update_content(self, client):
        f = client.open(FILENAME, "w")
        async with f:
            await f.write(b"content")

        f = client.open(FILENAME, "r+")
        async with f:
            content = await f.read()
            await f.write(content + b"-with-append")

        f = client.open(FILENAME)
        async with f:
            assert await f.read() == b"content-with-append"

    async def should_raise_file_not_found(self, client):
        f = client.open(FILENAME)
        with pytest.raises(FileNotFoundError):
            async with f:
                await f.read()

    async def should_run_within_context(self, client):
        f = client.open(FILENAME)
        with pytest.raises(RuntimeError):
            await f.read()

        with pytest.raises(RuntimeError):
            await f.write(b"")

    async def should_list_files(self, client):
        async with client.open("one/file", "w") as f:
            await f.write(b"content")

        async with client.open("other_one", "w") as f:
            await f.write(b"content")

        async with client.open("the third", "w") as f:
            await f.write(b"content")

        assert set(await client.ls()) == set(["one/file", "other_one", "the third"])
        assert set(await client.ls("*ne*")) == set(["one/file", "other_one"])
