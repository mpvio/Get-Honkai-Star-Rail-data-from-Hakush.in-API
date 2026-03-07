import re

regex: str = r"<.*?>|#([0-9])\[[a-z0-9]+\](%?)|\\n"

def parseDesc(desc: str, param1: list, paramMax: list = None, paramWhale: list = None) -> str:
    if desc is None or desc == "": return desc
    splitDesc = re.split(regex, desc)
    finalTxt = ""
    for i in range(len(splitDesc)):
        txt: str = splitDesc[i]
        if txt is None or txt in ["", "%"]: continue
        elif txt.isdigit(): 
            num = int(txt) - 1
            try: percent = splitDesc[i+1] == "%"
            except: percent = False
            finalTxt += getValue(num, percent, param1, paramMax, paramWhale)
        else: finalTxt += txt
    return finalTxt

def getValue(index: int, percent: bool, param1: list, paramMax: list = None, paramWhale: list = None) -> str:
    values = []
    # param 1
    try: values.append(formatNumber(param1[index], percent))
    except: return ""
    # need max param?
    if paramMax == None or paramMax[index] == param1[index]: return valuesToString(values, percent)
    else: values.append(formatNumber(paramMax[index], percent))
    # need whale param?
    if paramWhale == None: return valuesToString(values, percent)
    else: values.append(formatNumber(paramWhale[index], percent))
    # output as string
    return valuesToString(values, percent)

def valuesToString(values: list, percent: bool) -> str:
    symbol = "%" if percent else ""
    answer = f"{values[0]}" if len(values) == 1 else "["+"|".join(str(v) for v in values)+"]"
    return answer + symbol

def formatNumber(num: int|float, percent: bool):
    if percent: num *= 100
    num = round(num, 1)
    if num.is_integer(): return int(num)
    else: return num