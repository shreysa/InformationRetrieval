#!/usr/bin/env python3

# CS6200 - Fall 2017
# HW 2 
# Author: Shreysa Sharma
# Date: October 25th, 2017

import os
import sys
import math
import pprint
import logging
import argparse
import operator
from bs4 import BeautifulSoup

class Graph:

    def __init__(self, data_directory):
        self._data_directory = data_directory
       
        self._urls_map = []
        self._sink_pages = []
        self._list_of_files = []
        self._list_of_doc_ids = []
        self._perplexity_history = []
              
        self._graph = {}
        self._page_rank = {}
        self._page_num_outgoing = {}
        self._page_num_incoming = {}
        
        self._converged_counter = 0

        # Setup logging
        '''
        The logging code was referenced from :
        https://stackoverflow.com/questions/40858658/python-logging-to-stdout-and-log-file
        '''

        logging.basicConfig(filename='run_process.log', level=logging.INFO)
        root_log = logging.getLogger()
        root_log.setLevel(logging.INFO)

        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        channel.setFormatter(formatter)
        root_log.addHandler(channel)
    
    def init(self):

        # Get all the *.html files in the data_directory
        files_list = os.listdir(self._data_directory)
        self._list_of_files = [f for f in files_list if f.endswith('html')]

        logging.info('Number of files in data_directory: ' + str(len(self._list_of_files)))

        # Read and process the file that maps from url -> cached_file
        url_to_file_map_file_name = self._data_directory + '/url_to_file_map.csv'
        logging.info('Reading map from url->cached_file: {}'.format(url_to_file_map_file_name))
        with open(url_to_file_map_file_name) as f:
            for line in f:
                line_split = line.strip().split(';data/')
                url = line_split[0]
                cached_file_name = line_split[1]
                doc_id = url.split('/')[-1]
                self._list_of_doc_ids.append(doc_id)
                self._urls_map.append({
                    'url': url,
                    'cached_file_name': cached_file_name,
                    'doc_id': doc_id
                    })
        
        number_of_docs = len(self._urls_map)
        logging.info('Number of url -> cached_data_file mappings: ' + str(number_of_docs))

        # Initial page rank PR(p) = 1 / N
        for entry in self._urls_map:
            doc_id = entry['doc_id']
            self._page_rank[doc_id] = 1 / number_of_docs

        # Check data integrity
        self.check_files()

    def check_files(self):
        logging.info('Checking file mapping and cached files')
        already_mapped = []
        num_warnings = 0
        for i, entry in enumerate(self._urls_map):
            doc_id = entry['doc_id']
            cached_file_name = entry['cached_file_name']
            if cached_file_name not in already_mapped:
                already_mapped.append(cached_file_name)
            else:
                logging.warn('Another doc_id already refers to this cached file. doc_id: {}, cached_file_name: {}'.format(doc_id, cached_file_name))
                num_warnings += 1
            if cached_file_name not in self._list_of_files:
                logging.warn("[" + str(i) + "] Missing file: " + cached_file_name + " doc_id: " + doc_id)
                num_warnings += 1
            
            # Quit if the number of warnings exceed the threshold
            # this can happen quite a few files have been deleted from the data folder
            if num_warnings > 50:
                logging.fatal('Warning limit exceeded, too many missing files in data folder - Please re-run the crawler, then re-run this script.')
                sys.exit(-1)
    
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
    
    def process_links(self, found_links):
        '''
        The link is processes to get the href, remove the administrative and 
        the links that point to the same page. The links with wiki in it are added,
        also a check is done for the keywords if any have been provided
        '''
        doc_ids_container = []
        for i, link in enumerate(found_links):
            url = self.process_url(link.get('href'))
            if url is None:
                continue
            elif '#' in url or ':' in url:
                continue
            elif url.startswith('/wiki/'):
                doc_ids_container.append(url.split('/')[-1])
            else:
                continue
        return doc_ids_container
    
    def get_doc_ids_from_cached_file(self, file_name):
        logging.info("Processing file: {}".format(file_name))
        with open(file_name, 'r') as cached_file:
            soup = BeautifulSoup(cached_file.read(), 'html.parser')
            content_div = soup.find(id='bodyContent').find(id="mw-content-text")
            found_links = content_div.find_all('a')
            doc_ids_container = self.process_links(found_links)
            doc_ids_relevant = []

            # Filter the list - only consider doc_ids that appear the csv file
            # ignore the rest. 
            for entry in  set(doc_ids_container):
                if entry in self._list_of_doc_ids:
                    doc_ids_relevant.append(entry)
            
            return doc_ids_relevant

    def build(self):
        # Process all the cached files
        for entry in self._urls_map:
            current_doc_id = entry['doc_id']
            cached_file_name = entry['cached_file_name']
            # Find all the doc_ids in the current page. ie. out going links from current page
            doc_ids_in_page = self.get_doc_ids_from_cached_file(self._data_directory + '/' + cached_file_name)

            # Store the number of outgoing links from this page
            self._page_num_outgoing[current_doc_id] = len(doc_ids_in_page)

            # if the page has no relevant outgoing links, it is considered a sink
            if len(doc_ids_in_page) == 0:
                self._sink_pages.append(current_doc_id)

            # Add the current_doc_id as an incoming link each of the relevant doc_ids found in page
            for d_id in doc_ids_in_page:
                if d_id not in self._list_of_doc_ids:
                    logging.warn("This filter has already been applied, possible bug")
                    continue
                elif d_id in self._graph:
                    if current_doc_id not in self._graph[d_id]:
                        self._graph[d_id].append(current_doc_id)
                else:
                    self._graph[d_id] = [current_doc_id]
        
        # Cache the number of incoming links to the page/doc_id
        for key, value in self._graph.items():
            self._page_num_incoming[key] = len(value)
    
    def compute_perplexity(self):
        sum_page_rank = 0.0
        for _, pr in self._page_rank.items():
            sum_page_rank += pr * math.log2(pr)
        shannon_entropy = -sum_page_rank
        perplexity = 2**shannon_entropy
        return perplexity

    def compute_page_rank(self):
        num_iterations = 0
        damping_factor = 0.85
        perplexity = self.compute_perplexity()
        self._perplexity_history.append(perplexity)
        converged = False

        num_pages = len(self._urls_map)

        while not converged:
            sink_pr = 0
            new_page_rank_store = {}
            for sink_page in self._sink_pages:
                sink_pr += self._page_rank[sink_page]

            # To prevent an infinite loop
            if num_iterations > 500:
                logging.fatal('Unable to converge, quitting.')
                sys.exit(-1)
            
            # Compute new page rank score
            for page in self._urls_map:
                current_doc_id = page['doc_id']
                new_page_rank = (1.0 - damping_factor) / num_pages
                new_page_rank += damping_factor * (sink_pr / num_pages)
                for incoming_link in self._graph[current_doc_id]:
                    PRq = self._page_rank[incoming_link]
                    Lq = self._page_num_outgoing[incoming_link]
                    new_page_rank += damping_factor * (PRq / Lq)
                new_page_rank_store[current_doc_id] = new_page_rank

            # Update the page rank scores 
            for page in self._urls_map:
                current_doc_id = page['doc_id']
                self._page_rank[current_doc_id] = new_page_rank_store[current_doc_id]
            
            # Compute new perplexity and check if converged
            perplexity = self.compute_perplexity()
            num_converged_entries = 0
            if (len(self._perplexity_history) >= 4):
                for i in range(0, 4):
                    perplexity_at_i = self._perplexity_history[-(i + 1)]
                    if math.fabs(perplexity_at_i - perplexity) < 1.0:
                        num_converged_entries += 1
                if (num_converged_entries == 4):
                    converged = True
            self._perplexity_history.append(perplexity)

            logging.info('[{}] - perplexity: {:f} - converged: {}'.format(num_iterations, perplexity, converged))
            num_iterations += 1

    def compute_stats_for_graph(self):
        '''
        This method updates object with the state required 
        to compute page rank.
        '''

        if len(self._graph) == 0:
            logging.error("Graph is empty!")
            sys.exit(-1)
        
        number_of_docs = len(self._graph)
        inverse_num_docs = 1.0 / float(number_of_docs)

        # Initialize starting values
        for key in self._graph.keys():
            self._page_num_incoming[key] = 0
            self._page_num_outgoing[key] = 0
            self._page_rank[key] = inverse_num_docs
            self._urls_map.append({'doc_id': key})

        # Update with actual values
        for key, value in self._graph.items():
            for entry in value:
                self._page_num_outgoing[entry] += 1
            self._page_num_incoming = len(value)
        
        # Check which pages are sinks
        self._sink_pages = []
        for key in self._graph.keys():
            if self._page_num_outgoing[key] == 0:
                self._sink_pages.append(key)
    

    def generate_test_graph(self):
        # Test Graph Defn
        self._graph['A'] = ['D', 'E', 'F']
        self._graph['B'] = ['A', 'F']
        self._graph['C'] = ['A', 'B', 'D']
        self._graph['D'] = ['B', 'C']
        self._graph['E'] = ['B', 'C', 'D', 'F']
        self._graph['F'] = ['A', 'B', 'D']

        self.compute_stats_for_graph()
    
    def save_graph(self, file_name):
        '''
        Save the graph to the specified file, the format is as specified 
        in the HW2 PDF.
        '''
        with open(file_name, 'w') as f:
            for key, value in self._graph.items():
                f.write("{} ".format(key))
                for entry in value:
                    f.write("{} ".format(entry))
                f.write("\n")
    
    def load_graph(self, file_name):
        '''
        Load the graph saved using save_graph, and compute stats 
        necessary to calculate page_rank
        FIXME: Expand with additional sanity checks
        '''
        with open(file_name, 'r') as f:
            for line in f:
                items = line.strip().split()
                self._graph[items[0]] = items[1:]
        self.compute_stats_for_graph()

    def plot_perplexity_history(self, file_name):
        try:
            import matplotlib.pyplot as plt
            plt.plot(range(0,len(self._perplexity_history)),self._perplexity_history);
            plt.xlabel('Number of Iterations')
            plt.ylabel('Perplexity')
            plt.title('Perplexity History')
            plt.savefig(file_name)
        except ImportError:
            logging.info('Unable to plot, matplotlib is not installed.')
    
    def get_sorted_page_ranks(self, num_top):
        # code adapted from the solution presented in:
        # https://stackoverflow.com/questions/613183/how-to-sort-a-dictionary-by-value#613218
        sorted_ranks = sorted(self._page_rank.items(), key=operator.itemgetter(1), reverse=True)
        range_end = num_top
        if range_end > len(sorted_ranks):
            range_end = len(sorted_ranks)
        return (doc_id for doc_id in sorted_ranks[0:range_end])

    def get_sources_sinks_ratios(self):
        '''
        Returns the proportion of source and sink pages
        '''
        num_pages = len(self._graph)
        num_sinks = len(self._sink_pages)
        num_sources = 0
        for key, value in self._graph.items():
            if len(value) == 0:
                num_sources += 1
        
        source_ratio = num_sources / num_pages
        sink_ratio = num_sinks / num_pages

        return (source_ratio, sink_ratio)
    
    def get_sorted_num_incoming_links(self, num_top):
        # code adapted from the solution presented in:
        # https://stackoverflow.com/questions/613183/how-to-sort-a-dictionary-by-value#613218
        num_incoming_links = {}
        for key, val in self._graph.items():
            num_incoming_links[key] = len(val)
        sorted_incoming_links = sorted(num_incoming_links.items(), key=operator.itemgetter(1), reverse=True)
        
        range_end = num_top
        if range_end > len(sorted_incoming_links):
            range_end = len(sorted_incoming_links)
        return (doc_id for doc_id in sorted_incoming_links[0:range_end])
          
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a graph from the data collected by the crawler, and compute page rank.")
    parser.add_argument("data_directory", type=str, help="Directory in which the crawled data is stored")
    parser.add_argument("run_name", type=str, help="Give the name a run, the output files will use this")
    parser.add_argument("-n", "--num-top", type=int, help="Number of top results to show")
    parser.add_argument("--test", help="Run the test graph as specified in Hw2 pdf. data_directory is ignored", action='store_true')
    args = parser.parse_args()

    run_name = args.run_name
    data_directory = args.data_directory
    num_top = 10
    if args.num_top:
        num_top = args.num_top

    graph = None
    if args.test:
        # Run Test
        graph = Graph(None)
        graph.generate_test_graph()
    else:
        # Build graph and compute PageRank values
        graph = Graph(data_directory)
        graph.init()
        graph.build()
    
    # Save Graph, Compute PageRank and Write Results
    graph.save_graph(run_name + '_graph.txt')
    graph.compute_page_rank()
    # Disabled, matplotlib could run into issues on MacOS
    #graph.plot_perplexity_history(run_name + '_perplexity_history.png')

    # Get Results
    page_rank_top_links = graph.get_sorted_page_ranks(num_top)
    num_incoming_top_links = graph.get_sorted_num_incoming_links(num_top)
    source_ratio, sink_ratio = graph.get_sources_sinks_ratios()

    # Write Results
    with open(run_name + '_results.txt', 'w') as f:
        f.write('Sources and Sinks\n')
        f.write('-----------------\n')
        f.write('Source Ratio : {:f}\n'.format(source_ratio))
        f.write('Sink Ratio   : {:f}\n'.format(sink_ratio))
        f.write('\n')
        f.write('PageRank results\n')
        f.write('----------------\n')
        for i, entry in enumerate(page_rank_top_links):
            f.write('[{}] | PR: {:f} | {} \n'.format(i, entry[1], entry[0]))
        f.write('\n')
        f.write('Num incoming links results\n')
        f.write('--------------------------\n')
        for i, entry in enumerate(num_incoming_top_links):
            f.write('[{}] | num_incoming_links: {} | {}\n'.format(i, entry[1], entry[0]))
    
