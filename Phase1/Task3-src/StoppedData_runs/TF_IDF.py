import GeneralLib as GL
import math
from collections import OrderedDict
from SnippetGenerator import GenSnippet
from pip._vendor.distlib.compat import raw_input

class TfIdfSearch:
   
    def __init__(self, indexPath, corpusPath, queryPath):
        
        #Dictionary to store the index. 
        self._index = GL.jsonToDict(indexPath)
        self._corpusPath = corpusPath
        #List of all the files in the corpus.
        self._corpus = GL.getDataFiles(corpusPath)
        #Dictionary to store the document frequency table.
        self._dftable = GL.jsonToDict(raw_input("Enter json file where document frequencies are stored.[dTable.json]:"))
        #Dictionary to store all the queries.
        self._queries = GL.jsonToDict(queryPath)
        #System Name (default corpus case folded and striped of punctuation)
        self._systemName = "TF-IDF_CF_PUNC"
        #Choice to generate snippet
        self._chSnippet = 'n'
        
    def search(self):
        resultsPath = raw_input("Enter the path of folder where results will be stored.")
        self._chSnippet = raw_input("Do snippets need to be displayed? (Y/N)")
        if(self._chSnippet == 'Y' or self._chSnippet == 'y'):
            stopFile = raw_input("Enter the file containing stoplist [common_words.txt]")
        
        for qID in self._queries.keys():
            print("Results for Query " + str(qID) + ": \n")
            file = GL.getFilename(resultsPath, "TfIdfSearch-Query" + qID + ".txt")
            results = self.searchCorpus(self._queries[qID])
            if(self._chSnippet == 'Y' or self._chSnippet == 'y'):
                GS = GenSnippet(qID, self._queries[qID], self._corpusPath, self._index, stopFile)
            rank = 1
            resultData = ""
            for doc in results.keys():
                if rank > 100 :
                    break
                res = str(qID) + " QO " + doc + " " + str(rank) + " " + str(results[doc]) + " " + self._systemName+ "\n" 
                if(self._chSnippet == 'Y' or self._chSnippet == 'y'):
                    snippet = GS.generateSnippet((doc + ".html"), str(rank))
                    print(snippet)
                    resultData += (snippet + "\n")
                else:
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

                
        #Calculate tf-idf score for each document in the Documents list
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
                if term in self._index.keys():
                    if document in self._index[term].keys():
                        f = self._index[term][document]  #Term Frequency in the document
                        n = self._dftable[term][1]       #Document Frequency of the term
                        #Calculate the BM25 score for each term with the current document
                        docScore += self.tfIdfTermScore(f, n, dl)
            #Update the result dictionary.
            searchResults.update({document : docScore})
        #Return an ordered dictionary according to score
        return OrderedDict(sorted(searchResults.items() , key = lambda x:x[1] , reverse = True))
        
        
    #Function to calculate tfidf score
    def tfIdfTermScore(self, f, n , dl):
        tf = f / dl
        idf = math.log(CONSTANTS.N(self) / n)
        return (tf * idf)
    
#Class to define all the constants use to calculate the BM25 score.
class CONSTANTS:
    
    def N(self):
        return 3204
    
    
if __name__ == "__main__" :
    index = raw_input("Enter json file where index is stored:")
    corpus = raw_input("Enter folder where corpus to be searched is stored:")
    query = raw_input("Enter json file where cleaned queries were stored:")
    
    tfIdf = TfIdfSearch(index , corpus , query)
    tfIdf.search()