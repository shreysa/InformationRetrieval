# CS6200 - Fall 2017
# HW2
# Author: Shreysa Sharma
# October 25, 2017

URL_LIMIT=1000
#URL_LIMIT=100
DEPTH_LIMIT=6
DELAY=1
KEYWORD=rain
START_URL=https://en.wikipedia.org/wiki/Tropical_cyclone

deps:
	pip3 install -r requirements.txt

help:
	@echo "Crawler Help"
	@echo "------------"
	python3 crawler.py -h
	@echo "PageRank Process help"
	@echo "---------------------"
	python3 process.py -h

# Crawler Commands

run_crawler_dfs:
	python3 crawler.py $(START_URL) $(URL_LIMIT) $(DEPTH_LIMIT) $(DELAY) --crawl dfs
	@mv ./data ./data_dfs_$(URL_LIMIT)

run_crawler_bfs:
	python3 crawler.py $(START_URL) $(URL_LIMIT) $(DEPTH_LIMIT) $(DELAY) --crawl bfs
	@mv ./data ./data_bfs_$(URL_LIMIT)

run_crawler_dfs_focused:
	python3 crawler.py $(START_URL) $(URL_LIMIT) $(DEPTH_LIMIT) $(DELAY) --keyword $(KEYWORD) --crawl dfs
	@mv ./data ./data_dfs_focused_$(URL_LIMIT)

run_crawler_bfs_focused:
	python3 crawler.py $(START_URL) $(URL_LIMIT) $(DEPTH_LIMIT) $(DELAY) --keyword $(KEYWORD) --crawl bfs
	@mv ./data ./data_bfs_focused_$(URL_LIMIT)

# PageRank process script commands

compute_bfs:
	python3 process.py data_bfs_$(URL_LIMIT) G1 --num-top 50 

compute_dfs:
	python3 process.py data_dfs_$(URL_LIMIT) G2 --num-top 50 

compute_test:
	python3 process.py ignored_directory TEST --num-top 10 --test

# Utility commands

clean:
	@rm -rf *.log
	@rm -rf *.txt
	@rm -rf *.png
