# CS6200 - Fall 2017
# HW3
# Author: Shreysa Sharma
# October 25, 2017

URL_LIMIT=1000
DEPTH_LIMIT=6
DELAY=1
START_URL=https://en.wikipedia.org/wiki/Tropical_cyclone

deps:
	pip3 install -r requirements.txt

help:
	@echo "Crawler Help"
	@echo "------------"
	python3 crawler.py -h
	@echo "Indexer help"
	@echo "------------"
	python3 create_index.py -h

# Crawler Commands

run:	run_crawler_bfs generate_index

run_crawler_bfs:
	python3 crawler.py $(START_URL) $(URL_LIMIT) $(DEPTH_LIMIT) $(DELAY) --crawl bfs
	@mv ./data ./data_bfs_$(URL_LIMIT)


# Indexer Commands
generate_index:
	python3 create_index.py data_bfs_$(URL_LIMIT) --case-folding --filter-punctuation

generate_index_casefolding:
	python3 create_index.py data_bfs_$(URL_LIMIT) --case-folding 

generate_index_punctuation:
	python3 create_index.py data_bfs_$(URL_LIMIT) --filter-punctuation

generate_index_no_args:
	python3 create_index.py data_bfs_$(URL_LIMIT)

generate_index_with_stoplist:
	python3 create_index.py data_bfs_$(URL_LIMIT) --case-folding --filter-punctuation --stop-list

generate_index_stoplist:
	python3 create_index.py data_bfs_$(URL_LIMIT) --stop-list
# Utility commands

clean:
	@rm -rf *.log
	@rm -rf *.txt
	@rm -rf *.png
