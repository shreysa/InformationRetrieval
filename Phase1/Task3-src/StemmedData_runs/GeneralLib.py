import json
import os

# Function to extract data from a .json file to a dictionary
def jsonToDict(fname):
    with open(fname) as f:
        data = json.load(f)
    return data
    
# Function to write dictionary to .json file
def dictToJson(fname, data):
    with open(fname , "w") as f:
        json.dump(data , f)

#Get the filename with the full path
def getFilename(path, filename):
    file = path + filename
    return file

#Get the name of the file without "." the extension    
def getTitle(filename):
    title = filename.split(".")
    return title[0]
  
#Get a list of all file names from the specified directory    
def getDataFiles(path):
    data_files = list()
    for root , dir ,files in os.walk(path):
        for file in files:
            data_files.append(file)
    return data_files

#Extract data from a txt file
def fileToList(fname):
    with open(fname, 'r') as f:
        data = f.read().split(r"\n")
    return data

#Get results from a txt file
def getResults(fname):
    with open(fname, 'r') as f:
        data = f.read().split("\n")
          
    results = dict()
    for line in data:
        line = line.strip()
        if line == "":
            continue
        tokens = line.split(" ")
        results.update({int(tokens[3]) : tokens[2]})
        
    return results

#Extracts Query ID from filename
def getQID(file):
    name = file.split("-Query")
    ID = name[1].split(".")
    return ID[0]