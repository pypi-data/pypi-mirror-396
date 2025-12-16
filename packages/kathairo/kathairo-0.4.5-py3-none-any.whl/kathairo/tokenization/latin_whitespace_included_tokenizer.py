from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple, cast

import regex as re

from machine.annotations.range import Range
from machine.utils.string_utils import is_control, is_punctuation, is_symbol
from kathairo.tokenization.whitespace_included_tokenizer import WhitespaceIncludedTokenizer
from spacy.lang.fr.tokenizer_exceptions import FR_BASE_EXCEPTIONS

URL_REGEX = re.compile(r"(?:[\w-]+://?|www[.])[^\s()<>]+(?:[\w\d]+|(?:[^\p{P}\s]|/))", re.IGNORECASE)

CONTRACTION_WORD_REGEX = re.compile(r"\b\w+([-]\w+)*[\'\’]\w+\b")

class LatinWhitespaceIncludedWordTokenizer(WhitespaceIncludedTokenizer): #uses WhitespaceIncludedTokenizer
    def __init__(self, regex_rules_class, abbreviations: Iterable[str] = [], treat_apostrophe_as_single_quote: bool = False, language:str = None) -> None:
        self._abbreviations = {a.lower() for a in abbreviations}
        self.treat_apostrophe_as_single_quote = treat_apostrophe_as_single_quote
        self.language = language
        self.regex_rules = regex_rules_class.get_regex_rules()

    def tokenize_as_ranges(self, data: str, data_range: Optional[Range[int]] = None) -> Iterable[Range[int]]:
        if data_range is None:
            data_range = Range.create(0, len(data))
        ctxt = LatinWhitespaceIncludedWordTokenizer._TokenizeContext()
        for char_range in super().tokenize_as_ranges(data, data_range):
            url_match = URL_REGEX.match(data[char_range.start : char_range.end])
            if url_match is not None:
                url_len = len(url_match.group())
                yield Range.create(char_range.start, char_range.start + url_len)
                ctxt.index = char_range.start + url_len
            else:
                ctxt.index = char_range.start

            ctxt.word_start = -1
            ctxt.inner_word_punct = -1

            while ctxt.index < char_range.end:
                token_range1, token_range2 = self._process_character(data, data_range, ctxt)
                if token_range1 is not None:
                    yield token_range1
                if token_range2 is not None:
                    yield token_range2

            if ctxt.word_start != -1:
                if ctxt.inner_word_punct != -1:
                    inner_punct_str = data[ctxt.inner_word_punct : char_range.end]
                    if (
                        inner_punct_str == "." and self._is_abbreviation(data, ctxt.word_start, ctxt.inner_word_punct)
                    ) or (inner_punct_str == "'" and not self.treat_apostrophe_as_single_quote):
                        #range1 = data[ctxt.word_start, char_range.end]
                        yield Range.create(ctxt.word_start, char_range.end)
                    else:
                        #range1 = data[cast(int, ctxt.word_start): ctxt.inner_word_punct]
                        yield Range.create(cast(int, ctxt.word_start), ctxt.inner_word_punct)
                        #range2 = data[ctxt.inner_word_punct: char_range.end]
                        yield Range.create(ctxt.inner_word_punct, char_range.end)
                else:
                    #range1 = data[ctxt.word_start: char_range.end]
                    yield Range.create(ctxt.word_start, char_range.end)

    def _process_character(
        self, data: str, data_range: Range[int], ctxt: LatinWhitespaceIncludedWordTokenizer._TokenizeContext
    ) -> Tuple[Optional[Range[int]], Optional[Range[int]]]:
        token_ranges: Tuple[Optional[Range[int]], Optional[Range[int]]] = (None, None)
        c = data[ctxt.index]
        end_index = ctxt.index + 1

        if is_punctuation(c) or is_symbol(c) or is_control(c):
            
            while end_index != data_range.end and data[end_index] == c:
                end_index += 1
            if ctxt.word_start == -1:
                if c == "'" and not self.treat_apostrophe_as_single_quote:
                    ctxt.word_start = ctxt.index
                else:
                    match = None
                    for rule in self.regex_rules:
                        match = rule.match(data, ctxt.index)
                    if match is None:
                        #range1 = data[ctxt.index: end_index]
                        token_ranges = (Range.create(ctxt.index, end_index), None)
                    else:
                        ctxt.word_start = ctxt.index
            elif ctxt.inner_word_punct != -1:
                inner_punct_str = data[ctxt.inner_word_punct : ctxt.index]
                if inner_punct_str == "'" and not self.treat_apostrophe_as_single_quote:
                    #range1 = data[ctxt.word_start: ctxt.index]
                    token_ranges = (Range.create(ctxt.word_start, ctxt.index), None)
                else:
                    #range1 = data[ctxt.word_start: ctxt.inner_word_punct]
                    #range2 = data[ctxt.inner_word_punct: ctxt.index]
                    token_ranges = (
                        Range.create(ctxt.word_start, ctxt.inner_word_punct),
                        Range.create(ctxt.inner_word_punct, ctxt.index),
                    )
                ctxt.word_start = ctxt.index
            else:
                for rule in self.regex_rules:
                    substring = data[ctxt.index-1:ctxt.index+2]      
                    
                    match = rule.match(data, ctxt.index)
                    #match = rule.search(substring)
                    if match is not None:
                        ctxt.inner_word_punct = ctxt.index
                        group = match.group()
                        ctxt.index += len(group)
                    
                        if(self.language == "fra"):
                            contraction_token = CONTRACTION_WORD_REGEX.match(data, ctxt.word_start)
                            if(contraction_token is not None):
                                group = contraction_token.group().replace("’","'")
                                if(group not in FR_BASE_EXCEPTIONS):
                                    #range1 = data[ctxt.word_start:ctxt.index]
                                    token_ranges = (Range.create(ctxt.word_start, ctxt.index),None)
                                    ctxt.word_start = -1
                                
                        return token_ranges
                #range1 = data[ctxt.word_start:ctxt.index]
                #range2 = data[ctxt.index:end_index]
                token_ranges = (Range.create(ctxt.word_start, ctxt.index), Range.create(ctxt.index, end_index))
                ctxt.word_start = -1
        elif ctxt.word_start == -1:
            ctxt.word_start = ctxt.index

        ctxt.inner_word_punct = -1
        ctxt.index = end_index
        return token_ranges

    def _is_abbreviation(self, data: str, start: int, end: int) -> bool:
        substr = data[start:end].lower()
        return substr in self._abbreviations

    @dataclass
    class _TokenizeContext:
        index: int = 0
        word_start: int = 0
        inner_word_punct: int = 0
