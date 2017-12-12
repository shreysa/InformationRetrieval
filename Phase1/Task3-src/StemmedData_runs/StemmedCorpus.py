import GeneralLib as GL
from pip._vendor.distlib.compat import raw_input

class Indexer:
    
    def __init__(self):
        #File contianing the stemmed text 
        self._corpusFile = raw_input("Enter file containing stemmed text:[cacm_stem.txt]")
        #json File where stemmed index will be stored 
        self._indexPath = raw_input("Enter file where index will be stored. [.json file]:")
        #Corpus to be stored after generating single files for each document
        self._corpusPath = raw_input("Enter the path for folder where each document extracted from text file will be stored:")
        self._index = dict()
    
    
    #Function creates seperate docs and indexes them
    def createDocs(self):
        with open(self._corpusFile, 'r') as f:
            data = f.read().split('#') 
        
        ctr = 0
        for doc in data[1:]:
            ctr+=1
            document = list()
            docno = format(ctr, "04")
            docID = "CACM-" + docno
            
            document = self.getContent(doc.strip().split(" "))
            self.index_without_positions(document, docID)
            with open(GL.getFilename(self._corpusPath, (docID + ".txt")) , 'w') as f:
                f.write(doc.strip())
            print("Done with document " + docID)
        GL.dictToJson(self._indexPath, self._index)
        
    #Function to get content for each doc    
    def getContent(self, content):
        document = list()
        flag = 0  
        for line in content:
            if not ((line == "") or (line == "['") or (line == "']")):
                line = line.replace(r"\t" , " ").replace("\n" , " ")
                tokens = line.split(" ")
                for token in tokens:
                    if not (any((char.isalpha() or char.isdigit()) for char in token)):
                        continue
                    if(token == "pm") or (token == "am"):
                        flag = 1
                    document.append(token)
                if (flag == 1):
                    break;     
        return document
    
    #Function builds an index without term positions
    def index_without_positions(self, data, docID):

        for term in data:
            if term in self._index.keys():
                if docID in self._index[term].keys():
                    self._index[term][docID] += 1
                else:
                    self._index[term].update({docID : 1})
            else:
                self._index.update({term : {docID : 1}})   
      
if __name__ == "__main__" :
    indexer = Indexer()
    indexer.createDocs()
    