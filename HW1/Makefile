clean:
	rm -rf ./data
	rm -rf ./data_old

deps:
	pip3 install -r requirements.txt

help:
	python3 crawler.py -h

run_task_1:
	python3 crawler.py https://en.wikipedia.org/wiki/Tropical_cyclone 1000 6 1

run_task_2:
	python3 crawler.py https://en.wikipedia.org/wiki/Tropical_cyclone 1000 6 1 --keyword rain
