import pytest

from aiofs.os import OsFileSystem


@pytest.fixture
def client(tmp_path):
    local_dir = tmp_path / "dir"
    template = f"{local_dir}/{{}}/file"

    return OsFileSystem(template)


class A_OsFile:
    async def should_have_template_customizable(self, client):
        client.template = "{}"
        assert client.template == "{}"

    async def should_persist_content(self, client):
        f = client.open("dir/file", "w")
        async with f:
            await f.write(b"content")

        f = client.open("dir/file")
        async with f:
            assert await f.read() == b"content"

    async def should_update_content(self, client):
        f = client.open("dir/file", "w")
        async with f:
            await f.write(b"content")

        f = client.open("dir/file", "r+")
        async with f:
            content = await f.read()
            await f.write(content + b"-with-append")

        f = client.open("dir/file")
        async with f:
            assert await f.read() == b"content-with-append"

    async def should_raise_file_not_found(self, client):
        f = client.open("dir/file")
        with pytest.raises(FileNotFoundError):
            async with f:
                await f.read()

    async def should_run_within_context(self, client):
        f = client.open("dir/file")
        with pytest.raises(RuntimeError):
            await f.read()

        with pytest.raises(RuntimeError):
            await f.write(b"")

    async def should_remove_file(self, client):
        async with client.open("dir/file", "w") as f:
            await f.write(b"content")

        await client.rm("dir/file")

        with pytest.raises(FileNotFoundError):
            async with client.open("dir/file") as f:
                await f.read()

    async def should_list_files(self, client):
        async with client.open("one/file", "w") as f:
            await f.write(b"content")

        async with client.open("other_one", "w") as f:
            await f.write(b"content")

        async with client.open("the third", "w") as f:
            await f.write(b"content")

        assert set(await client.ls()) == set(["one/file", "other_one", "the third"])
        assert set(await client.ls("*ne*")) == set(["one/file", "other_one"])
