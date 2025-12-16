from kathairo.tokenization.ChineseBibleWordTokenizer import ChineseBibleWordTokenizer
from machine.corpora import UsxFileTextCorpus
from machine.corpora import UsfmFileTextCorpus, UsxFileTextCorpus
from machine.tokenization import LatinWordTokenizer
from machine.scripture import (
    ENGLISH_VERSIFICATION,
    Versification
)

from machine.corpora import UsfmStylesheet

usfm = """\\id MAT - Test
\\h Matthew
\\mt Matthew
\\ip An introduction to Matthew
\\c 1
\\s Chapter One
\\p
\\v 1 This is verse \\pn one\\pn* of chapter one.
\\v 2 This is verse two\\f + \\fr 1:2: \\ft This is a footnote.\\f* of chapter one. 
""".replace("\n", "\r\n")

stylesheet = UsfmStylesheet("usfm.sty")

from machine.corpora import UsfmTokenizer, UsfmTokenType

usfm_tokenizer = UsfmTokenizer(stylesheet)
#tokens = usfm_tokenizer.tokenize(usfm)
#for token in tokens:
#  if token.type is UsfmTokenType.TEXT:
#    token.text = token.text.upper()

#print(usfm_tokenizer.detokenize(tokens))

from machine.corpora import UsfmParser

#usfm_parser = UsfmParser(stylesheet, usfm)
#state = usfm_parser.state
#while usfm_parser.process_token():
#  if state.token.type is UsfmTokenType.TEXT and state.is_verse_text:
#    state.token.text = state.token.text.upper()

#print(usfm_tokenizer.detokenize(state.tokens))

from machine.corpora import UsfmParserHandler

tokenizer = LatinWordTokenizer()
tokenized_row = tokenizer.tokenize("दाऊद ने मीकल से कहा, “ यहोवा, जिस ने तेरे पिता और उसके समस्त घराने के बदले मुझ को चुनकर अपनी प्रजा इस्राएल का प्रधान होने को ठहरा दिया है, उसके सम्मुख मैं ऐसा नाचा-- और मैं यहोवा के सम्मुख इसी प्रकार नाचा करूँगा ।")
for token in tokenized_row:
  print(token)
stop = True

class VerseTextUppercaser(UsfmParserHandler):
  def text(self, state, text):
    if state.is_verse_text:
      state.token.text = text.upper()
      print(state.token.text)

usfm_parser = UsfmParser(stylesheet=stylesheet, usfm=usfm, handler=VerseTextUppercaser())
usfm_parser.process_tokens()

print(usfm_tokenizer.detokenize(usfm_parser.state.tokens))

targetVersification = Versification.load("./resources/bsb_usx/release/versification.vrs", fallback_name="web")
corpus = UsfmFileTextCorpus("./resources/bsb_usfm", versification = targetVersification, include_markers=True)
tokenizer = LatinWordTokenizer()

row = corpus.get_rows

for row in corpus:
    tokenized_row = tokenizer.tokenize(row.text)
    if(row.ref.bbbcccvvvs[:6] == "019003"):
        print(row)

targetVersification = Versification.load("./resources/occb_simplified_usx/release/versification.vrs", fallback_name="web")
corpus = UsxFileTextCorpus("./resources/occb_simplified_usx/release/USX_1", versification = targetVersification)

for row in corpus:
    if(row.ref.bbbcccvvvs[:6] == "003006"):
        print(row)