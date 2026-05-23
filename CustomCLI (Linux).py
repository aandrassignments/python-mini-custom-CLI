import os
from shlex import split
from socket import gethostname

cli_loop = True

def tokenizer(command, arguments):
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
  
def externals(command, arguments):
  full_command = [command] + arguments
  pid = os.fork()
  if pid == 0:
    os.execvp(command, full_command)
  else:
    os.wait()

def advanced(command, arguments):
  commands=tokenizer(command, arguments)
  prev_read=None
  pids=[]
  for i, index in enumerate(commands):
    if i != len(commands)-1:
      r,w = os.pipe()

    pid=os.fork()
    #logic : if not last write, if not first read
    if pid == 0:
      if prev_read != None:
        os.dup2(prev_read, 0)
        os.close(prev_read)

      if i<len(commands)-1:
        os.dup2(w,1)
        os.close(r)
        os.close(w)

      os.execv(index[0],index)
    else:
      pids.append(pid)
      if prev_read != None:
        os.close(prev_read)
      if i<len(commands)-1:
        os.close(w)
        prev_read=r
    
    for pid in pids:
      os.waitpid(pid, 0)

  def getCwd():
    print(f"Current Directory : {os.getcwd()}")
  
  def changeDirectory(arguments):
    if arguments:
      try:
        os.chdir(arguments[0])
        getCwd()
      except:
        print("Invalid Path")
  
  def getHelp() :
    print("Available Commands : ")
  
  while cli_loop :
    cliprompt = f"\033[36m\033[1m{gethostname()}@CustomCLI\033[0m\033[33m\033[1m:~{os.getcwd()}$\033[0m"
    user_input = input(cliprompt)
    user_input = split(user_input)
    if not user_input:
      continue

    command = user_input[0]
    arguments = user_input[1:]

    match command :
      case ".exit":
        cli_loop=False

      case "getcwd":
        getCwd()

      case "cd" :
        changeDirectory(arguments)

      case "help" | "?":
        getHelp()

      case _:
        # externals(command, arguments)
        advanced(command, arguments)