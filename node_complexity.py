#!/bin/python
import sys
from random import randint

variables = {}
val_list = {}

def getVal(var):
    if (var in val_list):
      return val_list[var]
    vLists = variables[var]
    paths = 0
    for index in xrange(0,len(vLists)):
      vpaths = 1
      opt_path = 0
      
      #if (var == 'terDigitZero'):
      #  print (vLists)  
      #  print(vLists[index])

      for value in vLists[index]:
         if value[0] == '[':
            value = value[1:len(value) - 1]
            opt_path += 1
         if value[0] == '"':
            vpaths *= 1
         else:
            vpaths *= getVal(value)
         vpaths += opt_path
      paths += vpaths
    
    # compute number of paths per node
    if (var not in val_list):
      val_list[var] = paths
      print (var + ": " + str(paths))
    return paths


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
        getVal('start')
    else:
        getVal('start')

main()
