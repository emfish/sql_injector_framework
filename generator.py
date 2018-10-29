#!/bin/python
import sys
from random import randint

variables = {}

def getVal(var, decisionList):
    vLists = variables[var]
    retstring = ''
    retPath = ''
    if len(decisionList) == 0:
        index = randint(0, len(vLists) - 1)
    else:
        index = decisionList[0] % len(vLists)
        del decisionList[0]
    retPath += str(index) + ','
    for value in vLists[index]:
        if value[0] == '[':
            if len(decisionList) == 0:
                index = randint(0, 1)
            else:
                index = decisionList[0] % 2
                del decisionList[0]
            retPath += str(index) + ','
            if index == 1:
                value = value[1:len(value) - 1]
            else:
                continue
        if value[0] == '"':
            retstring += value[1:len(value) - 1]
        else:
            rs, rP = getVal(value, decisionList)
            retstring += rs
            retPath += rP
    return retstring, retPath


def main():
    with open('grammar.txt') as grammarfile:
        for line in grammarfile:
            if len(line) > 0 and line[0] == '#':
                continue
            if '=' in line:
                name = line[:line.index('=')].strip()
                values = line[line.index('=') + 1:].strip()
                valueList = []
                inQuotes = False
                i = 0
                j = 0
                while i < len(values):
                    if values[i] == '\\':
                        i += 2
                    elif values[i] == '"':
                        inQuotes = not inQuotes
                        i += 1
                    elif not inQuotes and (values[i] == '|' or values[i] == ';'):
                        valueList.append(values[j:i])
                        i += 1
                        j = i
                    else:
                        i += 1
                vLists = []
                for value in valueList:
                    vList = []
                    inQuotes = False
                    i = 0
                    j = 0
                    while i < len(value):
                        if i == len(value) - 1:
                            vList.append(value[j:].strip())
                            break
                        elif value[i] == '\\':
                            i += 2
                        elif value[i] == '"':
                            inQuotes = not inQuotes
                            i += 1
                        elif not inQuotes and value[i] == ',':
                            vList.append(value[j:i].strip())
                            i += 1
                            j = i
                        else:
                            i += 1
                    vLists.append(vList)
                variables[name] = vLists
    if len(sys.argv) > 1:
        retstring, retPath = getVal('start', [int(decision) for decision in sys.argv[1].split(',')])
    else:
        retstring, retPath = getVal('start', [])
    print(retstring)
    if retPath[-1] == ',':
        retPath = retPath[:-1]
    print(retPath)

main()
