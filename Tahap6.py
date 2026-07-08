import os
from socket import gethostname

def tokenizer(user_input):
  input_str= user_input

  inside_single_quotes=False
  inside_double_quotes=False

  tokens=["<", ">", "|", " ", "'", '"']

  input_list=[]

  current_word=[]

  double_operators=[">>", "<<", "||", "&&"]

  i=0
  while i < len(input_str):
    current = input_str[i]

    if i+1 < len(input_str):
      next_str = input_str[i+1]
    else : next_str=""

    if current not in tokens:
      current_word.append(current)
      i+=1

    elif current == " ":

      if inside_single_quotes or inside_double_quotes:
        current_word.append(current)
        i+=1

      elif current_word:
        input_list.append("".join(current_word))
        current_word=[]
        i+=1

      else:i+=1

    elif current == "'" and not inside_double_quotes:
      inside_single_quotes=not inside_single_quotes
      i+=1

    elif current == '"' and not inside_single_quotes:
      inside_double_quotes=not inside_double_quotes
      i+=1

    else :

      if current+next_str in double_operators:
        operator=current+next_str

        if current_word:
          input_list.append("".join(current_word))
        current_word=[]

        input_list.append(operator)
        i+=2
        continue
      
      if current_word:
        input_list.append("".join(current_word))

      input_list.append(current)
      current_word=[]
      i+=1

  if current_word!=[]:
    input_list.append("".join(current_word))

  if inside_single_quotes or inside_double_quotes:
    print("Invalid Syntax")
    return []
  # print(input_list)
  return input_list

def split_pipeline(command, arguments):
    commands=[]
    current_command=[]
    full_command= [command] + arguments
    for item in full_command:
      if item=="|": #note : might break if | is the last
        if not current_command:
          print("Invalid Syntax")
          return None
        commands.append(current_command)
        current_command=[]
      else:
        current_command.append(item)
    if not current_command:
      print("Invalid Syntax")
      return None
    commands.append(current_command)
    return commands

def split_redirects(full_command):
  i=0
  input_file=None
  output_file=None
  output_mode=None
  clean_com_args=[]
  while i<len(full_command):
    if full_command[i]=="<":
      if i+1>=len(full_command):
        print("Invalid Syntax")
        return None
      input_file=full_command[i+1]
      i+=2
    elif full_command[i]==">":
      if i+1>=len(full_command):
        print("Invalid Syntax")
        return None
      output_file=full_command[i+1]
      output_mode="truncate"
      i+=2
    elif full_command[i]==">>":
      if i+1>=len(full_command):
        print("Invalid Syntax")
        return None
      output_file=full_command[i+1]
      output_mode="append"
      i+=2
    else:
      clean_com_args.append(full_command[i])
      i+=1
  return (clean_com_args, input_file, output_file, output_mode)

def run_externals(command, arguments):
  full_command = [command] + arguments
  split_results = split_redirects(full_command)
  if split_results is None :
    return
  clean_com_args, input_file, output_file, output_mode = split_results
  pid=os.fork()
  if pid==0:
    try :
      if input_file:
        fd=os.open(input_file, os.O_RDONLY)
        os.dup2(fd,0)
        os.close(fd)
      if output_file:
        if output_mode=="truncate":
          flags = os.O_WRONLY|os.O_CREAT|os.O_TRUNC
        else :
          flags = os.O_WRONLY|os.O_CREAT|os.O_APPEND
        fd=os.open(output_file, flags, mode=0o777)
        os.dup2(fd,1)
        os.close(fd)
      if clean_com_args==[]:
        clean_com_args=full_command
      try :
        os.execvp(clean_com_args[0], clean_com_args)
      except FileNotFoundError:
        print("Command Not Found")
        os._exit(1)

    # except FileNotFoundError:
    #   print("Command Not Found")
    #   os._exit(1)
    except OSError as err:
      print(f"Error : {err.strerror}")
      os._exit(1)
  
  else:
    os.waitpid(pid, 0)

def run_pipeline(command, arguments):
  commands = split_pipeline(command, arguments)
  if commands is None:
    return
  prev_read=None
  pids=[]
  for i, cmd in enumerate(commands):

    if i != len(commands)-1:
      r,w = os.pipe()

    pid=os.fork()
    #logic : if not last, write. if not first, read
    if pid==0:
      try:
        if prev_read != None:
          os.dup2(prev_read, 0)
          os.close(prev_read)

        if i<len(commands)-1:
          os.dup2(w, 1)
          os.close(r)
          os.close(w)

        split_results = split_redirects(cmd)
        if split_results is None :
          os._exit(1)
        clean_com_args, input_file, output_file, output_mode = split_results
        if input_file:
          fd=os.open(input_file, os.O_RDONLY)
          os.dup2(fd,0)
          os.close(fd)
        if output_file:
          if output_mode=="truncate":
            flags = os.O_WRONLY|os.O_CREAT|os.O_TRUNC
          else :
            flags = os.O_WRONLY|os.O_CREAT|os.O_APPEND
          fd=os.open(output_file, flags, mode=0o777)
          os.dup2(fd,1)
          os.close(fd)
        if not clean_com_args: #idk previously it's clean_com_args==[] which is more or less the same?
          clean_com_args=cmd
        try :
          os.execvp(clean_com_args[0], clean_com_args)
        except FileNotFoundError:
          print("Command Not Found")
          os._exit(1)
      # except FileNotFoundError:
      #   print("Command Not Found")
      #   os._exit(1)
      except OSError as err:
        print(f"Error : {err.strerror}")
        os._exit(1)

    else:
      pids.append(pid)
      if prev_read != None:
        os.close(prev_read)
      if i<len(commands)-1:
        os.close(w)
        prev_read=r

  for pid in pids:
    os.waitpid(pid,0)

def getCwd():
  print (f"Current Directory : {os.getcwd()}")

def changeDirectory(arguments):
  if arguments:
    try :
      os.chdir(arguments[0])
      getCwd()
    except OSError:
      print("Invalid Path")

cli_loop = True
while cli_loop :
  cliprompt = f"\033[36m\033[1m{gethostname()}@CustomCLI\033[0m\033[33m\033[1m:~{os.getcwd()}$\033[0m "

  user_input = input(cliprompt)
  user_input = tokenizer(user_input)
  if not user_input:
    continue

  command = user_input[0]
  arguments = user_input[1:] 

  match command.lower() :
    case ".exit":
      cli_loop = False
    case "getcwd" | "pwd":
      getCwd()
    case "cd":
      changeDirectory(arguments)
    case "help" | "?":
      print("help | ? picked")  
    case _:
      if "|" in arguments:
        run_pipeline(command, arguments)
      else:
        run_externals(command, arguments)