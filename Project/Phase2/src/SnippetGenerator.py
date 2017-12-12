import GeneralLib as GL

class GenSnippet:
    
    def __init__(self, qID, query, corpus, index, stopFile):
        self._corpus = GL.getDataFiles(corpus)
        self._corpusPath = corpus
        self._index = index
        self._qID = qID
        self._query = query.split(" ")
        #Number of words to be accounted for before and after the query term
        self._lookahead = 5
        #StopList
        self._stopList = GL.fileToList(stopFile)
    
    #Function to generate snippets
    def generateSnippet(self, file, rank):
        with open(GL.getFilename(self._corpusPath, file), "r") as f:
            data = f.read().split(" ")
            
        snippet = "\n<document>\n<qid>" + self._qID + "<\\qid>\n"
        snippet += "<rank>" + rank + "<\\rank>\n"
        snippet += ("<doc>" + GL.getTitle(file) + "<\\doc>\n<snippet>\n")
        
        maxFreqTerm = self._query[0]
        maxFreq = 0
        
        #Get the query term with maximum frequency in the document
        for token in data:
            if not (any((char.isalpha() or char.isdigit()) for char in token)):
                continue
            if ("<" in token):
                continue
            token = token.lower()
            if token in self._index.keys():
                if token in self._index[token].keys():
                    if self._index[token][GL.getTitle(file)] > maxFreq:
                        if not ((token == "") or (token == " ") or (token in self._stopList)):
                            maxFreqTerm = token
                            maxFreq = self._index[token][GL.getTitle(file)]
        
        if maxFreqTerm in data:
            pos = data.index(maxFreqTerm)
        else:
            pos = 3
        docSnip = ""
        
        #Formulate a snippet highlighting the query terms
        for i in range(pos-self._lookahead, pos+self._lookahead):
            if (i > -1 and i < len(data)):
                if not ("<" in data[i]):
                    token = data[i].replace("<html>","").replace("<\\html>","").replace("<\\pre>","").replace("<pre>","").replace("\n","").replace("\t","") 
                    #Highlight the terms in query
                    if(token in self._query):
                        docSnip += ("<b>" + token + "<\\b> ")
                    else:
                        docSnip += (token + " ")
        snippet += docSnip + "\n<\\snippet>\n<\\document>"
        return snippet
                
            
        