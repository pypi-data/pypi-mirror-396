import polars as pl
import csv

book_abbrev_dict = {
    1:'GEN',
    2:'EXO',
    3:'LEV',
    4:'NUM',
    5:'DEU',
    6:'JOS',
    7:'JDG',
    8:'RUT',
    9:'1SA',
    10:'2SA',
    11:'1KI',
    12:'2KI',
    13:'1CH',
    14:'2CH',
    15:'EZR',
    16:'NEH',
    17:'EST',
    18:'JOB',
    19:'PSA',
    20:'PRO',
    21:'ECC',
    22:'SNG',
    23:'ISA',
    24:'JER',
    25:'LAM',
    26:'EZK',
    27:'DAN',
    28:'HOS',
    29:'JOL',
    30:'AMO',
    31:'OBA',
    32:'JON',
    33:'MIC',
    34:'NAM',
    35:'HAB',
    36:'ZEP',
    37:'HAG',
    38:'ZEC',
    39:'MAL',
    40:'MAT',
    41:'MRK',
    42:'LUK',
    43:'JHN',
    44:'ACT',
    45:'ROM',
    46:'1CO',
    47:'2CO',
    48:'GAL',
    49:'EPH',
    50:'PHP',
    51:'COL',
    52:'1TH',
    53:'2TH',
    54:'1TI',
    55:'2TI',
    56:'TIT',
    57:'PHM',
    58:'HEB',
    59:'JAS',
    60:'1PE',
    61:'2PE',
    62:'1JN',
    63:'2JN',
    64:'3JN',
    65:'JUD',
    66:'REV',
}

df = pl.read_csv("nt_CUVMPS_verse.tsv", separator='\t', infer_schema_length=0)

previous_chapter_id = 0
previous_book_id = 0

book_arr = []

for row in df.iter_rows(named=True):
    id = row["id"]
    verse = str(row["text"])

    book_id = id[0:2]
    chapter_id = id[2:5]
    verse_id = id[5:8]
    

    
    if(previous_book_id != book_id):
        if(book_arr != []):
            with open(output_file_name, 'w', newline='', encoding='utf-8') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t') # quoting=csv.QUOTE_NONE, quotechar=None
                tsv_writer.writerows(book_arr)
            
        book_arr = []
        #df[row_index, "text"] = f"\\id {book_abbrev} \\c {int(chapter_id)} \\v {int(verse_id)} {verse}"
        book_abbrev = book_abbrev_dict[int(book_id)]
        output_file_name = f"SFM/{book_id}_{book_abbrev}.SFM"
        
        book_arr.append([f"\\id {book_abbrev} \\c {int(chapter_id)} \\v {int(verse_id)} {verse}"])
    elif(previous_chapter_id != chapter_id):
        #df[row_index, "text"] = f"\\c {int(chapter_id)} \\v {int(verse_id)} {verse}"
        book_arr.append([f"\\c {int(chapter_id)} \\v {int(verse_id)} {verse}"])
    else:
        #df[row_index, "text"] = f"\\v {int(verse_id)} {verse}"
        book_arr.append([f"\\v {int(verse_id)} {verse}"])
    
    previous_chapter_id = chapter_id
    previous_book_id = book_id

with open(output_file_name, 'w', newline='', encoding='utf-8') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t') # quoting=csv.QUOTE_NONE, quotechar=None
    tsv_writer.writerows(book_arr)

#df.select(["text"]).write_csv(output_file_name, separator='\t')