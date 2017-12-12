import GeneralLib as GL
from TF_IDF import TfIdfSearch
from collections import OrderedDict

class ProximitySearch:
    
    def __init__(self, indexPath, corpusPath, queryPath):
        
        #Dictionary to store the index. 
        self._index = GL.jsonToDict(indexPath)
        self._corpusPath = corpusPath
        #List of all the files in the corpus.
        self._corpus = GL.getDataFiles(corpusPath)
        #Dictionary to store all the queries.
        self._queries = GL.jsonToDict(queryPath)
        #System Name (default corpus case folded and striped of punctuation)
        self._systemName = "TF-IDF_CF_PUNC_PROX"
        #Allowed number of terms between two query terms
        self._prefNoTerms = 3
        #Index without positions.
        indexWoPos = "E:/InformationRetrieval/Assignments/IR2017_Project/Index/StoppedIndexWOPos.json"
        #TfIdf search object
        self._tfIdf = TfIdfSearch(indexWoPos, corpusPath, queryPath)
        
    
    def search(self): 
    
        resultsPath = "E:/InformationRetrieval/Assignments/IR2017_Project/ExtraCredit/TfIdf_ProximitySearch[Stopped]_Results/"
        for qID in self._queries.keys():
            print("Results for Query " + str(qID) + ": \n")
            file = GL.getFilename(resultsPath, "TfIdfSearch-Query" + qID + ".txt")
            tfidf_results = self._tfIdf.searchCorpus(self._queries[qID])
            prox_results = dict()
            for doc in tfidf_results.keys():
                docScore = self.calcProxScore(doc, self._queries[qID])
                if (docScore > 0):
                    prox_results.update({doc : docScore})

            final_results = OrderedDict(sorted(prox_results.items() , key = lambda x:x[1] , reverse = True))
            rank = 1
            resultData = ""
            for doc in final_results.keys():
                if rank > 100 :
                    break
                res = str(qID) + " QO " + doc + " " + str(rank) + " " + str(final_results[doc]) + " " + self._systemName+ "\n" 
                print(res)
                resultData += res
                rank+=1
                
            with open(file , 'w') as f:
                f.write(resultData)
            print("Done with Query " + str(qID))


    def calcProxScore(self, doc, query):
        
        qterms = query.split(" ")
        
        docScore = 0
        for i in range(0,len(qterms)):
            if (i==len(qterms)-1):
                break
            inwordCount = 5
            if (qterms[i] in self._index.keys()):
                if(doc in self._index[qterms[i]].keys()):
                    for pos in self._index[qterms[i]][doc][1]:
                        if (qterms[i+1] in self._index.keys()):
                            if(doc in self._index[qterms[i+1]].keys()):
                                for nextWPos in self._index[qterms[i+1]][doc][1]:
                                    if(pos < nextWPos):
                                        inwordCount = nextWPos - pos - 1
                                        break

            
            docScore += ((inwordCount - 3) / 4) 
        
        return docScore
            

if __name__ == "__main__" :
    index = "E:/InformationRetrieval/Assignments/IR2017_Project/Index/StoppedIndexWPos.json"
    corpus = "E:/InformationRetrieval/Assignments/IR2017_Project/CleanData[Stopped]/"
    query = "E:/InformationRetrieval/Assignments/IR2017_Project/Index/stoppedQuery.json"
    
    psearch = ProximitySearch(index , corpus , query)
    psearch.search()