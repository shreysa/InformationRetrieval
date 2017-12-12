## CS6200 Fall 2017
## HW2 Assignment
## Shreysa Sharma

### System Requirements
- Python3
- Python virtualenv (optional)
- Libraries listed in `requirements.txt`
- Make

### Directory contents
- crawler.py - Python3 source file with the implementation of the crawler.
- process.py - Python3 source file with the implementation of the PageRank algorithm.
- Makefile - make file to manage the project.
- README.md - This file.
- requirements.txt - list of python libraries this project depends on.

### Running the crawler and PageRank code
- Create python virtual environment using `virtualenv -p python3 venv` (optional)
- Change into the created virtualenv using `source venv/bin/activate` (optional)
- Install dependencies for this project using `make deps` (or) `pip3 intall -r requirements.txt`
- Run `make help` to print crawler usage message
- Run `make run_crawler_bfs` to collect data for Task 1.A described in HW2 description
  The downloaded data is stored in `data_bfs_1000/*.html` and `data_bfs_1000/urls.txt` has the list of urls
- Run `make run_crawler_dfs` to collect data for Task 1.B described in HW2 description
  The downloaded data is stored in `data_dfs_1000/*.html` and `data_dfs_1000/urls.txt` has the list of urls
- Back up the data folder(s) if required
- `run.log` contains the log file of the last crawler run
- Run `make compute_test` to run PageRank on the test graph provided in HW2 pdf.
  + The run log is stored in `run_process.log`.
  + The graph is stored in `TEST_graph.txt`.
  + The results (PageRank and IncomingLinkCount) are stored in `TEST_results.txt`.
  + The perplexity history is plotted against num_iterations and stored in `TEST_perplexity_history.png`.
- *Task 3 - G1* - Run `make compute_bfs`
  The run creates the same set of files as described for `compute_test`, `TEST` is replaced with `G1`.
- *Task 3 - G2* - Run `make compute_dfs`
  The run creates the same set of files as described for `compute_test`, `TEST` is replaced with `G2`.

### Assumptions:

A sink is which does not have any outgoing links to the list of urls generated when the program is run.

The doc id's are case sensitive.


#### Hand-In material
1) Source code is process.py and crawler.py
2) This file
3) Results/G1_graph.txt and Results/G2_graph.txt
4) Source_Sink_Prop.pdf
5) Perplexity_Values
6) Results/G1_results txt 
7) Results/G2_results.txt
8) Quantitative_Analysis.pdf


Results/G1_Perplexity_history.png and Results/G2_Perplexity_history.png represent the graph for perplexity values plotted against number of iterations.

Results/G1_urls.txt has the list of urls parsed for G1 and Results/G2_urls.txt has the list of urls parsed for G2.
