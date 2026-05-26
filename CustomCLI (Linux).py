import os
from shlex import split
from socket import gethostname

cli_loop = True

def tokenizer(user_input):
  input_str= user_input
  inside_single_quotes=False
  inside_double_quotes=False
  tokens=["<", ">", "|", " ", "'", '"']
  input_list=[]
  current_word=""
  double_operators=[">>", "<<", "||", "&&"]

  i=0
  while i < len(input_str):
    current = input_str[i]
    if i+1 < len(input_str):
      next_str = input_str[i+1]
    else : next_str=""

    if input_str[i] not in tokens:
      current_word+=input_str[i]
      i+=1

    elif input_str[i] == " ":
      if inside_single_quotes or inside_double_quotes:
        current_word+=input_str[i]
        i+=1
      elif current_word:
        input_list.append(current_word)
        current_word=""
        i+=1
      else:i+=1

    elif input_str[i] == "'" and not inside_double_quotes:
      inside_single_quotes=not inside_single_quotes
      i+=1

    elif input_str[i] == '"' and not inside_single_quotes:
      inside_double_quotes=not inside_double_quotes
      i+=1

    else :
      if current+next_str in double_operators:
        operator=current+next_str
        input_list.append(current_word)
        current_word=""
        input_list.append(operator)
        i+=2
        continue
      if current_word:
        input_list.append(current_word)
      input_list.append(input_str[i])
      current_word=""
      i+=1

  if current_word!="":
    input_list.append(current_word)
  if inside_single_quotes or inside_double_quotes:
    print("Invalid Syntax")
    return []
  return input_list

def split_pipeline(command, arguments):
    commands=[]
    current_command=[]
    full_command = [command] + arguments
    for item in full_command:
        if item == "|":
            commands.append(current_command)
            current_command=[]
        else:
            current_command.append(item)
    commands.append(current_command)
    return commands

def split_redirects(full_command):
    i=0
    input_file=None
    output_file=None
    clean_com_args=[]
    while i<len(full_command):
        if full_command[i]=="<":
            input_file=full_command[i+1]
            i+=2
        elif full_command[i]==">":
            output_file=full_command[i+1]
            i+=2
        else:
            clean_com_args.append(full_command[i])
            i+=1
    return (clean_com_args, input_file, output_file)

def run_externals(command, arguments):
    full_command = [command] + arguments
    clean_com_args, input_file, output_file = split_redirects(full_command)
    pid = os.fork()
    if pid == 0 :
        if input_file:
            fd=os.open(input_file, os.O_RDONLY)
            os.dup2(fd,0)
        if output_file:
            fd=os.open(output_file, os.O_WRONLY|os.O_CREAT|os.O_TRUNC, mode=0o777)
            os.dup2(fd,1)
        if clean_com_args==[]:
            clean_com_args=full_command
        os.execvp(clean_com_args[0], clean_com_args)
    else:
        os.wait()

def run_pipeline(command, arguments):
    commands = split_pipeline(command, arguments)
    prev_read=None
    pids=[]
    for i, index in enumerate(commands):

        if i != len(commands)-1:
            r,w = os.pipe()
        
        pid=os.fork()
        # Logic : if not last write, if not first read
        if pid==0:
            if prev_read != None:               
                os.dup2(prev_read, 0)
                os.close(prev_read)             

            if i<len(commands)-1:
                os.dup2(w, 1)
                os.close(r)
                os.close(w)
            
            clean_com_args, input_file, output_file = split_redirects(index)
            if input_file:
                fd=os.open(input_file, os.O_RDONLY)
                os.dup2(fd,0)
                os.close(fd)
            if output_file:
                fd=os.open(output_file, os.O_WRONLY|os.O_CREAT|os.O_TRUNC, mode=0o777)
                os.dup2(fd,1)
                os.close(fd)
            if clean_com_args==[]:
                    clean_com_args=index
            os.execvp(clean_com_args[0],clean_com_args)
        
        else:
            pids.append(pid)
            if prev_read != None:
                os.close(prev_read)
            if i<len(commands)-1:
                os.close(w)
                prev_read  = r

    for pid in pids:
        os.waitpid(pid, 0)

def getCwd():
    print(f"Current Directory : {os.getcwd()}")

def changeDirectory(arguments) :
    if arguments:
        try:
            os.chdir(arguments[0])
            getCwd()
        except :
            print("Invalid Path")

def getHelp() :
    print("Available Commands : ")

while cli_loop :
    cliprompt = f"\033[36m\033[1m{gethostname()}@CustomCLI\033[0m\033[33m\033[1m:~{os.getcwd()}$\033[0m "
    user_input = input(cliprompt)
    user_input = tokenizer(user_input)
    if not user_input:
        continue

    command = user_input[0]
    arguments = user_input[1:]

    match command :
        case ".exit":
            cli_loop = False
        case "getcwd":
            getCwd()
        case "cd":
            changeDirectory(arguments)
        case "help" | "?":
            getHelp()
        case _:
            if "|" in arguments:
                run_pipeline(command, arguments)
            else :  
                run_externals(command, arguments)
            