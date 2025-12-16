import unicodedata

def is_unicode_punctuation(char):
    category = unicodedata.category(char)
    return category.startswith("P")

def contains_number(string):
    return any(char.isdigit() for char in string)

empty_string = ""

zwsp = "​"#\u200b
zwj = "‍"#\u200d
zwnj = "‌"#\u200c
nbsp = "\xa0"
space = " "
six_per_em_space = " "#\u2006

stop_words = [
    space,
    zwsp,
    zwj,
    zwnj,
    nbsp,
    six_per_em_space
]

spaces = [
    space,
    nbsp,
    six_per_em_space
]

invisible_spaces = [
    zwsp
]

