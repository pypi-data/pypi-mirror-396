from machine.scripture import Versification, VerseRef

bible_book_abbreviations = [
    'GEN',
    'EXO',
    'LEV',
    'NUM',
    'DEU',
    'JOS',
    'JDG',
    'RUT',
    '1SA',
    '2SA',
    '1KI',
    '2KI',
    '1CH',
    '2CH',
    'EZR',
    'NEH',
    'EST',
    'JOB',
    'PSA',
    'PRO',
    'ECC',
    'SNG',
    'ISA',
    'JER',
    'LAM',
    'EZK',
    'DAN',
    'HOS',
    'JOL',
    'AMO',
    'OBA',
    'JON',
    'MIC',
    'NAM',
    'HAB',
    'ZEP',
    'HAG',
    'ZEC',
    'MAL',
    'MAT',
    'MRK',
    'LUK',
    'JHN',
    'ACT',
    'ROM',
    '1CO',
    '2CO',
    'GAL',
    'EPH',
    'PHP',
    'COL',
    '1TH',
    '2TH',
    '1TI',
    '2TI',
    'TIT',
    'PHM',
    'HEB',
    'JAS',
    '1PE',
    '2PE',
    '1JN',
    '2JN',
    '3JN',
    'JUD',
    'REV'
]

def save_versification(versification):
    with open("src/kathairo/versification/output.vrs", "w", encoding="utf-8") as file:
        
        file.write('# Versification  "English"\n')
        for book, book_size_array in zip(bible_book_abbreviations, versification.book_list):
            book_size_line = book
            
            current_chapter = 1
            for end_verse in book_size_array:
                book_size_line += f" {current_chapter}:{end_verse}"
                current_chapter += 1
                
            file.write(f'{book_size_line}\n')
        
        for key in versification.mappings._versification_to_standard:
            file.write(f'{key} = {versification.mappings._versification_to_standard[key]}\n')

def fix_versification(versification):
    fix_missing_end_verses_in_source_verse()

versification = Versification.load("src/kathairo/versification/eng.vrs")

fixed_versification = fix_versification(versification)

save_versification(versification)

#genesis_31_55 = VerseRef.from_string("GEN 31:55", versification)
#mapping = versification.mappings._versification_to_standard.get_versification(genesis_31_55)
#print(mapping)

#if versification_ref in versification.mappings._versification_to_standard:
#    del versification.mappings._standard_to_versification[versification.mappings._versification_to_standard[versification_ref]]
#    del versification.mappings._versification_to_standard[versification_ref]

# Add the new mapping
#versification.add_mapping(new_versification_ref, new_standard_ref)

versification.book_list[0][0] = 0

versification.mappings.add_mapping(
    VerseRef("GEN", 1, 1, versification), 
    VerseRef("GEN", 1, 2, versification)
)
