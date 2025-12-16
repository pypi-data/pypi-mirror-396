import time
start = time.time()

import json
from concurrent.futures import ProcessPoolExecutor, as_completed

from kathairo.tokenization.ChineseBibleWordTokenizer import ChineseBibleWordTokenizer
from machine.tokenization import LatinWordTokenizer
from kathairo.tokenization.latin_whitespace_included_tokenizer import LatinWhitespaceIncludedWordTokenizer
from kathairo.tokenization.regex_rules import DefaultRegexRules

from kathairo.parsing.usx.usx_file_text_corpus import UsxFileTextCorpus
from kathairo.parsing.usfm.usfm_file_text_corpus import UsfmFileTextCorpus
from kathairo.parsing.usfm.usfm_handlers import ModifiedTextRowCollector

from machine.scripture import ORIGINAL_VERSIFICATION, Versification
from kathairo.helpers.paths import import_module_from_path

from kathairo.tsvs.build_tsv import corpus_to_tsv, tokens_to_tsv

import polars as pl

SOURCE_VERSIFICATION = Versification(name="sourceVersification", base_versification=ORIGINAL_VERSIFICATION)

def create_tokenizer(json_object, regex_rules_class):
    treat_apostrophe_as_single_quote = json_object.get("treatApostropheAsSingleQuote", False)
    language = json_object.get("language")

    if json_object.get("chineseTokenizer"):
        return ChineseBibleWordTokenizer()
    elif json_object.get("latinTokenizer"):
        return LatinWordTokenizer(treat_apostrophe_as_single_quote=treat_apostrophe_as_single_quote)
    elif json_object.get("latinWhiteSpaceIncludedTokenizer"):
        return LatinWhitespaceIncludedWordTokenizer(
            treat_apostrophe_as_single_quote=treat_apostrophe_as_single_quote,
            language=language,
            regex_rules_class=regex_rules_class
        )
    return None

def create_corpus(json_object, target_versification, psalm_superscription_tag):
    if "targetUsfmCorpusPath" in json_object:
        return UsfmFileTextCorpus(
                json_object["targetUsfmCorpusPath"],
            handler=ModifiedTextRowCollector,
            versification=target_versification,
            psalmSuperscriptionTag=psalm_superscription_tag
        )
    return UsxFileTextCorpus(
        json_object["targetUsxCorpusPath"],
        versification=target_versification
    )

def get_config(json_object):
    config_dict = {}

    regex_rules_class = DefaultRegexRules()
    if "regexRulesPath" in json_object:
        regex_rules_module = import_module_from_path("regex_rules", json_object["regexRulesPath"])
        regex_rules_class = getattr(regex_rules_module, "CustomRegexRules", DefaultRegexRules)()
    config_dict["regexRulesClass"] = regex_rules_class

    config_dict["tokenizer"] = create_tokenizer(json_object, regex_rules_class)

    target_versification_path = json_object.get("targetVersificationPath")
    config_dict["targetVersificationPath"] = target_versification_path
    config_dict["targetVersification"] = Versification.load(target_versification_path, fallback_name="web")

    config_dict["psalmSuperscriptionTag"] = json_object.get("psalmSuperscriptionTag", 'd')

    config_dict["projectName"] = json_object.get("projectName")
    if "tsvPath" in json_object:
        config_dict["tsvPath"] = json_object.get("tsvPath")
        config_dict["isCorpus"] = False
    else:
        config_dict["corpus"] = create_corpus(json_object, config_dict["targetVersification"], config_dict["psalmSuperscriptionTag"])
        config_dict["isCorpus"] = True
    
    config_dict["excludeBracketedText"] = json_object.get("excludeBracketedText", False)
    config_dict["excludeCrossReferences"] = json_object.get("excludeCrossReferences", False)
    config_dict["language"] = json_object.get("language")
    
    zw_removal_path = json_object.get("zwRemovalPath")
    config_dict["zwRemovalDf"] = pl.read_csv(zw_removal_path, separator='\t', infer_schema_length=0, quote_char=None) if zw_removal_path else None
    
    stop_words_path = json_object.get("stopWordsPath")
    config_dict["stopWordsDf"] = pl.read_csv(stop_words_path, separator='\t', infer_schema_length=0, quote_char=None) if stop_words_path else None
    
    return config_dict

def process_corpus(json_object):
    
    config_dict = get_config(json_object)

    if(config_dict["isCorpus"]):
        return{
            'corpus_to_tsv': corpus_to_tsv(
                targetVersification=config_dict["targetVersification"],
                sourceVersification=SOURCE_VERSIFICATION,
                corpus=config_dict["corpus"],
                tokenizer=config_dict["tokenizer"],
                project_name=config_dict["projectName"],
                excludeBracketedText=config_dict["excludeBracketedText"],
                excludeCrossReferences=config_dict["excludeCrossReferences"],
                language=config_dict["language"],
                zwRemovalDf=config_dict["zwRemovalDf"],
                stopWordsDf=config_dict["stopWordsDf"],
                regex_rules_class=config_dict["regexRulesClass"]
            )
        }
    else:
        return{
            'tokens_to_tsv': tokens_to_tsv(
                targetVersification=config_dict["targetVersification"],
                sourceVersification=SOURCE_VERSIFICATION,
                tsvPath=config_dict["tsvPath"],
                project_name=config_dict["projectName"],
                language=config_dict["language"],
                zwRemovalDf=config_dict["zwRemovalDf"],
                stopWordsDf=config_dict["stopWordsDf"],
                excludeBracketedText=config_dict["excludeBracketedText"],
                excludeCrossReferences=config_dict["excludeCrossReferences"],
                regex_rules_class=config_dict["regexRulesClass"]
            )            
        }
    
def get_json_data(json_file):
    with open(json_file) as file:
        json_data = json.load(file)

    solo_project = next((obj for obj in json_data if "solo" in obj), None)    
    if(solo_project is not None):
        json_data = [solo_project]
        
    return json_data

def main(json_path):

    json_data = get_json_data(json_path)

    with ProcessPoolExecutor() as executor:
        
        futures = {executor.submit(process_corpus, json_object): json_object for json_object in json_data}

        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Elapsed time: {time.time() - start:.2f} seconds")
            except Exception as e:
                print(f"Task generated an exception: {e}")

    print(f"Total elapsed time: {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    main()