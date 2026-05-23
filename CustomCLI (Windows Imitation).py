import subprocess
import os
from shlex import split
cli_loop=True

def externals(command, arguments):
  splitted_command = [command] + arguments
  full_command = " ".join(splitted_command)
  print(full_command)
  try :
    process = subprocess.Popen(full_command, shell=True)
    process.wait()
  except Exception:
    print("Unknown Error")

def getCwd():
  print(f"Current Directory : {os.getcwd()}")

def changeDirectory(arguments) :
  if arguments :
    try :
      os.chdir(arguments[0])
      print(f"Changed Directory to : {os.getcwd()}")
    except :
      print("invalid path")

def getHelp():
  print("Available Commands : \n.exit\ngetcwd\ncd\nhelp\nexternals(cmd syntaxes)")

while cli_loop :
  user_input = input("CustomCLI> ")
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
      externals(command, arguments)