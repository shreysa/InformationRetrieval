### Stop Words List - Details and Discussion
##### Author: Shreysa Sharma
##### Course: CS6200 - Fall 2017

Three Approaches were used to generate the stop word list: 
 
#### Approach 1:

- In the First approach, the top n most frequent words are picked programmatically (here n = 15) and stop word list is generated which is in the file `results/stop_list.txt`.
	The stop words are : 'the', 'of', 'and', 'in', 'to', 'a', 'on', 'retrieved', 'is', 'from', 'as', 'for', 'was', 'by', 'with'
	
#### Approach 2:

- In the Second approach, owing to the corpus size I programmatically calculate the percentage occurrance of words and pick the words that have percentage of occurrance greater than half percent. This list is stored in `results/stop_list_by_percentage.txt`
	The words are : 'the', 'of', 'and', 'in', 'to', 'a', 'on', 'retrieved', 'is', 'from', 'as', 'for', 'was', 'by', 'with', 's'
	
#### Approach 3:

- In the third approach, the `results/index_1_term_freq_table.txt` was manually examined and the following words were picked up for the stop word list:
      'the', 'of', 'and', 'in', 'to', 'a', 'on', 'is', 'from', 'as', 'for', 'was', 'by', 'with', 's'
	
#### Conclusion:
- The manual examination was necassery to remove words that appeared to be relevant to the subject matter. If we just use approach 1 or 2 we miss out on the word "*retrieved*", which could be a meaningful word in the context of the content. For e.g:  4 people “retrieved"" from the hurricane effected areas. Including “retrieved” to the stop list could lead to loss of useful or sought after information. I decided the cut off value as 15 as the last word added to the stop list is “*s*”. Just the letter “s” does not add to any useful information and has high occurrence majorly because of the way punctuation has been done. In the code,  “that’s” would be trimmed to “that s” and not “thats”. “s” is very commonly used with apostrophe and this kind of filtering results in high occurance of s in the index. All words after s in the list could be used contextually to make things more understandable, hence, the cut off value was decided to be 15.

- The words in the stop list are the most frequent words and if skipped from a sentence, would not lead to loss of information and at the same time help in reducing the number of index entries. As the selection of stop words depends from corpus to corpus if the seed page is changed to something else then the stop list would also need to be changed.
