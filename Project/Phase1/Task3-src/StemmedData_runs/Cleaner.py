import GeneralLib as GL 
from bs4 import BeautifulSoup as BS
from pip._vendor.distlib.compat import raw_input
import re
    

class Cleaner:
    
    def __init__(self, corpus_path, cleanData_path):
        #Corpus to be cleaned
        self._corpus = GL.getDataFiles(corpus_path)
        #Path of the corpus
        self._corpusPath = corpus_path
        #Path where the clean data will be stored
        self._cleanDataPath = cleanData_path
      
        
    def cleanProc(self):
        
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
        
        for file in self._corpus:        
            soup = BS(open(GL.getFilename(self._corpusPath, file)), "html.parser")
            soup = soup.find("pre")        
            content = (str(soup.findAll(text=True))).split(r"\n")
            
            #Get all the content from the document
            documentData = self.getContent(content)
            
            #Perform following functions if chosen
            if choices[0] == 1:
                documentData = self.case_fold(documentData)
            if choices[1] == 1:
                documentData = self.remove_punct(documentData)
            if choices[2] == 1:
                documentData = self.stop(documentData)
            
            
            #Store the cleaned documents in text files
            document = ""
            for token in documentData:
                document += (token + " ")
            
            document = re.sub(r'\s+', ' ', document)
            document = document.lstrip()
            document = document.rstrip()
                       
            filename = (GL.getTitle(file) + ".txt")   
            with open(GL.getFilename(self._cleanDataPath, filename), 'w') as f:
                f.write(document)
    
    
    #Function to get content from a document and convert to a list of tokens
    def getContent(self, content):
        document = list()
        flag = 0
            
        for line in content:
            if not ((line == "") or (line == "['") or (line == "']")):
                line = line.replace(r"\t" , " ")
                tokens = line.split(" ")
                for token in tokens:
                    if not (any((char.isalpha() or char.isdigit()) for char in token)):
                        continue
                    if(token == "PM") or (token == "AM"):
                        flag = 1
                    document.append(token)
                if (flag == 1):
                    break;
                
        return document
        
    #Function to convert to Lower case
    #Name Initials are excluded.
    def case_fold(self, content):
        transformedContent = list()
        
        for token in content:
            if(re.search(r'[A-Z][a-z]+\,', token)) or (re.search(r'[A-Z]\.', token)):
                transformedContent.append(token)
            else:
                token = token.lower()
                transformedContent.append(token)
        return transformedContent
    
    #Function to remove punctuation
    def remove_punct(self, content):
        transformedContent = list()
        for token in content:
            if(token.upper() == token.lower()): #Checks if a term contains alphabets 
                #Remove all punctuation marks except (',' '.' '-') for numbers
                token = re.sub(r'[^\.\,\:\w\s-]', "" , token) 
                transformedContent.append(token)
            elif(re.search(r'[A-Z][a-z]+\,', token)):
                token = re.sub(r'[^\,\w\s-]', "" , token)
                transformedContent.append(token)
            elif (re.search(r'[A-Z]\.', token)):
                token = re.sub(r'[^\.\w\s-]', "" , token)
                transformedContent.append(token)
            else:
                #Remove all punctuation marks except ('-') for words
                token = re.sub(r'[^\w\s-]', "" , token)
                transformedContent.append(token)
        return transformedContent
    
    #Function to stop content
    def stop(self,content):
        #File containing stoplist
        file = raw_input("Enter full path and name of the file containing stoplist[.txt].")
        with open(file , 'r') as f:
            stoplist = f.read().split("\n")
        transformedContent = list()
        
        #Discard the word if in stoplist. 
        for token in content:
            if not token.strip() in stoplist:
                transformedContent.append(token)
                
        return transformedContent

#Main function
if __name__ == "__main__" :
    corpus = raw_input("Enter path of the cacm dataset:")
    cleanData = raw_input("Enter path of folder where clean data will be stored:")
    cleaner = Cleaner(corpus, cleanData)
    cleaner.cleanProc()