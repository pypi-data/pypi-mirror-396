import csv
from pathlib import Path
import os

def reconstitute(tsv_file_path:Path, project_name:str, language:str):
    #directory = Path(sys.argv[1])
    #input_files = directory.glob("*reconstitution*.tsv")
    input_files = [Path(tsv_file_path)]
    for input_file in input_files:
        
        verses = create_verse_array(input_file)

        output_file = input_file.parent.parent.parent / project_name / "reconstituted" / f"{input_file.stem}_reconstitution.tsv"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', newline='', encoding='utf-8') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None)

            tsv_writer.writerows(verses) #OLD WAY

def create_verse_array(input_file):
        rows = [r for r in csv.DictReader(input_file.open("r", encoding='utf-8'), delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None)]
        verses = []
        verses.append(["id", "text"])
        text = ""
        parts = []
        last_verse = None
        for row in rows:
            this_verse = row["id"][0:8]
            if last_verse is None:
                last_verse = this_verse
                parts.append(f"{this_verse}")

            if last_verse != this_verse:
                parts.append(text)
                verses.append(parts)#.strip()
                
                last_verse = this_verse
                
                text = ""
                parts = [f"{this_verse}"]#[f""]#

            text+=(row["text"])
            if row["skip_space_after"] == "y":
                continue
            text+=(" ")
        parts.append(text)
        verses.append(parts)#.strip()
        
        return verses