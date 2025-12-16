from pathlib import Path
from typing import Optional

from machine.scripture.verse_ref import Versification
from machine.utils.typeshed import StrPath
from machine.corpora.file_stream_container import FileStreamContainer
from machine.corpora.stream_container import StreamContainer
from machine.corpora.usfm_stylesheet import UsfmStylesheet
from kathairo.parsing.usfm.usfm_text_base import ModifiedUsfmTextBase
from machine.corpora.usfm_parser_handler import UsfmParserHandler


class UsfmFileText(ModifiedUsfmTextBase):
    def __init__(
        self,
        stylesheet: UsfmStylesheet,
        encoding: str,
        filename: StrPath,
        handler: UsfmParserHandler,
        psalmSuperscriptionTag: str, 
        versification: Optional[Versification] = None,
        include_markers: bool = False,
    ) -> None:
        super().__init__(_get_id(filename, encoding), stylesheet, encoding, handler, psalmSuperscriptionTag, versification, include_markers) #passes in handler

        self._filename = Path(filename)

    def _create_stream_container(self) -> StreamContainer:
        return FileStreamContainer(self._filename)


def _get_id(filename: StrPath, encoding: str) -> str:
    with open(filename, "r", encoding=encoding) as file:
        for line in file:
            line = line.strip()
            if line.startswith("\\id "):
                id = line[4:]
                index = id.find(" ")
                if index != -1:
                    id = id[:index]
                return id.strip().upper()
    raise RuntimeError("The USFM does not contain an 'id' marker.")
