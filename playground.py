def tokenizer(user_input):
  input_str= user_input

  #buat cek ada di dalam tanda petik(dua) atau nggak soalnya kl kayak path kan
  #kadang ada yang ada spasinya jadi nggak bisa di split kayak biasa
  inside_single_quotes=False
  inside_double_quotes=False

  #karakter yang punya kegunaan khusus
  tokens=["<", ">", "|", " ", "'", '"']

  #list hasil tokenize
  input_list=[]

  #tempat sementara buat naro kata bisa dioptimize nanti pake list aja biar gk bikin string baru terus
  current_word=[]

  #token khusus yang butuh di cek index setelahnya
  double_operators=[">>", "<<", "||", "&&"]

  i=0
  while i < len(input_str):
    current = input_str[i]

    #look ahead buat cek misalnya untuk >> atau <<
    if i+1 < len(input_str):
      next_str = input_str[i+1]
    else : next_str=""

    #cek kl bukan token berarti tambahin ke kata yang sekarang
    #misal sekarang te terus ketemu s, gabung jadi tes
    if current not in tokens:
      current_word.append(current)
      i+=1

    #buat ngehandle spasi
    elif current == " ":

      #jadi spasinya gk jadi pemisah kl di dalam tanda petik(dua)
      if inside_single_quotes or inside_double_quotes:
        current_word.append(current)
        i+=1

      #spasi diluar tanda petik(dua) jadi akhir kata
      elif current_word:
        input_list.append("".join(current_word))
        current_word=[]
        i+=1

      #kl spasi biasa jadi pemisah
      else:i+=1

    #toggle petik, cuekin kl dalam petik(dua)
    elif current == "'" and not inside_double_quotes:
      inside_single_quotes=not inside_single_quotes
      i+=1

    #sama aja tapi buat petik dua
    elif current == '"' and not inside_single_quotes:
      inside_double_quotes=not inside_double_quotes
      i+=1

    #buat ngehandle token2 tadi diawal kayak (< | > dll)
    else :

      #cek buat character yg double (<<, ||, >>)
      if current+next_str in double_operators:
        operator=current+next_str

        #simpen word/kata sebelum operatornya
        if current_word:
          input_list.append("".join(current_word))
        current_word=[]

        #simpen operatornya
        input_list.append(operator)
        i+=2
        continue
      
      #save kata sebelum operator yang single chara
      if current_word:
        input_list.append("".join(current_word))

      #simpen operatornya
      input_list.append(current)
      current_word=[]
      i+=1

  #tambahin kata terakhir ke list
  if current_word!=[]:
    input_list.append("".join(current_word))

  #kl petik(dua) gk ketutup tolak kasih error invalid syntax
  if inside_single_quotes or inside_double_quotes:
    print("Invalid Syntax")
    return []
  print(input_list)
  return input_list

test_str = '>> file.txt'
tokenizer(test_str)