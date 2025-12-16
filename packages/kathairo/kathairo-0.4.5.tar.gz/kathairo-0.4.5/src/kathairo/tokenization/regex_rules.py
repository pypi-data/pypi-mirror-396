import regex as re

class DefaultRegexRules:
    INNER_WORD_PUNCT = r"[&\-:=@\xAD\xB7\u2010\u2011\u2027]+|['_]+"
    INNER_WORD_PUNCT_REGEX = re.compile(rf"{INNER_WORD_PUNCT}")

    NUMBER_COMMA_REGEX = re.compile(
        r"(?<=\d),(?=\d)"
    )

    NUMBER_PERIOD_REGEX = re.compile(
        r"(?<=\d)\.(?=\d)"
    )

    RIGHT_SINGLE_QUOTE_AS_APOSTROPHE_REGEX = re.compile(
        r"(?<=\p{L})’(?=\p{L})"
    )

    CONTRACTION_WORD_REGEX = re.compile(
        r"\b\w+(?:[\'\w\’]+)?\b"
    )
    
    def get_regex_rules(self):
        regex_rules = [
            self.INNER_WORD_PUNCT_REGEX,
            self.NUMBER_COMMA_REGEX,
            self.NUMBER_PERIOD_REGEX,
            self.RIGHT_SINGLE_QUOTE_AS_APOSTROPHE_REGEX,
            #CONTRACTION_WORD_REGEX
        ]
        
        return regex_rules

    #NON_JOINING_PUNCT =r"[.،«?!।၊–…{}—《》（）‘’“”;？：；。！，、,\[\]()]"
    NON_JOINING_PUNCT = r"[.،«?!।၊–…{}—《》（）‘’“”;？：；。！，、,\[\]()]"
    #does nothing, oddly        ၊ 
    #is joining in some cases   –   —

    WORD_LEVEL_PUNCT_REGEX = re.compile(
        fr"(?<=\w)(\p{{P}}(?<!{NON_JOINING_PUNCT}))(?=\w)"
    )