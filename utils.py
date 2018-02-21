import csv
from HSserver import *
import pickle
import requests as req
import json


def putUrl(url, data):
    headers={"content-type":"application/json"}
    
    r = req.put(url, data = data, headers = headers).text
    try:
        out = json.loads(r)
    except Exception:
        return r
    
    return out
    

def getUrl(url):
    r = req.get(url).text
    try:
        out = json.loads(r)
    except Exception:
        return r
    
    return out


def readCSV(filename, columns=[]):
    out = []
    
    singleColumn = type(columns)==int
    
    with open(filename+".csv", 'r') as f:
        reader= csv.reader(f)
        
        
        for row in reader:
            if columns==[]:
                toAppend = row
            else:
                if singleColumn:
                    toAppend = row[columns]
                else:
                    toAppend = [row[column] for column in columns]
            out.append(toAppend)
            
    return out

def writeCSV(filename, rows):
    with open(filename+".csv", 'w') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow([row])

def loadPickle(filename):
    with open(filename + ".pickle", 'r') as f:
        return pickle.load(f)

def savePickle(filename, var):
    with open(filename + ".pickle", 'w') as f:
        pickle.dump(var, f)

if __name__=="__main__":
    print ""
#    csv = readCSV("clientList", [2,3])