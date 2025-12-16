import pytest
import asyncio
from evsrc.infra.inmem import InMemFileSystem


@pytest.fixture
def fs():
    return InMemFileSystem()


class A_InMemFileSystem:
    async def given_a_file(self, filename: str, content: bytes, fs):
        async with fs.open(filename, "w") as f:
            await f.write(content)

    async def should_create_files(self, fs):
        async with fs.open("test/file", "w") as f:
            assert not await f.read()
            await f.write(b"content")

        async with fs.open("test/file", "r") as f:
            assert await f.read() == b"content"

    async def should_append_content_to_file(self, fs):
        await self.given_a_file("test/file", b"content", fs)

        async with fs.open("test/file", "a") as f:
            await f.write(b"-more")
            assert await f.read() == b"content-more"

    async def should_raise_file_not_found(self, fs):
        with pytest.raises(FileNotFoundError):
            async with fs.open("no/exist", "r") as f:
                await f.read()

    async def should_list_files(self, fs):
        await self.given_a_file("test/a_file", b"content", fs)
        await self.given_a_file("test/other_file", b"content", fs)

        assert await fs.ls() == ["test/a_file", "test/other_file"]

    async def should_remove_files(self, fs):
        await self.given_a_file("test/a_file", b"content", fs)

        await fs.rm("*")

        assert not await fs.ls()

    async def should_block_concurrence_editions(self, fs):
        async def write_with_delay():
            async with fs.open("test/file", "w") as f:
                await f.write(b"delayed")
                await asyncio.sleep(0.15)

        async def write_without_delay():
            await asyncio.sleep(0.05)
            async with fs.open("test/file", "w") as f:
                await f.write(b"last")

        asyncio.create_task(write_with_delay())
        asyncio.create_task(write_without_delay())

        await asyncio.sleep(0.1)
        async with fs.open("test/file", "w") as f:
            assert await f.read() == b"last"
