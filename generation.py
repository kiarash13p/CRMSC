import fire
import sys

B_INST, E_INST              =   "[INST]", "[/INST]"
B_SYS, E_SYS                =   "<<SYS>>", "<</SYS>>"

SPECIAL_TAGS                =   [B_INST, E_INST, "<<SYS>>", "<</SYS>>"]
SPECIAL_TAGS_PRECHECKING    =   [B_INST, E_INST, "<<SYS>>", "<</SYS>>" , "\n"]
SPECIAL_TAGS_SQA            =   ["### Scenario:","### Question:","### Answer:"]
SPECIAL_TAGS_SUA            =   ["system","user","assistant"]

UNSAFE_ERROR        =   "Error: special tags are not allowed as part of the prompt."
NOTFOUND_ERROR      =   ("Error: The arrangement of 'Scenario','Question', and 'Answer' is violated!"
                        "Starting with '### Scenario:' and then ### Question/Answer/Q/A/...")

def main(
        file_path : str,
        output_path : str = None
):
    try:
        file    =   open( file_path , "r" )
        #reading : str       =   file.read()
        dialog  =   list()
        message =   { "role" : "" , "content" : "" }
        while True:
            line    =   file.readline()
            if not line:
                # Appending last Message
                if message['role'] != "":
                    message['content'] = message['content'].strip('\n')
                    print( f"Adding {message}\n")
                    dialog.append( message )
                break
            assert not any([ tag in line.strip() for tag in SPECIAL_TAGS_PRECHECKING]) , UNSAFE_ERROR + f" -> {line.strip()}"
            mode        =   SPECIAL_TAGS_SQA.index(line.strip()) if SPECIAL_TAGS_SQA.count(line.strip()) else -1
            match mode:
                case -1:
                    message['content'] += line.strip()
                case 0 | 1 | 2:
                    if message['role'] != "":
                        
                        message['content'] = message['content'].strip('\n')
                        print( f"Adding {message}\n")
                        dialog.append( message )
                        message =   { "role" : "" , "content" : "" }
                    message['role']    =   SPECIAL_TAGS_SUA[mode]
        print( "Information received is as follows:\n")    
        for d in dialog: print( 8*"*" + f"\nRole: {d['role']}" + f"\nContent: {d['content']}")
        file.close()

        print("Converting ...")

        #inherit this part from meta
        if dialog[0]["role"] == "system":
                dialog = [
                    {
                        "role": dialog[1]["role"],
                        "content": B_SYS
                        + dialog[0]["content"]
                        + E_SYS
                        + dialog[1]["content"],
                    }
                ] + dialog[2:]
        # output      =   f"<s>{B_INST} {B_SYS}{ list(filter( lambda y: y['role'] == SPECIAL_TAGS_SUA[0] , dialog ))[0]['content'] }{E_SYS}"
        # for message in dialog:
        #     output += 
        output =  [f"<s>{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} </s>" for prompt, answer in zip( dialog[::2],dialog[1::2] )]
        print( "\n\nWriting data ... ")
        write       =   open( output_path + ".txt" if output_path else file_path + " - converted.txt" , "w")
        write.write( ''.join(output) )
        write.close()
        print( "done")
    except FileNotFoundError:
        print( f"Something went wrong with {file_path}, File not found!" )

if __name__ == "__main__":
    fire.Fire(main)