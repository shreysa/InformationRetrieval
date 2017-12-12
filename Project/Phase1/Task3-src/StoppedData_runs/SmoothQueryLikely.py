import GeneralLib as GL
import math
from collections import OrderedDict
from pip._vendor.distlib.compat import raw_input

class SmoothQuery:
   
    def __init__(self, indexPath, corpusPath, queryPath):
        
        #Dictionary to store the index. 
        self._index = GL.jsonToDict(indexPath)
        self._corpusPath = corpusPath
        #List of all the files in the corpus.
        self._corpus = GL.getDataFiles(corpusPath)
        #Dictionary to store all the queries.
        self._queries = GL.jsonToDict(queryPath)
        #Corpus Length
        self._CL = 0
        #System Name (default corpus case folded and striped of punctuation)
        self._systemName = "SmoothedQueryLikelihood_CF_PUNC"
        
    def search(self):
        resultsPath = raw_input("Enter the path of folder where results will be stored.")
        self._CL = self.corpusLength()
        for qID in self._queries.keys():
            print("Results for Query " + str(qID) + ": \n")
            file = GL.getFilename(resultsPath, "SmoothedQueryLike-Query" + qID + ".txt")
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
        qterms = query.split(" ")
        searchResults = dict()
                
        #Calculate Smoothed Query Likelihood score for each document in document list
        #Jelinek-Mercer smoothing is used.
        for document in self._corpus:
            #Strip the document name extension
            document = GL.getTitle(document)
            #Get document length for the current document
            with open(GL.getFilename(self._corpusPath, document + ".txt") ,'r') as f:
                data = f.read().split(" ")
            dl = len(data)
            
            #Initialize the document score to 0
            docScore = 0
            #Calculate the BM25 score for each term and add them to the docScore
            for term in qterms:
                if (term in self._index.keys()) and (document in self._index[term].keys()):
                    f = self._index[term][document]  #Term Frequency in the document
                else:
                    f = 0
                c = self.tf_corpus(term)       #Corpus Frequency of the term
                #Calculate the BM25 score for each term with the current document
                docScore += self.SmQLTermScore(f, c, dl)
            #Update the result dictionary.
            searchResults.update({document : docScore})
        #Return an ordered dictionary according to score
        return OrderedDict(sorted(searchResults.items() , key = lambda x:x[1] , reverse = True))
        
    
    #Function to calculate P(Q|D)    
    def SmQLTermScore(self, f, c, dl):
        L = CONSTANTS.Lambda(self)
        part1 = ((1 - L) * (f / dl))
        part2 = L * (c / self._CL)
        if(part1 == 0) and (part2 == 0):
            return 0
        return math.log(part1 + part2)
    
    
    #Function to calculate corpus size
    def corpusLength(self):
        totalLength = 0
        
        #get all the files from the corpus
        for file in self._corpus:
            with open(GL.getFilename(self._corpusPath, file) ,'r') as f:
                data = f.read().split(" ")
            
            totalLength+=len(data)
        return totalLength
    
    
    #Function to calculate term frequency over whole corpus
    def tf_corpus(self, term):
        totaltf = 0
        if term in self._index.keys():
            for doc in self._index[term].keys():
                totaltf += self._index[term][doc]
        return totaltf
            
    
#Class to define all the constants use to calculate the BM25 score.
class CONSTANTS:
    
    def Lambda(self):
        return 0.35
    
    
if __name__ == "__main__" :
    index = raw_input("Enter json file where index is stored:")
    corpus = raw_input("Enter folder where corpus to be searched is stored:")
    query = raw_input("Enter json file where cleaned queries were stored:")

    sm = SmoothQuery(index , corpus , query)
    sm.search()
