import GeneralLib as GL
from pip._vendor.distlib.compat import raw_input

#Function creates a dictionary of relevance data and stores in the json file.
def getRelevanceData():
    with open(raw_input("Enter the file containing relevance info:"),"r") as f:
        data = f.read().split("\n")

    relevanceInfo = dict()    
    for line in data:
        line = line.strip()
        tokens = line.split(" ")
        if tokens[0] in relevanceInfo.keys():
            relevanceInfo[tokens[0]].append(tokens[2])
        else:
            relevanceInfo.update({tokens[0] : [tokens[2]]})
    
    return relevanceInfo


if __name__ == "__main__" :
    GL.dictToJson(raw_input("Enter json file relevance info will be stored:"), getRelevanceData())