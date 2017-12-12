Final Project:

Goal: Design and build your information retrieval systems, evaluate and compare their performance levels in terms of retrieval effectiveness

SYNOPSIS:

This readme file has references and detailed information regarding how to setup, compile and run the programs in the assignment.
The project has multiple Folders:
Each of the base folders' contents are mentioned below:
--CleanData[CF_PUNC]
	-Clean dataset [CaseFolded and Striped Punctuation]
--CleanData[Stemmed]
	-Clean dataset [Stemmed]
--CleanData[Stopped]
	-Clean dataset [CaseFolded, Striped Punctuation and Stopped]
--DataSet
	-The cacm dataset provided
--Indexes
	-All different types of indexes created throughout the project.
--Phase1
	-Source Code and Results for Phase 1 of the Project.
--Phase2
	-Source Code and Results for Phase 2 of the Project.
--Phase3
	-Source Code and Results for Phase 3 of the Project.
--Phase4-ExtraCredit
	-Source Code and Results for Phase 4 of the Project.[Performing Proximity-based search]


GENERAL USAGE NOTES:

-- This project is written using Python 3.6.2
   Lucene model is implemented using JavaSE 8

-- Some files need the following python libraries to execute
   Beautiful Soup
 
-- However, the programs are independent of any operating systems and will run successfully in all platforms once the initial installation has been done. 




INSTALLATION GUIDE:

-- Download python 3.6.x from https://www.python.org/download/releases/3.6/

-- From Windows Home go to Control Panel -> System and Security -> System -> Advanced System Settings -> Environment Variables and add two new variables in 'PATH' -> [Home directory of Python]; [Home directory of Python]\Scripts

-- Open Command Prompt and upgrade pip using the following command: 'python -m pip install -U pip'

-- To check whether you have pip installed properly, just open the command prompt and type 'pip'

-- It should not throw an error, rather details regarding pip will be displayed.

-- Install BeautifulSoup by using the command 'pip install beautifulsoup4'

-- Open the unzipped folder and open a command prompt in that location and write the given command - 'C:\Python27\python.exe setup.py install'



-- Install JAVA SE8 or above if not already installed in the system from http://www.oracle.com/technetwork/java/javase/index-137561.html#windows

-- From Windows Home go to Control Panel -> System and Security -> System -> Advanced System Settings -> Environment Variables and add new variable in 'PATH' -> [Home directory of Java]\jdk[version number]\bin;


GENERAL INSTRUCTIONS:

Phase 1:
-Phase 1 is divided into three tasks:
--Task 1:
	1. Clean Corpus
	   Run 'Cleaner.py' to perform corpus cleaning. Options are provided to case-fold, remove punctuation and stop data.
	2. Clean Queries
	   Run 'QueryCleaner.py' to perform query cleaning. Options are provided to case-fold, remove punctuation and stop data.
	3. Index cleaned corpus
	   Run 'Indexer.py' to perform indexing. Options are provided asking whether or not to store term positions.
	4. Generate Document Frequency Table
	   Run 'DocFreqTables.py' to create document frequency table
	5. Run three base search engines BM25, Tf-Idf, Smoothed Query Likelihood model.
	   Run following file to execute all the search engines:
		BM25_Retrieval.py
		TF_IDF.py
		SmoothQueryLikely.py
	6. Include following jar files for Lucene:
	   LUCENE 4.7.2 is used.
		lucene-core-VERSION.jar
		lucene-queryparser-VERSION.jar
		lucene-analyzers-common-VERSION.jar

	  Run 'Main.java' to execute the Lucene search Engine.

	Task 1 results for all runs are stored in the Task1_Results folder.
	
--Task 2:
	Perform a pseudo-relevance feedback on results obtained afte running the queries for BM25 model.
	Run following file in order to execute pseudo-relevance feedback for BM25 Model:
		create_index.py	data/cacm --no-clean mv index_saved.pickle src/index_saved.pickle	
		bm25_PRF.py src/index_saved.pickle data/cacm.query.txt --xml --prf --stop-list-file common_words.txt

	Task 2 results for all runs are stored in the Task3_Results folder.

--Task 3:
---Stopping
	1. Clean Corpus
	   Run 'Cleaner.py' to perform corpus cleaning. Choose to stop the data.
	2. Clean Queries
	   Run 'QueryCleaner.py' to perform query cleaning. Choose to stop the data.
	3. Index cleaned corpus
	   Run 'Indexer.py' to perform indexing. Options are provided asking whether or not to store term positions.
	4. Generate Document Frequency Table
	   Run 'DocFreqTables.py' to create document frequency table
	5. Run three base search engines BM25, Tf-Idf, Smoothed Query Likelihood model.
	   Run following files to execute all the search engines for stopped data:
		BM25_Retrieval.py
		TF_IDF.py
		SmoothQueryLikely.py

---Stemming
	1. Create seperate files for each documents and index them.
	   Run 'StemmedCorpus.py'.
	4. Generate Document Frequency Table
	   Run 'DocFreqTables.py' to create document frequency table
	5. Run three base search engines BM25, Tf-Idf, Smoothed Query Likelihood model.
	   Run following files to execute all the search engines for stemmed data:
		BM25_Retrieval.py
		TF_IDF.py
		SmoothQueryLikely.py	

	Task 3 results for all runs are stored in the Task3_Results folder.

--Phase 2:
-Displaying snippets for results generated.
	1. Run Tf-Idf model on the queries. Choose to generate snippets when prompted to.
	   Run 'TF_IDF.py'
	
	Phase 2 results for snippet generation run is stored in the Results folder in the Phase2 folder.

--Phase 3:
-Evaluating results generated.
	1. Extract the relevance info from the cacm.rel.txt file provided
	   Run 'GenDicts.py'
	2. Evaluate the results generated by the above runs.
	   Run 'Evaluation.py' for each run by passing the folder where results for each run are stored when prompted.
	
	Phase 3 results for Evaluations of 8 runs are stored in the Results folder in the Phase3 folder.
	Each folder inside the results folder consists of files containing Precision and Recall Table and Precision@K(5,20) values.
	A file named 'MAP_MRR.txt' consists the Mean Average Precision and Mean Reciprocal Rank for each run.

--Phase 4:
-Performing Proximity-enabled search.
	1. Run the Proximity-enabled search combined with tf-idf on with stopping and without stopping.
	   Run 'ProximitySearch.py' twice.
		1. Enter the corpus and index generated with positions and without stopping. 
		2. Enter the corpus and index generated with positions and with stopping. 

	Phase 4 results for snippet generation run is stored in the Results folder in the Phase4-ExtraCredit folder.
	Evaluations performed on results generated in Phase 4 [Precision and Recall Tables, P@K, MAP, MRR] are stored in
	'EvaluationResults' folder inside Phase4-ExtraCredit.