import os
from socket import gethostname

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

        if current_word:
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
  print(input_list)
  return input_list

cli_loop = True
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
      print("getcwd picked")
    case "cd":
      print("cd picked")    
    case "help" | "?":
      print("help | ? picked")     
    case _:
      print("externals")
