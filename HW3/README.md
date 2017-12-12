## CS6200 Fall 2017
## HW3 Assignment
## Shreysa Sharma

### System Requirements
- Python3
- Python virtualenv (optional)
- Libraries listed in `requirements.txt`
- Make

### Directory contents
- crawler.py - Python3 source file with the implementation of the crawler.
- create_index.py - Python3 source file with the implementation of the indexer.
- Makefile - make file to manage the project.
- README.md - This file.
- requirements.txt - list of python libraries this project depends on.

### Running the crawler and creation of Index code
- Create python virtual environment using `virtualenv -p python3 venv` (optional)
- Change into the created virtualenv using `source venv/bin/activate` (optional)
- Install dependencies for this project using `make deps` (or) `pip3 intall -r requirements.txt`
- Run `make run` to run the crawler (as described in HW1) and the indexer. 
- This creates the output directory data_bfs_1000, corpus folder and all the table files described below.
- `run_index.log` contains the log file of the last indexer run
- Task 1.1, 1.2, 1.3 -> corpus folder generated after indexer runs
- Task 2 -> results/index_1_term_index.txt, results/index_2_term_index.txt and results/index_3_term_index.txt
- Task 3.1 -> results/index_1_term_freq_table.txt, results/index_2_term_freq_table.txt and results/index_3_term_freq_table.txt
- Task 3.2 -> results/index_1_doc_freq_table.txt, results/index_2_doc_freq_table.txt and results/index_3_doc_freq_table.txt
- Task 3.3 -> Stop_List_Explanation.md

### Usage
```
python3 create_index.py create_index.py  [-h] [-c] [-p] [-s] 
optional arguments:
  -h, --help               show this help message and exit
  -c, --case-folding       Convert corpus to lower case
  -p, --filter-punctuation Strip all non-relevant punctuation from the corpus
  -s, --stop-list          Use Stop list to filter words
```

#### Hand-In material
1) Source code is crawler.py for running the crawler and create_index.py that creates the index
2) This file
3) index_1_term_index.txt, index_2_term_index.txt and index_3_term_index.txt for Task 2.
4) index_1_term_freq_table.txt, index_2_term_freq_table.txt and index_3_term_freq_table.txt for Task 3.1
5) index_1_doc_freq_table.txt, index_2_doc_freq_table.txt and index_3_doc_freq_table.txt for Task 3.2
6) Stop_List_Explanation.md for Task 3.3

