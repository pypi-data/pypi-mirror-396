import regex as re
from machine.scripture import (
    VerseRef,
    Versification,
)

def create_target_to_sources_dict(targetVersification:VerseRef):
    unused_versification_mapping = {}
    
    for key, value in targetVersification.mappings._standard_to_versification.items():
        if value.bbbcccvvvs in unused_versification_mapping:
            unused_versification_mapping[value.bbbcccvvvs].append(key)
        else:
            unused_versification_mapping[value.bbbcccvvvs] = [key]
    
    return unused_versification_mapping

def set_source_verse(targetVref:VerseRef, sourceVersification:Versification, unused_versification_mapping:dict[VerseRef:VerseRef]) -> tuple:
    
    sourceVref = ""
    source_verse_range_end = ""    
    
    mappings_to_targetVref = unused_versification_mapping.get(targetVref.bbbcccvvvs)
    
    if(mappings_to_targetVref != None):
        mappings_to_targetVref_len = len(mappings_to_targetVref)
               
        sourceVref = mappings_to_targetVref[0]
        if(mappings_to_targetVref_len > 1):
            last_mapping = mappings_to_targetVref[mappings_to_targetVref_len-1]
            source_verse_range_end = f"{re.sub(r'[^0-9]', '', last_mapping.bbbcccvvvs)}"[1:]
        
    if(sourceVref == ""):
        targetVref.change_versification(sourceVersification)
        sourceVref = targetVref
    
    return sourceVref, source_verse_range_end