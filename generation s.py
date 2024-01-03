import fire
import sys,os
import re
from typing import List
B_INST, E_INST              =   "[INST]", "[/INST]"
B_SYS, E_SYS                =   "<<SYS>>", "<</SYS>>"

SPECIAL_TAGS                =   [B_INST, E_INST, "<<SYS>>", "<</SYS>>"]
SPECIAL_TAGS_PRECHECKING    =   [B_INST, E_INST, "<<SYS>>", "<</SYS>>" , "\n"]
SPECIAL_TAGS_SQA            =   ["### Scenario:","### Question:","### Answer:"]

UNSAFE_ERROR        =   "Error: special tags are not allowed as part of the prompt."
NOTFOUND_ERROR      =   ("Error: The arrangement of 'Scenario','Question', and 'Answer' is violated!"
                        "Starting with '### Scenario:' and then ### Question/Answer/Q/A/...")

def main(
        path : str,
        output_path : str = None,
):
    assert  path is not None , "\n***\n\tInput path cannot be None, as information is needed for conversion\n***"
    if output_path is None:
        print( "\n----/ Warning, no output path is defined, so we will try to use the current folder of program execution for saving results /----")
    if os.path.isfile( path ):
        print( f"Working on the file {path}" )
        readandwrite( path , output_path )
    else:
        print( f"Working on the directory {path}" )
        for o in os.listdir(path):
            print( f"Start reading file {o} ...")
            readandwrite( [path , o ] , output_path)
def readandwrite( 
        file_path       : str | List[str],
        output_path     : str = None
                 ):
    try:
        file                                =   open( f"{file_path}" if type(file_path) is str else f"{file_path[0]}\\{file_path[1]}", "r" )
        reading : str                       =   file.read()
        splitter                            =   re.split( "### (?=Scenario|Question|Answer)" , reading)
        messages                            =   list()
        for t in splitter:
            if len(t) > 0:
                messages.append( { re.split( "(Scenario|Question|Answer):\n" , t )[1].strip()  : re.split( "(Scenario|Question|Answer):\n" , t )[2].strip().replace("\n"," ")  })
        
        is_scenario_available   :   bool    =   "Scenario" in set().union( *(t.keys() for t in messages) )
        output                  :   str     =   ""
        print("Converting ...")
        if is_scenario_available:
            for i,j in zip(messages[1::2],messages[2::2]):
                output += f"<s>{B_INST} {B_SYS} {messages[0]['Scenario']} {E_SYS} {i['Question'].strip()} {E_INST} {j['Answer'].strip()} </s>\n" 
        
        if output_path is None:
            output_path =   "\\".join( file_path.split('\\')[:-1] ) if type(file_path) is str else file_path[0]
        outputfile  =   output_path + "\\" + file_path.split('\\')[-1].split('.')[0] + " - converted.txt" if type(file_path) is str else \
                        output_path + "\\" + file_path[1].split('.')[0] + " - converted.txt"
        write       =   open( outputfile , "w")
        write.write( ''.join(output) )
        write.close()
        print( "Done")
    
    except FileNotFoundError as e:
        print( f"Something went wrong with {file_path}, File not found!" )
        print(e)

if __name__ == "__main__":
    fire.Fire(main)