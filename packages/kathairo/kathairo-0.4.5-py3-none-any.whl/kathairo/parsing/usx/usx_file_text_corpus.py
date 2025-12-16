from pathlib import Path
from typing import List, Optional

from machine.scripture.verse_ref import Versification
from machine.utils.typeshed import StrPath
from machine.corpora.corpora_utils import get_usx_versification
from machine.corpora.scripture_text_corpus import ScriptureTextCorpus
from kathairo.parsing.usx.usx_file_text import UsxFileText #use Modified UsxFileText


class UsxFileTextCorpus(ScriptureTextCorpus):
    def __init__(
        self,
        project_dir: StrPath,
        versification: Optional[Versification] = None,
    ) -> None:
        project_dir = Path(project_dir)
        versification = get_usx_versification(project_dir, versification)
        texts: List[UsxFileText] = []
        for filename in project_dir.glob("*.usx"):
            texts.append(UsxFileText(filename, versification))
        super().__init__(versification, texts)
