import GeneralLib as GL
import os
from pip._vendor.distlib.compat import raw_input

class Evaluate:
    
    def __init__(self, qresultsPath):
        #Folder where results are stored
        self._qrPath = qresultsPath
        #Json file where relevance info is stored 
        self._relInfo = GL.jsonToDict(raw_input("Enter json file where relevance info is stored:"))
        #Precision table
        self._precTable = dict()
        #Recall Table
        self._recallTable = dict()
        #Table having average precisions for each query 
        self._avgPrecisions = list()
        #Table having the reciprocal rank if first relevant document retrieved.
        self._fRecRank = list()
        self._MAP = 0
        self._MRR = 0
        self._Pat5 = 0
        self._Pat20 = 0
    
    #Evaluate results of a query    
    def performEval(self):
        resultsFile = GL.getDataFiles(self._qrPath)
        evalFilesPath = raw_input("Enter folder where all evaluation results will be stored:")
        if not os.path.exists(evalFilesPath):
            os.mkdir(evalFilesPath)
        
        #For each query, get the results
        for file in resultsFile:
            qID = GL.getQID(file)

            #If query not in relvance info, discard the query
            if not qID in self._relInfo.keys():
                continue
            filename = GL.getFilename(self._qrPath, file)
            results = GL.getResults(filename)
            folderName = evalFilesPath + "Eval_Query" + str(qID) +"/"
            
            
            #Calculate precision and store precision table    
            self._precTable = self.calcPrecision(results, qID)
            data = ""
            if (len(self._precTable.keys()) > 1):
                if not os.path.exists(folderName):
                    os.mkdir(folderName)
                for entry in self._precTable.keys():
                    data += entry + "\t" + str(self._precTable[entry]) + "\n"            
                with open(GL.getFilename(folderName, "PrecisonTable.txt"), 'w') as f:
                    f.write(data)
                
                #Calculate P@5 and P@20 
                self._Pat5 = self.calcPatK(5)
                self._Pat20 = self.calcPatK(20)
                data = "\nPrecision @ 5 :" + str(self._Pat5)
                data += "\nPrecision @ 20 :" + str(self._Pat20)
                with open(GL.getFilename(folderName, "Precision@K.txt"), 'w') as f:
                    f.write(data)
                    
            #Calulate average precisions
            self._avgPrecisions.append(self.calcAvgPrecision(qID, results))
            
            #Calculate precision and store precision table 
            self._recallTable = self.calcRecall(results, qID)
            data = ""
            if (len(self._recallTable.keys()) > 1):
                if not os.path.exists(folderName):
                    os.mkdir(folderName)
                for entry in self._recallTable.keys():
                    data += entry + "\t" + str(self._recallTable[entry]) + "\n"            
                with open(GL.getFilename(folderName, "RecallTable.txt"), 'w') as f:
                    f.write(data)
            
            print("Done with evaluating Query" + str(qID) + ".")
               
        self._MAP = self.calcMAP()
        print(self._MAP)
        self._MRR = self.calcMRR()
        data = "Mean Average Precision : " + str(self._MAP)
        data += "\nMean Reciprocal Rank : " + str(self._MRR)
        
        with open(GL.getFilename(evalFilesPath, "MAP_MRR.txt"), 'w') as f:
            f.write(data)
        print("Done with evaluation.")    
    
    #Function to calculate precision
    def calcPrecision(self, results, qID):
        pTable = dict()
        N = 0
        D = 0
        
        for rank in results.keys():
            if (results[rank] in self._relInfo[qID]):
                N+=1
                if(N==1):
                    self._fRecRank.append(1 / rank)
            D+=1
            pTable.update({results[rank] : (N / D)})
        return pTable
            
    #Function to calculate recall
    def calcRecall(self, results, qID):
        rTable = dict()
        N = 0
        D = len(self._relInfo[qID])
        
        for rank in results.keys():
            if (results[rank] in self._relInfo[qID]):
                N+=1
            rTable.update({results[rank] : (N / D)})
        return rTable

    
    #Function to calculate Average precision
    def calcAvgPrecision(self, qID, results):
        totalPrecision = 0
        for entry in self._relInfo[qID]:
            if entry in results.values():
                totalPrecision += self._precTable[entry]
        
        return (totalPrecision / len(self._relInfo[qID]))
    
    
    #Function to calculate MAP
    def calcMAP(self):
        totalPrecision = 0
        for prec in self._avgPrecisions:
            totalPrecision += prec

        return (totalPrecision / len(self._avgPrecisions))
    
    
    #Function to calculate MRR
    def calcMRR(self):
        totalRecRank = 0
        for rrank in self._fRecRank:
            totalRecRank += rrank
        
        return (totalRecRank / len(self._fRecRank))
            
    
    #Function to calculate precision at K
    def calcPatK(self, K):
        rank = 1
        for doc in self._precTable.keys():
            if rank==K:
                return self._precTable[doc]
            rank+=1
        
        return 0
    
if __name__ == "__main__" :
    
    resultsFolder = raw_input("Enter folder where search results are stored:")
    evaluate = Evaluate(resultsFolder)
    evaluate.performEval()