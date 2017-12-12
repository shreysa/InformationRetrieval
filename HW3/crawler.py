#!/usr/bin/env python3

# CS6200 - Fall 2017
# HW 3
# Author: Shreysa Sharma
# Date: October 25th, 2017

import os
import re
import sys
import time
import shutil
import logging
import hashlib
import argparse
import requests
from urllib import parse
from bs4 import BeautifulSoup
from stemming.porter2 import stem

class Crawler:

    def __init__(self, base_url, root_url, urls_limit, depth_limit, delay, crawl_type, keyword=None):
        self._urls = list()
        self._limit = urls_limit
        self._limit_depth = depth_limit
        self._delay = delay
        self._depth = 1
        self._request_data = None
        self._base_url = base_url
        self._root_url = root_url
        self._keyword = keyword
        self._crawl_type = crawl_type
        self._keyword_stem = None
        self._prev_page_get_time = time.time()
        self._url_to_file_name_map = dict()

        if self._keyword:
            self._keyword_stem = stem(self._keyword)

        '''
        The logging code was referenced from :
        https://stackoverflow.com/questions/40858658/python-logging-to-stdout-and-log-file
        '''

        logging.basicConfig(filename='run.log', level=logging.INFO)
        root_log = logging.getLogger()
        root_log.setLevel(logging.INFO)

        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        channel.setFormatter(formatter)
        root_log.addHandler(channel)

    def get_page(self, url):
        '''
        Gets the page if time difference between when the last 
        page was fetched and current time is greater than provided delay
        else waits for the provided time before fetching
        '''
        current_time = time.time()
        if current_time - self._prev_page_get_time >= self._delay:
            self._request_data = requests.get(url)
            self._prev_page_get_time = time.time()
            logging.info('Getting page :, url: {}'.format(url))
            return self._request_data
        else:
            logging.info('Delaying get_page for {} second(s)'.format(self._delay))
            time.sleep(self._delay)
            return self.get_page(url)
    
    def add_element(self, url, depth, index, container):
        '''
        Check if URL exists in global URL cache
        '''
        for elem in self._urls: 
            if elem == url:
                return False
        
        '''
        Check if URL exists in link URL cache
        '''
        for elem in container:
            if elem['url'] == url:
                return False

        '''
        If not, create Link Object and add to container
        '''
        link_object = {'url': url, 'depth': depth, 'index_in_page': index}
        logging.debug('Appending url to list from depth {} : {}'.format(self._depth, url))
        container.append(link_object)
        
        
    def process_url(self, url):
        '''
        Strips out http from the url and gets just the last part of the url for processing
        '''
        if url is None:
            return None
        url_local = url.strip()
        if url.startswith('http'):
            split_url = url_local.split('://', 1)
            url_local = split_url[-1]
        return url_local

    def contains_keyword(self, url, url_text):
        '''
            When there is no keyword, search is not Focused
            all urls are processed
        '''
        if self._keyword is None:
            return True
        else:
            '''
            if search keyword is provided, then the url is splitted and the keyword's existence is 
            checked in the url
            '''
            url_text_words = url_text.strip().split()
            for word in url_text_words:
                if word.lower().startswith(self._keyword_stem):
                    return True

            url_decoded = parse.unquote(url)
            url_split = re.split('/|_|-', url_decoded)
            for word in url_split:
                if word.lower().startswith(self._keyword_stem):
                    return True
        return False
   
        
    def process_links(self, found_urls, depth):
        '''
        The link is processes to get the href, remove the administrative and 
        the links that point to the same page. The links with wiki in it are added,
        also a check is done for the keywords if any have been provided
        '''
        urls_container = []
        for i, link in enumerate(found_urls):
            url = self.process_url(link.get('href'))
            url_text = link.get('title')
            if url is None:
                continue
            elif '#' in url or ':' in url:
                continue
            elif url.startswith('/wiki/') and self.contains_keyword(url, url_text):
                self.add_element(url, depth, i, urls_container)
            else:
                continue
        return urls_container

    def get_links_in_page(self, request_data, depth):
        '''
        Beautiful Soup library has been used to parse the html
        Makes note of number of links found, filters and adds them on the 
        basis of if the limit provided has been reached or not
        '''
        if (request_data.ok or request_data.is_permanent_redirect or request_data.is_redirect):
            soup = BeautifulSoup(request_data.text, 'html.parser')
            content_div = soup.find(id='bodyContent').find(id="mw-content-text")
            found_links = content_div.find_all('a')
            urls_container = self.process_links(found_links, depth)
            logging.info('Number of links found in page: {}'.format(len(urls_container)))

            urls_added = []
            if len(self._urls) >= self._limit:
                return []
            elif len(self._urls) + len(urls_container) >= self._limit:
                cur_len = len(self._urls)
                remaining_items = self._limit - cur_len        
                return urls_container[:remaining_items]
            else:
                return urls_container

    def crawl_pages_dfs(self, url, depth, index):
        '''
        Pages are crawled here using *depth-first* search and checks are done for each item 
        before crawling to keep note of the limit or depth provided
        '''

        # Quit if the URL count limit is reached
        if len(self._urls) >= self._limit:
            return

        # Quit if the depth limit is reached
        if (depth + 1) > self._limit_depth:
            return
        
        # if url is already not present in the list of urls then it is added to the list
        if url not in self._urls:
            self._urls.append(url)
            request_data = self.get_page(self._base_url + url)
            self.write_page(request_data, depth, index)
            self._depth = depth + 1
            links_in_page = self.get_links_in_page(request_data, depth + 1)
            for url_obj in links_in_page:
                url = url_obj['url']
                url_depth = url_obj['depth']
                url_index = url_obj['index_in_page']                
                self.crawl_pages_dfs(url, url_depth, url_index)

    def crawl_pages_bfs(self, url, depth, index):
        '''
        Pages are crawled here using *breath-first* search and checks are done for each item 
        before crawling to keep note of the limit or depth provided
        '''
        url_obj_initial = {'url': url, 'index_in_page': 0, 'depth': depth}
        queue = [url_obj_initial]

        while queue:
            url_obj = queue.pop(0)
            url = url_obj['url']
            url_depth = url_obj['depth']
            url_index = url_obj['index_in_page']

            # Quit if the URL count limit is reached
            if len(self._urls) >= self._limit:
                logging.info('Stopping crawler, URL limit reached')
                break

            # Quit if the depth limit is reached
            if (url_depth + 1) > self._limit_depth:
                logging.info('Stopping crawler, depth limit reached')
                break

            # if url is already not present in the list of urls then it is added to the list
            if url not in self._urls:
                self._urls.append(url)
                request_data = self.get_page(self._base_url + url)
                self.write_page(request_data, url_depth, url_index)
                self._depth = url_depth + 1
                links_in_page = self.get_links_in_page(request_data, url_depth + 1)
                queue.extend(links_in_page)
    
            
    def write_url_files(self):
        logging.info('Writing list of urls to {}'.format('./data/urls.txt'))
        with open('./data/urls.txt', 'w') as f:
            for url in self._urls:
                f.write(self._base_url + url + '\n')

        logging.info('Writing list of url -> file_name map to {}'.format('./data/url_to_file_map.csv'))
        with open('./data/url_to_file_map.csv', 'w') as f:
            for key, value in self._url_to_file_name_map.items():
                f.write('{};{}\n'.format(key, value))
    
    def write_page(self, request_data, depth, index):
        unique_hash = hashlib.md5(request_data.url.encode('utf-8')).hexdigest()
        file_name = 'data/d_{}_i_{}_{}.html'.format(depth, index, unique_hash)
        self._url_to_file_name_map[request_data.url] = file_name
        logging.info('Saving page to file {}'.format(file_name))
        with open(file_name, 'w') as f:
            f.write('<!--Crawler.py CS6200 - Depth: {} - Index: {} - URL: {}-->\n'.format(depth, index, request_data.url))
            f.write(request_data.text)
 
    def start(self):
        '''
        This is the starter method, writes down processing information on the output window
        '''
        logging.info('\n')
        header_message = 'Starting crawler at page: {}'.format(self._base_url + self._root_url)
        logging.info(header_message)
        logging.info('-'*len(header_message))
        logging.info('\tParameters:')
        focussed_mode = "False"
        if self._keyword:
            focussed_mode = "True"
        logging.info('Crawler Type:   |   {}'.format(self._crawl_type))
        logging.info('Focused Mode:   |   {}'.format(focussed_mode))
        logging.info('Root URL:       |   {}'.format(self._root_url))
        logging.info('URLs Limit:     |   {}'.format(self._limit))
        logging.info('Depth Limit:    |   {}'.format(self._limit_depth))
        logging.info('Request Delay:  |   {} second(s)'.format(self._delay))
        logging.info('Keyword:        |   {}'.format(self._keyword))

        # Create directory for storing run data
        # or backup existing directory as data_old
        if not os.path.exists('./data'):
            os.mkdir('./data')
        else:
            shutil.move('./data', './data_old')
            os.mkdir('./data')

        if self._crawl_type == 'bfs':
            # Crawl the pages using - *BFS*
            self.crawl_pages_bfs(self._root_url, self._depth, 0)
        elif self._crawl_type == 'dfs':
            # Crawl the pages using - *DFS*
            self.crawl_pages_dfs(self._root_url, self._depth, 0)
        else:
            logging.error('Unknown crawler type: {}, valid options [dfs|bfs]'.format(self._crawl_type))
            sys.exit(-1)

        # Completed crawling - i.e. Reached either url limit or depth limit
        self.write_url_files()
        logging.info('Completed crawling {} as per the requested parameters.'.format(self._base_url + self._root_url))
        logging.info('Reached a depth of: {}'.format(self._depth))
        
URL_BASE = 'https://en.wikipedia.org'
ROOT_URL = '/wiki/Tropical_cyclone'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl wikipedia starting at the provided root_url")
    parser.add_argument("root_url", type=str, help="URL at which to start crawler")
    parser.add_argument("url_limit", type=int, help="Stop crawler when url_limit is reached")
    parser.add_argument("depth_limit", type=int, help="Stop crawler when depth_limit is reached")
    parser.add_argument("delay", type=int, help="Delay between each get request to wikipedia in seconds (min 1 second)")
    parser.add_argument("-c", "--crawl", type=str, help="Crawl the pages again, using the specified search pattern [dfs|bfs]")
    parser.add_argument("-k", "--keyword", type=str, help="If keyword is provided, the crawler operates in focused mode, filtering by keyword.")
    
    args = parser.parse_args()

    crawl_type = 'bfs'
    if args.crawl:
        crawl_type = args.crawl.strip().lower()
    else:
        print("Type of crawler not specified, defaulting to BFS - Breadth First Search crawler")

    root_url = args.root_url
    url_limit = args.url_limit
    depth_limit = args.depth_limit
    delay = args.delay
    if args.keyword:        
        keyword = args.keyword
    else:
        keyword = None

    if (root_url.startswith('https://en.wikipedia.org')):
        root_url = root_url.replace('https://en.wikipedia.org','')
    else:
        print("Unexpected root_url, expected url starting with 'https://en.wikipedia.org'")
        sys.exit(1)
    
    if (delay < 1):
        print("Delay set to 1 second")
        delay = 1

    if keyword is None:
        # Non focussed mode
        crawler = Crawler(URL_BASE, root_url, urls_limit=url_limit, depth_limit=depth_limit, delay=delay, crawl_type=crawl_type)
        crawler.start()
    else:
        # Focused crawler
        crawler = Crawler(URL_BASE, root_url, urls_limit=url_limit, depth_limit=depth_limit, delay=delay, crawl_type=crawl_type, keyword=keyword)
        crawler.start()
