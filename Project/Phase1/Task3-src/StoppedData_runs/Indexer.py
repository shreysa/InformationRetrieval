import GeneralLib as GL
from pip._vendor.distlib.compat import raw_input

class Indexer:
    
    def __init__(self, indexPath, corpus):
        #json file where index will be stored
        self._indexPath = indexPath
        #Folder where corpus is stored
        self._corpusPath = corpus
        self._index = dict()
        
    #Function to build index    
    def build_index(self , choice):
        corpus = GL.getDataFiles(self._corpusPath)
        
        if(choice == 0):
            for file in corpus:
                self.index_without_positions(file)
        else:
            for file in corpus:
                self.index_with_positions(file)
        
        GL.dictToJson(self._indexPath, self._index)
    
    #Function builds index with term positions 
    def index_with_positions(self, file):
        with open(GL.getFilename(self._corpusPath, file) ,'r') as f:
            data = f.read().split(" ")
        
        docID = GL.getTitle(file)
        pos = 1
        for term in data:
            if term in self._index.keys():
                if docID in self._index[term].keys():
                    self._index[term][docID][0] += 1
                    self._index[term][docID][1].append(pos)
                else:
                    self._index[term].update({docID : [1 , [pos]]})
            else:
                self._index.update({term : {docID : [1 , [pos]]}})
            pos+=1
    
     
    #Function builds index without positions                    
    def index_without_positions(self, file):
        with open(GL.getFilename(self._corpusPath, file) ,'r') as f:
            data = f.read().split(" ")
        
        docID = GL.getTitle(file)
        for term in data:
            if term in self._index.keys():
                if docID in self._index[term].keys():
                    self._index[term][docID] += 1
                else:
                    self._index[term].update({docID : 1})
            else:
                self._index.update({term : {docID : 1}})        


if __name__ == "__main__" :
    
    indexFile = raw_input("Enter file where index will be stored. [.json file]:")
    corpus = raw_input("Enter the path for corpus to be indexed")
    indexer = Indexer(indexFile, corpus)
    
    choice = raw_input("Store term positions?")
    if (choice == 'Y' or choice == 'y'):
        indexer.build_index(1)
    else:
        indexer.build_index(0)      