import GeneralLib as GL
from collections import OrderedDict
from pip._vendor.distlib.compat import raw_input

def gen_df_tables(index):
        
    df_table = dict() #Initialize dictionary for a table
        
    #For each term in the index calculate document frequency and store in the table(dictionary)
    #along with the DocIDs.
    for term in index.keys():
        docIDs = list()
        for doc in index[term].keys():
            docIDs.append(doc) 
            
        df_table.update({term : (docIDs , len(docIDs))})
        
        #Return  a lexicographically sorted dictionary.    
    return OrderedDict(sorted(df_table.items() , key = lambda x:x[0]))

if __name__ == "__main__" :
    index = raw_input("Enter path of the index")
    GL.dictToJson(raw_input("Enter json file where doc frequency table will be stored."), gen_df_tables(index))