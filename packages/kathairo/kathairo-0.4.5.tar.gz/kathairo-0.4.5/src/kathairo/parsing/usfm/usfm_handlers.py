from typing import Iterable, List, Optional, Sequence

from machine.scripture.verse_ref import VerseRef
from machine.corpora.text_row import TextRow
from machine.corpora.usfm_parser_state import UsfmParserState
from machine.corpora.usfm_token import UsfmToken
from machine.corpora.usfm_token import UsfmTokenType
from machine.corpora.scripture_ref import ScriptureRef
from machine.utils.string_utils import has_sentence_ending

from machine.corpora.usfm_text_base import UsfmTextBase
from machine.corpora.usfm_text_base import _TextRowCollector


class ModifiedTextRowCollector(_TextRowCollector):

    def __init__(self, text: UsfmTextBase, psalm_superscription_tag: str = "d") -> None:
        super().__init__(text)
        self._psalm_superscription_tag = psalm_superscription_tag
        self._in_psalm_superscription = False

    def start_para(
        self,
        state: UsfmParserState,
        marker: str,
        unknown: bool,
        attributes,
    ) -> None:
        is_superscription = (
            marker == self._psalm_superscription_tag
            and state.verse_ref.book == "PSA"
            and state.verse_ref.bbbcccvvvs not in ("019119000", "019107000")
        )

        if is_superscription:
            self._in_psalm_superscription = True

        super().start_para(state, marker, unknown, attributes)

    def end_para(self, state: UsfmParserState, marker: str) -> None:
        super().end_para(state, marker)

        if marker == self._psalm_superscription_tag:
            self._in_psalm_superscription = False

    def _end_non_verse_text(self, state: UsfmParserState, scripture_ref: ScriptureRef) -> None:
        text = self._row_texts_stack.pop() if self._row_texts_stack else ""

        if self._in_psalm_superscription and text.strip():
            self._rows.append(self._text._create_scripture_row(scripture_ref, text, self._sentence_start))
            self._sentence_start = has_sentence_ending(text)
        elif self._text._include_all_text and text:
            self._rows.append(self._text._create_scripture_row(scripture_ref, text, self._sentence_start))
