import re
from bs4 import BeautifulSoup as BS
from pip._vendor.distlib.compat import raw_input
import GeneralLib as GL
from Cleaner import Cleaner

class QCleaner:
    
    def __init__(self, queryFile, queryJSON):
        #Initialize the cleaner object
        self._cleaner = Cleaner(" ", " ")
        #txt file in which all queries are stored
        self._qFile = queryFile
        #json file to store the queries after cleaning
        self._qJson = queryJSON
        #list to store raw queries
        self._queryList = list()
        #list to store refined queries
        self._queryDict = dict()
        #stopList
        self._stopList = list()
        #QueryID initialized to 1
        self._qID = 1

    
    def cleanQueries(self):
        
        choices = [0, 0, 0]
        
        choice = raw_input("Perform case-folding?")
        if (choice == 'Y' or choice == 'y'):
            choices[0] = 1
        
        choice = raw_input("Remove Punctuation?")
        if (choice == 'Y' or choice == 'y'):
            choices[1] = 1
                
        choice = raw_input("Perform stopping?")
        if (choice == 'Y' or choice == 'y'):
            choices[2] = 1
    
        self.getQueries()
        
        for query in self._queryList:
            refinedQuery = self._cleaner.getContent(query.split(r"\n"))
            
            if choices[0] == 1:
                refinedQuery = self._cleaner.case_fold(refinedQuery)
            if choices[1] == 1:
                refinedQuery = self._cleaner.remove_punct(refinedQuery)
            if choices[2] == 1:
                refinedQuery = self._cleaner.stop(refinedQuery)
        
            rQuery = ""
            for token in refinedQuery:
                rQuery += (token + " ")
                
            rQuery = re.sub(r'\s+', ' ', rQuery)
            rQuery = rQuery.lstrip()
            rQuery = rQuery.rstrip()
            
            self._queryDict.update({self._qID : rQuery})
            self._qID+=1
        GL.dictToJson(self._qJson, self._queryDict)
            
        
    def getQueries(self):
        
        soup = BS(open(self._qFile), "html.parser")
        for doc in soup.find_all("docno"):
            doc.extract()
        for query in soup.findAll("doc"):
            text = query.text
            self._queryList.append(text.lstrip().rstrip())
            
            
if __name__ == "__main__" :
    
    queryFile = raw_input("Enter the file containing the queries [cacm.query.txt]:")
    queryJson = raw_input("Enter file where cleaned queries will be stored [.json file]:")
    qCleaner = QCleaner(queryFile, queryJson)
    qCleaner.cleanQueries()