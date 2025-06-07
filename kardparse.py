#这个模块提供kards卡组码校验-解析功能
import re

def split_string(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

def codeCheck(code):
    regexrule = "^%%[1-9]{2}\|(?:(?:[0-9a-zA-Z]{2})*;){3}(?:[0-9a-zA-Z]{2})*$"
    result = re.match(regexrule, code, flags=0)
    if result != None:
        return True
    else:
        return False

def codeAnalyze(code):
    deck = {
        "major":"",
        "minor":"",
        "1card":[],
        "2card":[],
        "3card":[],
        "4card":[]
            }
    split1 = code.split("|")
    country = split1[0]
    cards = split1[1]
    deck["major"] = country[2]
    deck["minor"] = country[3]
    split2 = cards.split(";")
    deck["1card"] = split_string(split2[0], 2)
    deck["2card"] = split_string(split2[1], 2)
    deck["3card"] = split_string(split2[2], 2)
    deck["4card"] = split_string(split2[3], 2)
    return deck

def deckList(deck):
    decklist = []
    decklist+=deck["4card"]*4
    decklist+=deck["3card"]*3
    decklist+=deck["2card"]*2
    decklist+=deck["1card"]
    decklist.sort()
    return decklist

def countryList(deck):
    countryList = []
    countryList.append(deck["major"])
    countryList.append(deck["minor"])
    return countryList