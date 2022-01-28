from pathlib import Path
import state
from enum import Enum
import aiofiles

class FileType(str, Enum):
    MAPSET = ("{digest}.zip", "zip")
    PREVIEW = ("preview.mp3", "mp3")
    COVER = ("cover.jpg", "jpg")

    def __init__(self, name: str, ext: str):
        self.name = name
        self.ext = ext

    def from_ext(self, ext: str) -> "FileType":
        return {
            "zip": FileType.MAPSET,
            "mp3": FileType.PREVIEW,
            "jpg": FileType.COVER,
        }[ext]

    def formatted(self, version) -> str:
        if self == FileType.COVER:
            return self.MAPSET.name.format(digest=version)
        else:
            return self.MAPSET.name

class File:
    typ: FileType
    mid: str
    version: str

    _fs: "Filesystem"

    @property
    def path(self) -> Path:
        return self._fs._construct_path(
            mid=self.mid,
            digest=self.version,
            ft=self.typ,
        ) / self.typ.format(digest=self.version)


    @property
    def exists(self):
        return self.path.exists

class Filesystem:
    def __init__(self, entry: str = state.config.BEATMAP_PATH) -> None:
        self.entry = Path(entry)
        assert self.entry.is_dir()

    # https://cdn.ryuunosuke.moe/beatmaps/{id}/{hash}/(preview.mp3 || {hash}.zip || cover.jpg))
    def _construct_path(self, mid: str, digest: str) -> Path:
        return self.entry / "beatmaps" / mid / digest

    async def save(self, mid: str, version: str, ft: "FileType", data: bytes):
        path = self._construct_path(mid, version, ft) / ft.formatted(version)
        async with aiofiles.open(str(path)) as f:
            await f.write(data)

    