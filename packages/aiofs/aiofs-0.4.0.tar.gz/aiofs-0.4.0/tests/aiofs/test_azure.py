import os
import pytest

from aiofs.azure import AzFileSystem, AzureContainerConfig


HOSTNAME = os.getenv("AZURE_HOSTNAME", "127.0.0.1")
FILENAME = "filename"


@pytest.fixture
async def fs(azure_config):
    fs = AzFileSystem(azure_config, "prefix/*/posfix")
    yield fs
    await fs.rm("*")
    await fs.close()


# Parametrize the class
class An_AzFileLike:
    async def should_have_template_customizable(self, fs):

        fs.template = "{}"
        assert fs.template == "{}"

    async def should_persist_content(self, fs):
        f = fs.open(FILENAME, "w")
        async with f:
            await f.write(b"content")

        f = fs.open(FILENAME)
        async with f:
            assert await f.read() == b"content"

    async def should_update_content(self, fs):
        f = fs.open(FILENAME, "w")
        async with f:
            await f.write(b"content")

        f = fs.open(FILENAME, "r+")
        async with f:
            content = await f.read()
            await f.write(content + b"-with-append")

        f = fs.open(FILENAME)
        async with f:
            assert await f.read() == b"content-with-append"

    async def should_raise_file_not_found(self, fs):
        f = fs.open(FILENAME)
        with pytest.raises(FileNotFoundError):
            async with f:
                await f.read()

    async def should_run_within_context(self, fs):
        f = fs.open(FILENAME)
        with pytest.raises(RuntimeError):
            await f.read()

        with pytest.raises(RuntimeError):
            await f.write(b"")

    async def should_list_files(self, fs):
        async with fs.open("one/file", "w") as f:
            await f.write(b"content")

        async with fs.open("other_one", "w") as f:
            await f.write(b"content")

        async with fs.open("the third", "w") as f:
            await f.write(b"content")

        assert set(await fs.ls()) == set(["one/file", "other_one", "the third"])
        assert set(await fs.ls("*ne*")) == set(["one/file", "other_one"])

    async def should_list_files_without_suffix(self, fs):
        fs.template = "{}"
        async with fs.open("one/file", "w") as f:
            await f.write(b"content")

        async with fs.open("other_one", "w") as f:
            await f.write(b"content")

        async with fs.open("the third", "w") as f:
            await f.write(b"content")

        assert set(await fs.ls()) == set(["one/file", "other_one", "the third"])
        assert set(await fs.ls("*ne*")) == set(["one/file", "other_one"])
