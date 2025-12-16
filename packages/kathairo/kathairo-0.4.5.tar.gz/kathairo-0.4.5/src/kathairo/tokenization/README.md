# WhitespaceIncludedTokenizer
This is a modification of SIL's WhitespaceTokenizer.  It has a single change which is to add the line

```
yield Range.create(i, i+1) # Added for kathairo.py to include whitespace
```
in order to return whitespace as tokens.

# LatinWhitespaceIncludedTokenizer
This is a modification of SIL's LatinWordTokenizer.  Rather than using WhitespaceTokenizer it uses WhitespaceIncludedTokenizer.  

It also handles periods, commas, and right-single-apostrophes differently than the LatinWordTokenizer.  It does not assume that since there are characters on either side of these punctuation marks that then the string of text should not be separated.  Rather, it requires certain parameters be met in order for the string to not be split up (For example, commas must be surrounded on either side by numbers).