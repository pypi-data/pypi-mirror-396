from pathlib import Path
from typing import Optional

from machine.scripture.verse_ref import Versification
from machine.utils.typeshed import StrPath
from machine.corpora.corpora_utils import get_usx_id
from machine.corpora.file_stream_container import FileStreamContainer
from machine.corpora.stream_container import StreamContainer
from kathairo.parsing.usx.usx_text_base import UsxTextBase #use modified UsxTextBase


class UsxFileText(UsxTextBase):
    def __init__(self, filename: StrPath, versification: Optional[Versification] = None) -> None:
        self._filename = Path(filename)
        super().__init__(get_usx_id(self._filename), versification)

    def _create_stream_container(self) -> StreamContainer:
        return FileStreamContainer(self._filename)
