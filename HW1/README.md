## CS6200 Fall 2017
## HW1 Assignment
## Shreysa Sharma

### System Requirements
- Python3
- Python virtualenv (optional)
- Libraries listed in `requirements.txt`
- Make

### Directory contents
- crawler.py - Python3 source file with the implementation of the crawler
- Makefile - make file to manage the project
- README.md - This file
- requirements.txt - list of python libraries this project dependencs on

### Running the crawler
- Create python virtual environment using `virtualenv -p python3 venv` (optional)
- Change into the created virtualenv using `source venv/bin/activate` (optional)
- Install dependencies for this project using `make deps` (or) `pip3 intall -r requirements.txt`
- Run `make help` to print crawler usage message
- Run `make run_task_1` to run Task 1.E described in HW1 description
  The downloaded data is stored in `data/*.html` and `data/urls.txt` has the list of urls
- Back up the data folder if required
- Run `make run_task_2` to run Task2 described in HW1 description
  The downloaded data is stored in `data/*.html` and `data/urls.txt` has the list of urls
- `run.log` contains the log file of the run


#### Depth Reached
The Task 1 reached a depth of 3 and 1000 urls.
The Task 2 reached a depth of 6 and 410 urls.
