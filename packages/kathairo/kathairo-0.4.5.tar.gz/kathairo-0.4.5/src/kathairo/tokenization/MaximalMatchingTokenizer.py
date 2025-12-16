from machine.tokenization import WhitespaceTokenizer
from machine.annotations.range import Range
from typing import List

'''
Copyright © 2023 Cherith Analytics, LLC
Permission is hereby granted, free of charge, to any person obtaining a copy of portions of this file, specifically WhitespaceDelimitLongestWordMatches() and GetNgram(), (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

''' Notes from Andi:
The maximal matching algorithm has two problems: 

(1) it can be wrong when there are combinational ambiguity 
where a sequence of characters can be single word/token in some contexts but separate words in other contexts.  
Since MM always go for the bigger one, these sequences will always be segmented as a single word regardless of contexts.  
Cases of combinational ambiguity do not occur very frequently, though.

(2) it can be wrong when there are overlapping ambiguities where a sequence of characters such as ABC can be 
segmented as AB C or A BC depending on the contexts.  The overlap.txt file is used to correct such mistakes, 
favoring the more likely segmentation in the Bible.

Another way to resolve overlapping ambiguities is to do it from both directions.  The code I gave you only does 
it in one direction: left to right.  But you can do both left to right and right to left.  The tokens you can get in 
both left and right directions are guaranteed to be correct, but you need a separate routine to handle the ones that 
do not agree in both directions.  You may lose words if you only keep the tokens that you can get from both directions.  
In other words, bi-directional maximal matching can improve precision but lose in recall.

In spite of these problems, the accuracy of MM is pretty high and meets the needs of most applications.

To improve the coverage of the current tokenizer (i.e. to be able to handle texts that contain words that are not in the word list), 
we just need to add words to the list.  However, the more words are in the list, the more likely we will have combinational and overlapping 
ambiguities.
'''

# <summary>
#
# Based on Andi Wu's BibleTokenizer (andi.wu@globalbibleinitiative.org)
# 
# 1. looks at a verse's characters as if each is a linear (sequential) graph of 
# vertices (characters) and edges (their pairwise adjacency).
# 2. tries to match them to the pairs of characters in the vocabulary file (words.txt), considering each pair 
# in this file as as two vertices connected by a pair-wise-edge, using a simple greedy algorithm,
# 3. to find the maximal matching set for the verse consistent with the pairs in the vocabulary file,
# 4. which are considered characters joined together as a token.
# 
# Words contains all the words to match.
# 
# CombinationCorrections map combination errors to corrections. 
# 
# </summary>

class MaximalMatchingTokenizer(WhitespaceTokenizer):
      
    MAX_GRAM_DEFAULT:int = 10

    _maxGram:int

    #CombinationCorrections = {}

    # <summary>
    # Add words to maximal match on to Words property.
    # </summary>
    # <param name="maxGram"></param>
    def __init__(self, maxGram:int):
            super().__init__()
            self._maxGram = maxGram
            self.CombinationCorrections = {}
            self.Words = set()

    def tokenize_as_ranges(self, data:str, range:Range)-> List[Range]:
        if range is None:
            range = Range.create(0, len(data))
        
        #segment words
        whitespaceSegmentedText = self.WhitespaceDelimitLongestWordMatches(data[range.start:range.length], self.Words, self._maxGram)

        #correct overlaps
        self.CorrectCombinations(whitespaceSegmentedText)

        rangesForWhitespaceSegmentedText = super().tokenize_as_ranges(whitespaceSegmentedText, Range.create(0, len(whitespaceSegmentedText)))

        # Adjust the ranges for the original text
        adjusted_ranges = [Range.create(r.start - i, r.end - i) for i, r in enumerate(rangesForWhitespaceSegmentedText)]

        return adjusted_ranges

    # <summary>
    # Use to correct the following combination errors by replacing a sequence of characters with another:
    # 1. maximal match algorithm favors largest combination of characters, but this can be incorrect when in context with other characters
    # that follow. For example, if algorithm tokenizes as AB, in cases where AB is followed by C the characters A and B should instead be tokenized as A B.
    # 2. When there is an overlapping ambiguity, for example, if algorithm tokenizes as AB C but it could have also tokenized as A BC.
    # 
    # These corrections should favor the majority cases.
    # </summary>
    # <param name="whitespaceSegmentedText"></param>
    
    def CorrectCombinations(self, whitespaceSegmentedText):
        for key, value in self.CombinationCorrections.items():
            whitespaceSegmentedText = whitespaceSegmentedText.replace(key, value)

    # <summary>
    # Note: whitespace delimits spaces that aren't a part of a match.
    # </summary>
    # <param name="text"></param>
    # <param name="words"></param>
    # <param name="maxGram"></param>
    # <returns></returns>
    def WhitespaceDelimitLongestWordMatches(self, text:str, words:[str], maxGram:int):
        segments = ""

        chars = list(text)

        #for i in range(0,i<chars.length,1):
        #    for n in range(maxGram,n > 0,-1):
        #        ngram = self.GetNgram(chars, i, n)
        #        if ngram != "" and (n == 1 or ngram in self.Words):
        #            segments += ngram + (" " if len(ngram) != 1 or not ngram.isspace() else "") # only delimit if the single character is not a space, otherwise just add space.
        #            i = i + n - 1; # need to subtract 1 because the iterator increments after the body.
        #            break
        
        i=0
        while i < len(chars):
            for n in range(self._maxGram, 0, -1):
                ngram = self.GetNgram(chars, i, n)
                if ngram != "" and (n == 1 or ngram in self.Words):
                    segments += ngram + (" " if len(ngram) != 1 or not ngram.isspace() else "")
                    i = i + n - 1
                    break
            i += 1
        
        return segments

    def GetNgram(self, chars:[str], index:int, length:int):
        ngram:str = ""

        i:int = index
        while(i+length <= len(chars) and length>0):
                
                ngram += chars[i]
                
                i+=1
                length-=1

        #for i in range(index, index + length):
        #    if i < len(chars):
        #        ngram += chars[i]

        return ngram

    #def get_ngram(self, chars, index, length):
    #    if index + length <= len(chars) and length > 0:
    #        return "".join(chars[index:index+length])
    #    return ""