import GeneralLib as GL
import math
from collections import OrderedDict
from pip._vendor.distlib.compat import raw_input

class BM25Search:
   
    def __init__(self, indexPath, corpusPath, queryPath):
        #Dictionary to store the index. 
        self._index = GL.jsonToDict(indexPath)
        #Path where all files are stored
        self._corpusPath = corpusPath
        #List of all the files in the corpus.
        self._corpus = GL.getDataFiles(corpusPath)
        #Dictionary to store the document frequency table.
        self._dftable = GL.jsonToDict(raw_input("Enter json file where document frequencies are stored.[dTable.json]:"))
        #Dictionary to store all the queries.
        self._queries = GL.jsonToDict(queryPath)
        #average Document Length
        self._avDL = 0
        #System Name (default corpus case folded and striped of punctuation)
        self._systemName = "BM25_CF_PUNC"
    
    #Function to run all the queries one by one.
    def search(self):
        resultsPath = raw_input("Enter the path of folder where results will be stored.")
        self._avDL = self.avgDocLength()

        for qID in self._queries.keys():
            print("Results for Query " + str(qID) + ": \n")
            file = GL.getFilename(resultsPath, "BM25Search-Query" + qID + ".txt")
            results = self.searchCorpus(self._queries[qID])
            
            rank = 1
            resultData = ""
            for doc in results.keys():
                if rank > 100 :
                    break
                res = str(qID) + " QO " + doc + " " + str(rank) + " " + str(results[doc]) + " " + self._systemName+ "\n" 
                print(res)
                resultData += res
                rank+=1
                
            with open(file , 'w') as f:
                f.write(resultData)
            print("Done with Query " + str(qID))
            
    def searchCorpus(self,query):
        #Tokenize the query
        terms = query.split(" ")
        #Dictionary to store the query terms and their query frequency.
        queryTerms = dict()
        searchResults = dict()
        
        for term in terms:
            if term in queryTerms.keys():
                qFreq = queryTerms[term]
                queryTerms.update({term : (qFreq + 1)})
            else:
                queryTerms.update({term : 1})
                
        #Get all the relevant documents for the given query
        relDocs = BM25Search.getRelevantDocs(self, query)
        
        #Calculate BM25 score for each document in the relevant Documents list
        for document in relDocs:
            #Get document length for the current document
            with open(GL.getFilename(self._corpusPath, document + ".txt") ,'r') as f:
                data = f.read().split(" ")
            dl = len(data)
            
            #Initialize the document score to 0
            docScore = 0
            #Calculate the BM25 score for each term and add them to the docScore
            for term in queryTerms.keys():
                if term in self._index.keys():
                    if document in self._index[term].keys():
                        f = self._index[term][document]  #Term Frequency in the document
                        qf = queryTerms[term]               #Term Frequency in the query
                        n = self._dftable[term][1]       #Document Frequency of the term
                        K = self.calc_K(dl) 
                    
                        #Calculate the BM25 score for each term with the current document
                        docScore += self.bm25TermScore(f, qf, n, K)
            #Update the result dictionary.
            searchResults.update({document : docScore})
        
        #Return an ordered dictionary according to score
        return OrderedDict(sorted(searchResults.items() , key = lambda x:x[1] , reverse = True))
        
 
    def getRelevantDocs(self, query):
        #Tokenize the query
        terms = query.split(" ")
        #Initialize a list to store all the relevant documents.
        relDocs = list()
        
        for term in terms:
            if term in self._dftable.keys():
                for document in self._dftable[term][0]:
                    if not document in relDocs:
                        relDocs.append(document)
        
        return relDocs
        
        
    #Function to calculate the BM25 score for each term and the current document    
    def bm25TermScore(self, f, qf, n, K):
        k1 =  CONSTANTS.k1(self)
        k2 = CONSTANTS.k2(self)
        N = CONSTANTS.N(self)
        
        #The formula is divided into three parts and each part is calculated separately.
        part1 = math.log((N - n + 0.5) / (n + 0.5))
        part2 = ((k1 + 1) * f) / (K + f)
        part3 = ((k2 + 1) * qf) / (k2 + qf)
        
        #return the product of all three parts.
        return (part1 * part2 * part3)
               
    
    #Function to calculate K
    def calc_K(self, dl):
        b = CONSTANTS.b(self)
        return CONSTANTS.k1(self) * ((1 - b)+ (b * (dl / self._avDL)))
    
             
    #Function to calculate average document length
    def avgDocLength(self):
        totalLength = 0
        
        #get all the files from the corpus
        for file in self._corpus:
            with open(GL.getFilename(self._corpusPath, file) ,'r') as f:
                data = f.read().split(" ")
            
            totalLength+=len(data)
        
        #return total length of all file divided by the number of files in the corpus.
        return totalLength/CONSTANTS.N(self)
    

#Class to define all the constants use to calculate the BM25 score.
class CONSTANTS:
    
    def k1(self):
        return 1.2
    
    def k2(self):
        return 100
    
    def b(self):
        return 0.75
    
    def N(self):
        return 3204
    
if __name__ == "__main__" :
    index = raw_input("Enter json file where index is stored:")
    corpus = raw_input("Enter folder where corpus to be searched is stored:")
    query = raw_input("Enter json file where cleaned queries were stored:")
    
    bm = BM25Search(index , corpus , query)
    bm.search()
