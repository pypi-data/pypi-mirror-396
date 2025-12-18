import os
import struct
import zlib

import msgpack

from cvsx2mvsx.models.mvstory.model import StoryContainer


class MVStoryLoader:
    def __init__(
        self,
        story_container: StoryContainer,
        out_file_path: str,
        compression_level: int,
    ) -> None:
        self._story_container = story_container
        self._out_file_path = out_file_path
        self._compression_level = compression_level

    def run(self) -> None:
        dirpath = os.path.dirname(self._out_file_path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        compressor = zlib.compressobj(level=6, wbits=15)
        packer = msgpack.Packer(use_bin_type=True)

        with open(self._out_file_path, "wb") as f:

            def write(chunk):
                """Helper to compress and write immediately."""
                if chunk:
                    f.write(compressor.compress(chunk))

            write(packer.pack_map_header(2))

            write(packer.pack("version"))
            write(packer.pack(self._story_container.version))

            write(packer.pack("story"))
            story = self._story_container.story
            write(packer.pack_map_header(4))

            write(packer.pack("metadata"))
            write(packer.pack(story.metadata.model_dump()))

            write(packer.pack("javascript"))
            write(packer.pack(story.javascript))

            write(packer.pack("scenes"))
            write(packer.pack_array_header(len(story.scenes)))
            for scene in story.scenes:
                write(packer.pack(scene.model_dump()))

            write(packer.pack("assets"))
            write(packer.pack_array_header(len(story.assets)))

            for asset in story.assets:
                write(packer.pack_map_header(2))

                write(packer.pack("name"))
                write(packer.pack(asset.name))

                write(packer.pack("content"))

                if asset.file_path and asset.content is None:
                    file_size = os.path.getsize(asset.file_path)

                    if file_size < 256:
                        # bin 8: 0xc4 + 1 byte length
                        write(b"\xc4" + struct.pack(">B", file_size))
                    elif file_size < 65536:
                        # bin 16: 0xc5 + 2 byte length
                        write(b"\xc5" + struct.pack(">H", file_size))
                    else:
                        # bin 32: 0xc6 + 4 byte length
                        write(b"\xc6" + struct.pack(">I", file_size))

                    with open(asset.file_path, "rb") as af:
                        while True:
                            chunk = af.read(1024 * 1024)
                            if not chunk:
                                break
                            write(chunk)
                else:
                    data = asset.content or b""
                    write(packer.pack(data))

            f.write(compressor.flush())
