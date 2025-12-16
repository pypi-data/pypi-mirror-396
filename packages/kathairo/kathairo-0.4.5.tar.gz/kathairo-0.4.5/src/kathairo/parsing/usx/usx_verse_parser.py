from __future__ import annotations

import xml.etree.ElementTree as etree
from typing import Iterable

from machine.scripture.verse_ref import are_overlapping_verse_ranges
from machine.corpora.corpora_utils import merge_verse_ranges
from machine.corpora.usx_verse import UsxVerse
from machine.corpora.usx_verse_parser import UsxVerseParser
from machine.corpora.usx_verse_parser import _ParseContext


def _is_numbered_style(base_style: str, style: str) -> bool:
    """
    Check if a style is a numbered variant of a base style.
    For example, 's1', 's2' are numbered variants of 's'.
    """
    if not style.startswith(base_style):
        return False
    suffix = style[len(base_style):]
    return suffix.isdigit() if suffix else False


class ModifiedUsxVerseParser(UsxVerseParser):
    def __init__(self, merge_segments: bool = False) -> None:
        self._merge_segments = merge_segments
    
    def _parse_element(self, elem: etree.Element, ctxt: _ParseContext) -> Iterable[UsxVerse]:
        if elem.text is not None and ctxt.chapter is not None and ctxt.verse is not None:
            ctxt.add_token(elem.text)
        for e in elem:
            if e.tag == "chapter":
                if ctxt.chapter is not None and ctxt.verse is not None:
                    yield ctxt.create_verse()
                ctxt.chapter = e.get("number")
                ctxt.verse = None
                ctxt.is_sentence_start = True
            elif e.tag == "para":
                if not _is_verse_para(e):
                    ctxt.is_sentence_start = True
                    continue
                
                if(e.get("style", "") == "d" and (ctxt.verse != None and ctxt.verse != "0")):
                    continue
                
                # include superscriptions in text (TODO, limit to just the Psalms)
                if (e.get("style", "") == "d" and ctxt.chapter != '119'):#or e.get("style", "") == "s"
                    verse = "0"
                    ctxt.verse = verse
                ###
                        
                ctxt.para_element = e
                for evt in self._parse_element(e, ctxt):
                    yield evt
            elif e.tag == "verse":
                if "eid" in e.attrib:
                    yield ctxt.create_verse()
                    ctxt.verse = None
                else:
                    verse = e.get("number")
                    if verse is None:
                        verse = e.get("pubnumber")
                    assert verse is not None
                    if ctxt.chapter is not None and ctxt.verse is not None:
                        if verse == ctxt.verse:
                            yield ctxt.create_verse()

                            # ignore duplicate verse
                            ctxt.verse = None
                        elif are_overlapping_verse_ranges(verse, ctxt.verse):
                            # merge overlapping verse ranges in to one range
                            ctxt.verse = merge_verse_ranges(verse, ctxt.verse)
                        else:
                            yield ctxt.create_verse()
                            ctxt.verse = verse
                    else:
                        ctxt.verse = verse
            elif e.tag == "char":
                if e.get("style") == "rq":
                    if ctxt.chapter is not None and ctxt.verse is not None:
                        ctxt.add_token("", e)
                else:
                    for evt in self._parse_element(e, ctxt):
                        yield evt
            elif e.tag == "wg":
                if e.text is not None and ctxt.chapter is not None and ctxt.verse is not None:
                    ctxt.add_token(e.text, e)
            elif e.tag == "figure":
                if ctxt.chapter is not None and ctxt.verse is not None:
                    ctxt.add_token("", e)

            if e.tail is not None and ctxt.chapter is not None and ctxt.verse is not None:
                ctxt.add_token(e.tail)


_NONVERSE_PARA_STYLES = {"ms", "mr", "sr", "r", "sp", "rem", "restore", "cl", "s"} # removed "d" and "s" to include superscriptions

def _is_verse_para(para_elem: etree.Element) -> bool:
    style = para_elem.get("style", "")
    if style in _NONVERSE_PARA_STYLES:
        return False

    if _is_numbered_style("ms", style):
        return False

    if _is_numbered_style("s", style):
        return False

    return True
