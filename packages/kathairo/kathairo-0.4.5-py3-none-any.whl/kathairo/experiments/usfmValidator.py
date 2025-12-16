from usfm_grammar import USFMParser
from lxml import etree

def print_errors_for_usx(file_path:str):
    with open(file_path, 'r', encoding='utf-8') as usx_file:
        usx_str = usx_file.read()
        usx_obj = etree.fromstring(bytes(usx_str, encoding='utf8'))
        my_parser = USFMParser(from_usx=usx_obj)
        return my_parser

def print_errors_for_usfm(file_path:str):    
    input_usfm_str = open(file_path,"r", encoding='utf8').read()
    my_parser = USFMParser(input_usfm_str)
    return my_parser

import os

#directory_path = "./resources/bsb_usx/release/USX_1/"
directory_path = "./resources/ru_rsb/"
file_list = os.listdir(directory_path)

for file in file_list:
    #my_parser = print_errors_for_usx(directory_path+file)
    my_parser = print_errors_for_usfm(directory_path+file)
    
    errors = my_parser.errors
    if(errors is not None):
        for error in errors:
            #print(error)

            with open('output_russian.txt', 'a') as f:
                f.write(str(error))   
                f.write("\n")    


#--------------------------------------------

#test_xml_file = "./resources/bsb_usx/release/USX_1/1CH.usx"
#test_usfm_file = "./resources/bsb_usfm/50EPHBSB.SFM"

#my_parser = print_errors_for_usx(test_xml_file)
#my_parser = print_errors_for_usfm(test_usfm_file)

#errors = my_parser.errors
#for error in errors:
#    print(error)

#--------------------------------------------

# print(my_parser.to_usj())
# print(my_parser.to_list())
