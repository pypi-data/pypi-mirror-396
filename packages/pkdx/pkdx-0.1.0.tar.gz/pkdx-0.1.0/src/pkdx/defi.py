import sys, json, os, shutil, random
from term_image.image.block import BlockImage
from deep_translator import GoogleTranslator
import importlib.resources as res
##--------General----Functions------
def LDex(dex):
    if not os.path.exists(dex):
        return []
    with open(dex, "r") as f:
        return json.load(f)
def s(mode,name, dex):
    dex = LDex(dex)
    if str(mode) == "0":
        for i in dex:
            if i["name"]["english"].lower() == name.lower():
                return i
        return None
    elif str(mode == "1"):
        for i in dex:
            if int(i["id"]) == int(name):
                return i
        return None
def dictSep(search):
    typ = []
    for i in search:
        typ.append(i)
    return ', '.join(typ)
def find(mode,name,dex,img):
    pkmn = s(mode,name,dex)
    if pkmn != None:
        typ = dictSep((pkmn["type"]))
        print("------------"+pkmn["name"]["english"]+"------------")
        print("Also known as")
        print(str(pkmn["name"]["japanese"])+", "+str(pkmn["name"]["chinese"]+", and "+ str(pkmn["name"]["french"])))
        print("Type: "+typ)
        print("ID: "+str(pkmn["id"]))
        print("------Stats------")
        print("HP: "+str(pkmn["base"]["HP"]))
        print("Attack: "+str(pkmn["base"]["Attack"]))
        print("Defense: "+str(pkmn["base"]["Defense"]))
        print("Special Attack: "+str(pkmn["base"]["Sp. Attack"]))
        print("Special Defense: "+str(pkmn["base"]["Sp. Defense"]))
        print("Speed: "+str(pkmn["base"]["Speed"]))
        print("Height: "+str(pkmn["profile"]["height"]))
        print("Weight: "+str(pkmn["profile"]["weight"]))
        ##Add gender percentage bar later
        print("--------About-----")
        print("The "+str(pkmn["species"]))
        print(pkmn["description"])
        
    else:
        print("Not Found")
def imgSearch(name,dex,img):
    pkmn = s(0,name,dex)
    img = os.path.join(img,(str(pkmn["id"])+".png"))
    image = BlockImage.from_file(img)
    print(image)

##--------Make----Functions---------
def mkImage(path,name,dex,img):
    try:
        pkmn = s(0,name,dex)
        imag = os.path.join(img,(str(pkmn["id"])+".png"))
        shutil.copy2(path, imag)
        imgSearch(name,dex,img)
    except FileNotFoundError:
        print("The source file was not found.")
    except PermissionError:
        print("Permission denied to access source or destination.")
    except Exception as e:
        print(f"An error occurred: {e}")
def mkpkmn(dex,t,v,g):
    path = dex
    dex = LDex(dex)
    name = input("Name: ")
    typ = input("The first type: ")
    typ2 = input("The second type(optional): ")
    print("Description")
    species = input("The ")
    abt = input("More info: ")
    iD = (int(dex[-1]["id"])+1)
    if t == True:
        japanese = GoogleTranslator(source='auto', target='ja').translate(name)
        chinese = GoogleTranslator(source='auto', target='zh-CN').translate(name)
        french = GoogleTranslator(source='auto', target='fr').translate(name)
    elif t == False and v == True:
        japanese = input("Japanese name: ")
        chinese = input("Chinese name: ")
        french = input("French name: ")
    else:
        japanese = ""
        chinese = ""
        french = ""
    if v == True and g == False:
        hp = input("HP: ")
        hp = int(hp)
        atk = input("ATK: ")
        atk = int(atk)
        DEF = input("DEF: ")
        DEF = int(DEF)
        SpAtk = input("SP.ATK: ")
        SpAtk = int(SpAtk)
        SpDef = input("SP.DEF: ")
        SpDef = int(SpDef)
        spd = input("SPD: ")
        spd = int(spd)
        height = input("Height: ")
        weight = input("Weight: ")
        egg = input("Egg data: ")
        egg2= input("Additional egg data: ")
        gender = input("Gender Ratio(50:50): ")
        if gender == "":
            gender = "Genderless"
    elif g == True:
        hp = random.randint(10,255)
        atk = random.randint(5,165)
        DEF = random.randint(5,230)
        SpAtk = random.randint(15,140)
        SpDef = random.randint(40,230)
        spd=random.randint(5,160)
        height=(str(random.randint(0,100))+" m")
        weight=(str(round(random.uniform(0.0,999.9),1))+" kg")
        egg = ""
        egg2=""
        genstat = round(random.uniform(0.0, 100.0), 1)
        gen2stat= 100-genstat
        gender = (str(genstat)+":"+str(gen2stat))
    else:
        hp = 0
        atk =0
        DEF = 0
        SpAtk =0
        SpDef = 0
        spd=0
        height=""
        weight=""
        egg = ""
        egg2=""
        gender = "Genderless"
        
    pk = {
    "id": iD,
    "name": {
      "english": name,
      "japanese": japanese,
      "chinese": chinese,
      "french": french
    },
    "type": [typ, typ2],
    "base": {
      "HP": hp,
      "Attack": atk,
      "Defense": DEF,
      "Sp. Attack": SpAtk,
      "Sp. Defense": SpDef,
      "Speed": spd
    },
    "species": species,
    "description": abt,
    "evolution": {},
    "profile": {
      "height": height,
      "weight": weight,
      "egg": [egg,egg2],
      "ability": [
        []
      ],
      "gender": gender
    },
    "image": {
      "sprite": "",
      "thumbnail": "",
      "hires": ""
    }}
    dex.append(pk)
    with open(path, 'w') as file:
        json.dump(dex, file, indent=4,ensure_ascii=False)
