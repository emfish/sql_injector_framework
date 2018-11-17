#!/bin/python
import sys
import re
from random import randint
from collections import defaultdict


# WARNING: This script is turning into spaghetti
 
variables = {}	# Holds each variable defined in the grammar
indexCnt = {}	# Tracks the number of subPaths to explore for each child node 
subPaths = {}	# holds every possible decision combination that can be used at each node 
					#  up to length <sys.argv[1]>. These are popped off as they are explored
subPathCp = {} # Copy of subPaths, this is sloppy
nodeComp = {}  # Tracks the total subPaths per node. Not really being used atm (sloppy)
subPathSize=3  # Maximum depgth of tracked subTree (overwritten by sys.argv[1]
maxTests=10000    # Maximum number of tests to try
DEBUG_PRINT = False
VERBOSE_DEBUG_PRINT = False
GENERATE_OUTPUT = True

uniqueAttacks = [] # store all generated attacks (may be easier just to print them)
duplicateAttacks = {} # stores duplicate attacks (good for debugging a shitty path selection algorithm

def dPrint(instr):
    if (DEBUG_PRINT == True):
        print (instr)
def vdPrint(instr):
    if (VERBOSE_DEBUG_PRINT == True):
        print (instr)
def oPrint(instr):
    if (GENERATE_OUTPUT == True):
        print (instr)

def incDecisionTree(dList, idx):
    assert idx < len(dList)
    dList[idx] = str(int(dList[idx]) + 1)
    for i in range(idx + 1, len(dList)):
        dList[i] = '0'

# precomputes subtree structures based on the keys in subPaths
def crawlSubPaths(var):
    #for var in subPaths.keys():
        printnum = 1;
        rs, rp = getValInc(var, [])
        rpl = rp[0:len(rp)-1].split(',')[:subPathSize]
        rp = ','.join(rpl) + ','
        subPaths[var]['paths'].append(rp)
        subPathCp[var].append(rp)
        curPtr = len(rpl) - 1
        done = False
        while not done:
           incDecisionTree(rpl, curPtr)
           rs, rp = getValInc(var, [int(dec) for dec in rpl])
           rpl2 = rp[0:len(rp)-1].split(',')[:subPathSize]
           rp = ','.join(rpl2) + ','
           
           if (rpl[curPtr] == rpl2[curPtr]):
               subPaths[var]['paths'].append(rp)
               subPathCp[var].append(rp)
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
    global indexCnt
    vLists = variables[var]
    decisionString = ','.join(map(str, decisionList))
    retstring = ''
    retPath = ''
    pathCnt = 0
    if var in subPaths:
        if  len(subPaths[var]['paths']) > 0:
            if len(decisionList) == 0:
               rp = subPaths[var]['paths'].pop(0)
               decisionList = [int(d) for d in rp[0:len(rp)-1].split(',')]
            else:
               regPath = re.compile(decisionString + '*')
               regMatches = filter(regPath.match, subPaths[var]['paths'])
               if len(regMatches) > 0:
                  rp = regMatches[0]
                  subPaths[var]['paths'].remove(rp)
                  decisionList = [int(d) for d in rp[0:len(rp)-1].split(',')]
        pathCnt = len(subPaths[var]['paths'])     
            
              
    if len(decisionList) == 0:
        index = 0
        for i in range(1, len(indexCnt[var])):
           if (indexCnt[var][i] > indexCnt[var][index]):
               index = i
    else:
        index = decisionList[0] % len(vLists)
        del decisionList[0]
    retPath += str(index) + ','
    for value in vLists[index]:
        if value[0] == '[':
            if len(decisionList) == 0:
                idx = randint(0, 1)
            else:
                idx = decisionList[0] % 2
                del decisionList[0]
            retPath += str(idx) + ','
            if idx == 1:
                value = value[1:len(value) - 1]
            else:
                continue
        if value[0] == '"':
            retstring += value[1:len(value) - 1]
        else:
            #if (value in subPaths.keys()):
            #   subPath = subPaths[value]['paths'].pop(0)
            #   subPaths[value]['paths'].append(subPath)
            #   subPaths[value]['ctr'] += 1
            #   #print(value + "\t" + subPath[1] + "\t" + subPath[0])
            #   rs = subPath[0]
            #   rP = subPath[1]
            #else:
            rs, rP, pc = getVal(value, decisionList)
            
            retstring += rs
            retPath += rP
            pathCnt += pc
    indexCnt[var][index] = pathCnt
    totalPaths = sum(indexCnt[var])
    return retstring, retPath, totalPaths

def fillSelectionList(var, decisionList):
    vLists = variables[var]
    decisionString = ','.join(map(str, decisionList[:subPathSize])) + ','
    SPSelectionList = []

    assert (len(decisionList) != 0) 
    # this is so ugly it hurts
    for i in range(0, subPathSize):
       if decisionString in subPathCp[var]:
          break
       else: 
          decisionString = decisionString[0:len(decisionString)-1].rpartition(',')[0] + ','
    found = False
    for i in range(0, len(subPathCp[var])):
       if (subPathCp[var][i] == decisionString):
           found = True
           SPSelectionList.append(var + "__" + str(i))
    if found == False:
        print(var + " " + decisionString + " " + str(subPathCp[var]))
    assert(found == True)    

    index = decisionList[0] % len(vLists)
    del decisionList[0]
    for value in vLists[index]:
        if value[0] == '[':
            assert(len(decisionList) != 0)
            idx = decisionList[0] % 2
            del decisionList[0]
            if idx == 1:
                value = value[1:len(value) - 1]
            else:
                continue
        if value[0] != '"':
            spsl = fillSelectionList(value, decisionList)
            SPSelectionList.extend(spsl)
    return SPSelectionList


def nodeComplexity(var):
    if (var in nodeComp):
      return nodeComp[var]
    #if (var == 'unaryTrue' or  var == 'unaryFalse'):
    #  return 1
    vLists = variables[var]
    paths = 0
    for index in xrange(0,len(vLists)):
      vpaths = 1
      opt_path = 0
      
      #if (var == 'terDigitZero'):
      #  print (vLists)  
      #  print(vLists[index])

      for value in vLists[index]:
         opt_path = 0
         if value[0] == '[':
            value = value[1:len(value) - 1]
            opt_path += 1
         if value[0] == '"':
            vpaths *= 1
         else:
            vpaths *= nodeComplexity(value) + opt_path
         vpaths += opt_path
      paths += vpaths
    
    if (var not in subPaths):
      subPaths[var] = {'ctr':0, 'paths':[]}
      subPathCp[var] = []

    # compute number of paths per node
    if (var not in nodeComp):
      nodeComp[var] = paths
      vdPrint (var.ljust(25) + str(paths) )# + str(vLists))
    return paths

def runTests():

    # count the total number of subPaths to explore
    max_paths = 0
    for val in subPaths.keys():
       subPaths[val]['max'] = len(subPaths[val]['paths']) 
       max_paths += subPaths[val]['max']

    testNum = 0
    for i in range(0, maxTests):
        testNum += 1
        retstring, retPath, pathCnt = getVal('start', [])
        unexploredEdges = 0
  
        # Store Attacks (and duplicates to make sure the algorithm doesn't suck
        # should be able to remove this in final product
        if retstring not in uniqueAttacks:
           uniqueAttacks.append(retstring)
        elif retstring not in duplicateAttacks.keys():
           duplicateAttacks[retstring] = 0
           continue
        else:
           duplicateAttacks[retstring] += 1
           continue
           

        SPSelectionList = fillSelectionList('start', [int(d) for d in retPath[0:len(retPath)-1].split(',')])
        oPrint(str(i) +'\t'+ retstring +'\t'+ retPath +'\t'+ '\t'.join(map(str, SPSelectionList)))

        # check to see if every sub path has been explored
        for sp in subPaths.keys():
           unexploredEdges += len(subPaths[sp]['paths'])
        if unexploredEdges == 0:
           break

    dPrint ("Attacks Generated: " + str(len(uniqueAttacks)))
    dPrint ("unique(ish) duplicates: " + str(len(duplicateAttacks.keys())))  

    num_paths = 0
    for val in subPaths.keys():
        untested_paths = len(subPaths[val]['paths'])
        num_paths += subPaths[val]['max'] - untested_paths
        #print(val.ljust(25) + str((subPaths[val]['max']-untested_paths)) + "/" + str(subPaths[val]['max']).ljust(6))
    
    dPrint ("Executed " + str(testNum) + " tests: " )
    dPrint ("Tested " + str(num_paths) + " out of " + str(max_paths) + " paths: %.2f%%" % ((float(num_paths)/float(max_paths))*100))
   

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
                idxLists = []
                for value in valueList:
                    vList = []
                    idxLists.append(9999999999999999999)
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
                indexCnt[name] = idxLists

def main():
    if len(sys.argv) < 2:
       print ("USAGE: gen_fast.py <max_subTree_length>")
       return
    else:
       global subPathSize
       subPathSize = int(sys.argv[1])
    dPrint ("Reading Grammar")
    readGrammar()
    dPrint ("Calculating node complexity")
    nodeComplexity('start') 
    dPrint("Precomputing sub-paths")
    for var in subPaths.keys():
        crawlSubPaths(var)
    dPrint ("Generating tests")
    runTests()

main()
