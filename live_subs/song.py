from collections.abc import Generator, Iterable
from pathlib import Path
from pprint import pprint


class Song:

    def __init__(self, folder: Path) -> None:
        assert folder.is_dir
        translations: list[list[str]] = []
        self.languages: list[str] = []
        self.title: dict[str, str] = {}
        for file in folder.iterdir():
            self.languages.append(file.name)
            with open(file) as f:
                lines = f.readlines()
                self.title[file.name] = lines[0]
                del lines[0]
                translations.append(list("".join(lines).split("<!s>\n")))
        self.position: int = 0
        self.lines: list[dict[str, str]] = list(self.make_lines(translations))

    def make_lines(self,
                   translations: list[list[str]]) -> Iterable[dict[str, str]]:
        for zipped in zip(*translations):
            lines: dict[str, str] = {}
            for lang, line in zip(self.languages, zipped):
                lines[lang] = line
            yield lines

    def __len__(self) -> int | None:
        return len(self.lines)

    def __iter__(self) -> Generator[dict[str, str]]:
        for position in range(len(self.lines)):
            self.position = position
            yield self.lines[position]

    def current_line(self) -> dict[str, str]:
        return self.lines[self.position]

    def previous_line(self) -> dict[str, str] | None:
        if self.position == 0:
            return None
        self.position -= 1
        return self.lines[self.position]

    def next_line(self) -> dict[str, str] | None:
        if self.position == len(self.lines) - 1:
            return None
        self.position += 1
        return self.lines[self.position]


class SongList:

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self._songlist: list[str] = list(
            map(
                lambda dirpath: dirpath.name,
                filter(lambda path: path.is_dir(), self.folder.iterdir())
            )
        )
        self._current_song: int = 0

    def get_list(self) -> Iterable[str]:
        return self._songlist

    def get_song(self, name: str) -> Song | None:
        path = self.folder.joinpath(name)
        if not path.exists():
            return None
        self._current_song = self._songlist.index(name)
        return Song(path)

    def current_song(self) -> Song:
        if (
            song := self.get_song(self._songlist[self._current_song])
        ) is not None:
            return song
        raise IndexError("The Song is missing")

    def next_song(self) -> Song | None:
        if self._current_song >= len(self._songlist) - 1:
            return None
        self._current_song += 1
        return self.current_song()

    def previous_song(self) -> Song | None:
        if self._current_song <= 0:
            return None
        self._current_song -= 1
        return self.current_song()


if __name__ == "__main__":
    song_list = SongList(Path("/home/levitanus/gits/LiveSubs/backend/songs"))
    print(list(song_list.get_list()))
    song = song_list.get_song('02 Stille Nacht')
    print(song.lines)