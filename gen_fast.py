#!/bin/python
import sys
from random import randint
from collections import defaultdict

variables = {}
subPaths = {'unaryTrue': {'ctr':0, 'paths':[]}, 'unaryFalse': {'ctr':0, 'paths':[]}}

def incDecisionTree(dList, idx):
    assert idx < len(dList)
    dList[idx] = str(int(dList[idx]) + 1)
    for i in range(idx + 1, len(dList)):
        dList[i] = '0'

# precomputes subtree structures based on the keys in subPaths
def crawlSubPaths():
    for var in subPaths.keys():
        printnum = 1;
        rs, rp = getValInc(var, [])
        subPaths[var]['paths'].append([rs, rp])
        rpl = rp[0:len(rp)-1].split(',')
        curPtr = len(rpl) - 1
        done = False
        while not done:
           incDecisionTree(rpl, curPtr)
           rs, rp = getValInc(var, [int(dec) for dec in rpl])
           rpl2 = rp[0:len(rp)-1].split(',')
           
           if (rpl[curPtr] == rpl2[curPtr]):
               subPaths[var]['paths'].append([rs, rp])
               printnum += 1
               rpl = rpl2
               curPtr = len(rpl) - 1
           else:
               curPtr -= 1
           if (curPtr == -1):
               done = True

# slightly modified version of getVal used to crawl subTrees           
def getValInc(var, decisionList):
    vLists = variables[var]
    retstring = ''
    retPath = ''
    if len(decisionList) == 0:
        index = 0
    else:
        index = decisionList[0] % len(vLists)
        del decisionList[0]
    retPath += str(index) + ','
    for value in vLists[index]:
        if value[0] == '[':
            if len(decisionList) == 0:
                index = 0
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
            rs, rP = getValInc(value, decisionList)
            retstring += rs
            retPath += rP
    return retstring, retPath


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
            if (value in subPaths.keys()):
               subPath = subPaths[value]['paths'].pop(0)
               subPaths[value]['paths'].append(subPath)
               subPaths[value]['ctr'] += 1
               rs = subPath[0]
               rP = subPath[1]
            else:
               rs, rP = getVal(value, decisionList)
            retstring += rs
            retPath += rP
    return retstring, retPath

def runTests():
    # TODO decide on / implement algorithm
    # TODO output a series of tests to a csv 

    if len(sys.argv) > 1:
        retstring, retPath = getVal('start', [int(decision) for decision in sys.argv[1].split(',')])
    else:
        retstring, retPath = getVal('start', [])
    print(retstring)
    if retPath[-1] == ',':
        retPath = retPath[:-1]
    print(retPath)

def readGrammar():
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

def main():
    readGrammar()
    crawlSubPaths()
    runTests()

main()
