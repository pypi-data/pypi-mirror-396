import csv
from machine.tokenization import WhitespaceTokenizer
from machine.corpora import ScriptureTextCorpus
from machine.scripture import VerseRef, Versification
import re
from kathairo.helpers.strings import is_unicode_punctuation, contains_number
from kathairo.helpers.paths import get_file_location
import os
from kathairo.helpers import strings as strings
from kathairo.helpers import versification
from pathlib import Path

def corpus_to_tsv(
    targetVersification:Versification, 
    sourceVersification:Versification, 
    corpus:ScriptureTextCorpus, 
    tokenizer:WhitespaceTokenizer, 
    project_name:str, 
    language:str, 
    zwRemovalDf:str, 
    stopWordsDf:str, 
    excludeBracketedText:bool = False, 
    excludeCrossReferences:bool = False, 
    regex_rules_class = None
):    

    corpus_array = corpus_to_array(targetVersification, sourceVersification, corpus, tokenizer)

    #TODO try to make these parallel sometime
    array_to_token_level_tsv(corpus_array, project_name, language, zwRemovalDf, stopWordsDf, excludeBracketedText, excludeCrossReferences, regex_rules_class)
    array_to_verse_level_tsv(corpus_array, project_name, language)
  
def corpus_to_array(targetVersification:Versification, sourceVersification:Versification, corpus:ScriptureTextCorpus, tokenizer:WhitespaceTokenizer):
    
    corpus_array = []
    unused_versification_mapping = versification.create_target_to_sources_dict(targetVersification)
    
    verse_range_list = []
    append_range_list = verse_range_list.append

    pattern = re.compile(r'[^0-9]')

    for tokenized_row, untokenized_row in zip(corpus.tokenize(tokenizer), corpus):
        row_tokens = []
        
        for index in range(len(tokenized_row.segment)):
        
            token = tokenized_row.segment[index]
            row_tokens.append(token)
        
        targetVref = VerseRef.from_bbbcccvvv(untokenized_row.ref.verse_ref.bbbcccvvv, targetVersification)
        sourceVref, source_verse_range_end = versification.set_source_verse(targetVref, sourceVersification, unused_versification_mapping)

        if not untokenized_row.is_in_range or untokenized_row.is_range_start:
            for verse_range_row in verse_range_list:
                verse_range_row[3] = rowBcv
                verse_range_row[4] = sourceBcv
                corpus_array.append(verse_range_row)
            verse_range_list.clear()

        sourceBcv = f"{re.sub(r'[^0-9]', '', sourceVref.bbbcccvvvs)}"[1:]
        rowBcv = f"{re.sub(r'[^0-9]', '', untokenized_row.ref.verse_ref.bbbcccvvvs)}"[1:]
        
        row_text = untokenized_row.text
        if row_text:
            if untokenized_row.is_in_range:
                append_range_list([rowBcv, sourceBcv, row_tokens, "", source_verse_range_end, row_text])
            else:
                corpus_array.append([rowBcv, sourceBcv, row_tokens, "", source_verse_range_end, row_text])
        
    return corpus_array

def tokens_to_tsv(
    targetVersification:Versification, 
    sourceVersification:Versification, 
    tsvPath:str, 
    project_name:str, 
    language:str, 
    zwRemovalDf:str, 
    stopWordsDf:str, 
    excludeBracketedText:bool = False, 
    excludeCrossReferences:bool = False, 
    regex_rules_class = None
):
    corpus_array = tokens_to_array(tsvPath, targetVersification, sourceVersification)
    
    #TODO try to make these parallel sometime
    array_to_verse_level_tsv(corpus_array, project_name, language)
    array_to_token_level_tsv(corpus_array, project_name, language, zwRemovalDf, stopWordsDf, excludeBracketedText, excludeCrossReferences, regex_rules_class)

def tokens_to_array(tsvPath:str, targetVersification:Versification, sourceVersification:Versification,):
    pattern = re.compile(r'[^0-9]')
    unused_versification_mapping = versification.create_target_to_sources_dict(targetVersification)

    input_file = Path(tsvPath)
    corpus = [r for r in csv.DictReader(input_file.open("r", encoding='utf-8'), delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None)]
    
    corpus_array = []
    corpus_row = []
    verse_tokens = []
    verse_text = ""
    bcv_id = "40001001"
    previous_bcv_id = "40001001"
    for row in corpus:
        
        previous_bcv_id = bcv_id
        bcv_id = row['id'][0:8]
        if(bcv_id != previous_bcv_id):
            targetVref = VerseRef.from_bbbcccvvv(int(previous_bcv_id))
            sourceVref, source_verse_range_end = versification.set_source_verse(targetVref, sourceVersification, unused_versification_mapping)
            sourceBcv = f"{re.sub(r'[^0-9]', '', sourceVref.bbbcccvvvs)}"[1:]
            
            corpus_row = [previous_bcv_id, sourceBcv, verse_tokens, "", "", verse_text]
            corpus_array.append(corpus_row)
            corpus_row = []
            verse_tokens = []
            verse_text=""
        
        token = row['text']
        #token = [row['id'], row['text'], row['isPunc'], row['isPrimary']]    
        
        verse_tokens.append(token)
        
        verse_text += token
        #verse_text += row['text']
    
    #for final row
    targetVref = VerseRef.from_bbbcccvvv(int(previous_bcv_id))
    sourceVref, source_verse_range_end = versification.set_source_verse(targetVref, sourceVersification, unused_versification_mapping)
    sourceBcv = f"{re.sub(r'[^0-9]', '', sourceVref.bbbcccvvvs)}"[1:]

    corpus_row = [previous_bcv_id, sourceBcv, verse_tokens, "", "", verse_text]
    corpus_array.append(corpus_row)
    
    return corpus_array

def array_to_verse_level_tsv(
    corpus_array, 
    project_name: str, 
    language: str
):
    outputFileName = get_file_location("output", language, project_name, "verse", "verse")
    os.makedirs(os.path.dirname(outputFileName), exist_ok=True)
    with open(outputFileName, 'w', newline='', encoding='utf-8') as out_file:
        
        tsv_writer = csv.writer(out_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None)
        tsv_writer.writerow(["id", "source_verse", "text", "id_range_end", "source_verse_range_end"])
        
        for row in corpus_array:
            tsv_writer.writerow([row[0], row[1], row[5], row[3], row[4]])
            
def array_to_token_level_tsv(corpus_array,
                project_name:str, language:str, zwRemovalDf:str, stopWordsDf:str, excludeBracketedText:bool = False, 
                excludeCrossReferences:bool = False, regex_rules_class = None):
    
    zw_removal_df= zwRemovalDf
        
    stop_words_df=stopWordsDf

    WORD_LEVEL_PUNCT_REGEX = regex_rules_class.WORD_LEVEL_PUNCT_REGEX
    
    outputFileName = get_file_location("output", language, project_name, "token", "token")
    os.makedirs(os.path.dirname(outputFileName), exist_ok=True)
    with open(outputFileName, 'w', newline='', encoding='utf-8') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None)

        tsv_writer.writerow(["id", "source_verse", "text", "skip_space_after", "exclude", "id_range_end", "source_verse_range_end", "required"])

        in_brackets = False
        
        in_parentheses = False
        is_cross_reference = False
        has_number = False
        unprinted_parenthetical_tokens = []
        
        previous_verse_num = 0
        previous_skip_space_after = ""
        
        for row in corpus_array:

            current_verse_num = row[0]
            if(current_verse_num != previous_verse_num):
                wordIndex = 1
            previous_verse_num = current_verse_num

            for index in range(len(row[2])):
            
                has_number, is_cross_reference, unprinted_parenthetical_tokens = process_and_print_parenthetical_tokens(
                    excludeCrossReferences, 
                    tsv_writer, 
                    in_parentheses, 
                    has_number,
                    is_cross_reference, 
                    unprinted_parenthetical_tokens
                )

                #id = row[2][index][0]
                
                token = row[2][index]
                #token = row[2][index][1]
                
                #isPunc = row[2][index][2]
                #if(isPunc == "False"):
                #    isPunc = ""
                #else:
                #    isPunc = "y"
                #isPrimary = row[2][index][3]
                #if(isPrimary == "False"):
                #    isPrimary = "n"
                #else:
                #    isPrimary = "y"
                         
                    
                #Getting Tokens
                previous_previous_token, previous_token, next_token, next_next_token = get_surrounding_tokens(row[2], index)
                
                #Skip Space After
                skip_space_after = "y"
                
                if(is_stop_word(stop_words_df, token)):
                    continue 
                elif((next_token in strings.spaces) or (next_token in strings.invisible_spaces and next_next_token in strings.spaces)):
                    skip_space_after = ""
                
                #''' 
                #ZW Characters
                token = remove_zw_characters(zw_removal_df, token)

                #Exclude
                exclude = ""

                if isinstance(token, str) and len(token) > 0 and all(in_brackets or is_unicode_punctuation(char) for char in token):
                    exclude = "y"

                    if is_token_word_level_punct(stop_words_df, WORD_LEVEL_PUNCT_REGEX, previous_skip_space_after, token, previous_previous_token, previous_token, next_token, next_next_token, skip_space_after):
                        exclude = ""
                    
                if(excludeBracketedText and '[' in token):
                    in_brackets = True
                    exclude = "y"
                if(']' in token):
                    in_brackets = False
                    
                if(excludeCrossReferences and '(' in token): #add to unit test to look for that all things marked as cross references are indeed cross-references and no token has a colon and a parentheses
                    in_parentheses = True
                if(excludeCrossReferences and in_parentheses and contains_number(token)):#add this change to the unit test
                    has_number = True
                if(excludeCrossReferences and in_parentheses and has_number and ':' in token):
                    is_cross_reference = True
                
                #Required
                required = calculate_required(token)
                #'''
                
                #Printing
                wordIndexStr = str(wordIndex).zfill(3)
                
                if(row[5] != ""):
                    if(in_parentheses):
                        unprinted_parenthetical_tokens.append(([f"{row[0]}{wordIndexStr}", f"{row[1]}", token, skip_space_after, exclude,  row[3], row[4], required]))
                        #unprinted_parenthetical_tokens.append(([id, f"{row[1]}", token, skip_space_after, isPunc,  row[3], row[4], isPrimary]))
                    else:
                        tsv_writer.writerow([f"{row[0]}{wordIndexStr}", f"{row[1]}", token, skip_space_after, exclude, row[3], row[4], required])
                        #tsv_writer.writerow([id, f"{row[1]}", token, skip_space_after, isPunc, row[3], row[4], isPrimary])
                
                if(')' in token):
                    in_parentheses = False
                
                wordIndex += 1 
                previous_skip_space_after = skip_space_after

def process_and_print_parenthetical_tokens(excludeCrossReferences, tsv_writer, in_parentheses, has_number, is_cross_reference, unprinted_parenthetical_tokens):
    if(not in_parentheses):    
        for unprinted_cross_reference_token in unprinted_parenthetical_tokens:
            if(excludeCrossReferences and is_cross_reference):
                unprinted_cross_reference_token[4] = 'y' #exclude if is_cross_reference
            tsv_writer.writerow(unprinted_cross_reference_token)
        has_number = False
        is_cross_reference = False
        unprinted_parenthetical_tokens.clear()
    return has_number, is_cross_reference, unprinted_parenthetical_tokens

def get_surrounding_tokens(token_array, index):
    segment = token_array
    max_segment_index = len(segment) - 1

    previous_previous_token = segment[index - 2] if index - 2 >= 0 else ''
    previous_token = segment[index - 1] if index - 1 >= 0 else ''
    next_token = segment[index + 1] if index + 1 <= max_segment_index else strings.space
    next_next_token = segment[index + 2] if index + 2 <= max_segment_index else strings.space

    return previous_previous_token, previous_token, next_token, next_next_token

def is_stop_word(stop_words_df, token):
    return token in strings.stop_words or (stop_words_df is not None and token in stop_words_df["stop_words"].to_numpy())      

def remove_zw_characters(zw_removal_df, token):
    if(zw_removal_df is not None and token in zw_removal_df["words"].to_numpy()):
        token = token.replace(strings.zwsp, strings.empty_string).replace(strings.zwj, strings.empty_string).replace(strings.zwnj, strings.empty_string)
    return token

def is_token_word_level_punct(stop_words_df, WORD_LEVEL_PUNCT_REGEX, previous_skip_space_after, token, previous_previous_token, previous_token, next_token, next_next_token, skip_space_after):
    next_substring_token = (
        strings.space + next_token if skip_space_after == ""
        else next_next_token if is_stop_word(stop_words_df, next_token)
        else next_token
    )

    previous_substring_token = (
        previous_token + strings.space if previous_skip_space_after == ""
        else previous_previous_token if is_stop_word(stop_words_df, previous_token)
        else previous_token
    )

    substring = previous_substring_token + token + next_substring_token
    index = len(previous_substring_token + token) - 1

    return WORD_LEVEL_PUNCT_REGEX.match(substring, index) is not None

def calculate_required(token):
    return "y" if any(not is_unicode_punctuation(char) for char in token) else "n"         