import csv
from machine.utils import string_utils
from machine.corpora import UsxFileTextCorpus
from machine.corpora import ParatextTextCorpus, UsfmFileTextCorpus, UsxFileTextCorpus
from machine.tokenization import LatinWordTokenizer, WhitespaceTokenizer
from machine.scripture import (
    ENGLISH_VERSIFICATION,
    ORIGINAL_VERSIFICATION,
    RUSSIAN_ORTHODOX_VERSIFICATION,
    RUSSIAN_PROTESTANT_VERSIFICATION,
    SEPTUAGINT_VERSIFICATION,
    VULGATE_VERSIFICATION,
    LAST_BOOK,
    ValidStatus,
    VerseRef,
    Versification,
    get_bbbcccvvv,
)


import time
start_time=time.time()
#do something

from machine.corpora import ParatextTextCorpus
from machine.tokenization import LatinWordTokenizer

sourceVersification = Versification(name = "sourceVersification", base_versification=ENGLISH_VERSIFICATION)
targetVersification = Versification(name = "targetVersification", base_versification=ENGLISH_VERSIFICATION)

source_corpus = UsfmFileTextCorpus("./resources/bsb_usfm", versification = sourceVersification)
target_corpus = UsfmFileTextCorpus("./resources/arb-vd_usfm", versification = targetVersification)

parallel_corpus = source_corpus.align_rows(target_corpus).tokenize(LatinWordTokenizer())

from machine.translation import word_align_corpus
from machine.corpora import AlignedWordPair

aligned_corpus = word_align_corpus(parallel_corpus.lowercase())
#aligned_corpus = word_align_corpus(parallel_corpus.lowercase(), aligner="ibm1")

end_time=time.time()-start_time

for row in aligned_corpus.take(5):
    print("Source:", row.source_text)
    print("Target:", row.target_text)
    print("Alignment:", AlignedWordPair.to_string(row.aligned_word_pairs, include_scores=False))