#!/usr/bin/env python3

# CS6200 - Fall 2017
# Project
# Author: Shreysa Sharma
# Date: November 12th, 2017
#       December 2nd,  2017

import re
import os
import sys
import shutil
import pickle
import string
import logging
import argparse
import operator
from bs4 import BeautifulSoup

class Indexer:
    def __init__(self, data_directory, options):
        self._data_directory = data_directory
        self._urls_map = []
        self._list_of_files = []
        self._list_of_doc_ids = []
        self._case_folding = options['case_folding']
        self._punctuation = options['filter_punctuation']
        self._stop_list_op = options['stop_list']
        self._stop_list = ["the", "of", "and", "in", "to", "a", "on","is", "from", "as", "for", "was", "by", "with", "s"]

        # Setup logging
        '''
        The logging code was referenced from :
        https://stackoverflow.com/questions/40858658/python-logging-to-stdout-and-log-file
        '''
        logging.basicConfig(filename='run_index.log', level=logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        root_log = logging.getLogger()
        root_log.setLevel(logging.INFO)

        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.INFO)
        channel.setFormatter(formatter)

        root_log.addHandler(channel)

        logging.info('Reading stored files from: {}'.format(self._data_directory))
        logging.info('\tCase Folding: {:b}'.format(self._case_folding))
        logging.info('\tFilter Punctuation: {:b}'.format(self._punctuation))
        logging.info('\tStop list: {:b}'.format(self._stop_list_op))

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
                doc_id = url.split('/')[-1].lower()
                self._list_of_doc_ids.append(doc_id)
                self._urls_map.append({
                    'url': url,
                    'cached_file_name': cached_file_name,
                    'doc_id': doc_id
                    })
        
        number_of_docs = len(self._urls_map)
        logging.info('Number of url -> cached_data_file mappings: ' + str(number_of_docs))

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

    def read_file(self, file_name):
        with open(file_name, 'r') as f:
            return f.read()

    def clean_up(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        
        # Get the content div
        content_div = soup.find(id='bodyContent').find(id='mw-content-text')
        
        # Remove all table elements
        for table in content_div.find_all('table'):
            table.extract()
        
        # Remove all links
        for a in content_div.find_all('a'):
            a.extract()

        # Remove all formulas   
        for span in content_div.find_all("span", class_="mwe-math-element"):
            span.extract()

        # Remove non ascii characters
        processed_text = content_div.get_text().encode('ascii', errors='ignore').decode()
        
        # Remove all citations [1], [2] etc
        processed_text = re.sub('\[[A-za-z0-9\s]+\]', '', processed_text)
        
        # If casefolding is requested
        if(self._case_folding):
            processed_text = processed_text.casefold()
        
        # If filtering punctuation is requested
        if(self._punctuation):                 
            punctuation_pattern1 = '[\"$\()\[\]\{\}\'#*&:;<=>?@_`+!~/|]+'
            punctuation_pattern2 = '[\.,%-]+\s'
            punctuation_pattern3 = '\s[\.,%-]+'
            processed_text = re.sub(punctuation_pattern1, ' ', processed_text)
            processed_text = re.sub(punctuation_pattern2, ' ', processed_text)
            processed_text = re.sub(punctuation_pattern3, '', processed_text)
        
        if(self._stop_list_op):
            filtered_words = []
            for word in processed_text.split():
                if word not in self._stop_list:
                    filtered_words.append(word)
            
            processed_text = ' '.join(filtered_words)
        
        return processed_text

    def save_file(self, text, file_name):
        with open(file_name, 'w') as f:
            f.write(text)
        
    def get_term_frequency(self, file_contents, n):
        term_frequency = {}
        words = file_contents.split()
        for i in range(len(words)):
            term = ' '.join(words[i:i+n])
            term_frequency.setdefault(term, 0)
            term_frequency[term] += 1

        return term_frequency

    def get_term_frequencies(self, file_contents):
        term_frequency_1 = {}
        term_frequency_2 = {}
        term_frequency_3 = {}
        words = file_contents.split()
        num_tokens = len(words)
        for i in range(num_tokens):
            term_1_gram = words[i]
            term_2_gram = ' '.join(words[i:i+2])
            term_3_gram = ' '.join(words[i:i+3])
            term_frequency_1.setdefault(term_1_gram, 0)
            term_frequency_2.setdefault(term_2_gram, 0)
            term_frequency_3.setdefault(term_3_gram, 0)
            term_frequency_1[term_1_gram] += 1
            term_frequency_2[term_2_gram] += 1
            term_frequency_3[term_3_gram] += 1
        
        data = {
            'term_frequency_1': term_frequency_1,
            'term_frequency_2': term_frequency_2,
            'term_frequency_3': term_frequency_3,
            'num_tokens': num_tokens
        }

        return data

        # return (term_frequency_1, term_frequency_2, term_frequency_3)

    def create_inverted_index(self, term_frequencies):
        index = {}
        for doc_id, tf in term_frequencies:
            for word, word_freq_in_doc in tf.items():
                index.setdefault(word, [])
                index[word].append((doc_id, word_freq_in_doc))

        return index
    
    def clean_up_cacm(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        return soup.find('html').find('pre').get_text().strip()

    def generate_index_from_exisiting_corpus(self):
        doc_id_num_tokens = {}
        one_gram_term_freqs = []

        files_list = os.listdir(self._data_directory)
        list_of_files = [f for f in files_list if f.endswith('html')]

        for current_doc in list_of_files:
            with open(os.path.join(self._data_directory, current_doc), 'r') as f:
                current_doc_id = current_doc.replace('.html','')
                logging.info('Processing doc: {}'.format(current_doc_id))
                processed_data = f.read()
                processed_data = self.clean_up_cacm(processed_data)
                term_freq_data = self.get_term_frequencies(processed_data)
                one_gram_term_freqs.append((current_doc_id, term_freq_data['term_frequency_1']))
                doc_id_num_tokens[current_doc_id] = term_freq_data['num_tokens']

        logging.info('Creating 1-Gram inverted indices')
        index_1_gram = self.create_inverted_index(one_gram_term_freqs)

        logging.info('Saving index data to file')
        index_file_name = 'index_saved.pickle'
        self.save_index(index_1_gram, doc_id_num_tokens, one_gram_term_freqs, index_file_name)

    def generate_index(self):
        self.init()

        doc_id_num_tokens = {}
        one_gram_term_freqs = []
        two_gram_term_freqs = []
        three_gram_term_freqs = []

        # Create directory for storing run data
        # or backup existing directory as data_old
        if not os.path.exists('./corpus'):
            os.mkdir('./corpus')
        else:
            shutil.move('./corpus', './corpus_old')
            os.mkdir('./corpus')

        # Process all the cached files
        for entry in self._urls_map:
            current_doc_id = entry['doc_id']
            cached_file_name = entry['cached_file_name']
            url = entry['url']
            corpus_file_name = 'corpus/' + current_doc_id + '.txt'

            logging.info('Processing doc: {}'.format(current_doc_id))

            with open(self._data_directory + '/' + cached_file_name, 'r') as f:
                data = f.read()
                processed_data = self.clean_up(data)
                self.save_file(processed_data, corpus_file_name)
                # one_tf, two_tf, three_tf = self.get_term_frequencies(processed_data)
                term_freq_data = self.get_term_frequencies(processed_data)
                one_gram_term_freqs.append((current_doc_id, term_freq_data['term_frequency_1']))
                two_gram_term_freqs.append((current_doc_id, term_freq_data['term_frequency_2']))
                three_gram_term_freqs.append((current_doc_id, term_freq_data['term_frequency_3']))
                doc_id_num_tokens[current_doc_id] = term_freq_data['num_tokens']

        logging.info('Creating 1-Gram inverted indices')
        index_1_gram = self.create_inverted_index(one_gram_term_freqs)
        logging.info('Creating 2-Gram inverted indices')
        index_2_gram = self.create_inverted_index(two_gram_term_freqs)
        logging.info('Creating 3-Gram inverted indices')
        index_3_gram = self.create_inverted_index(three_gram_term_freqs)

        logging.info('Writing inverted indices tables')
        self.write_tables(index_1_gram,'index_1')
        self.write_tables(index_2_gram,'index_2')
        self.write_tables(index_3_gram,'index_3')

        logging.info('Writing stop list file')
        self.generate_stop_list(index_1_gram, 'stop_list')

        logging.info('Saving index data to file')
        index_file_name = 'index_saved.pickle'
        self.save_index(index_1_gram, doc_id_num_tokens, one_gram_term_freqs, index_file_name)

    def save_index(self, index, num_tokens_in_docs, one_gram_term_freqs, file_name):
        '''
        Save the index to a serialized file.
        Can be loaded using `load_index`.
        '''
        data = {
            'index': index,
            'num_token_in_doc': num_tokens_in_docs,
            'term_freqs_by_doc': one_gram_term_freqs,
            'options': {
                'case_folding': self._case_folding,
                'punctuation': self._punctuation,
                'use_stop_list': self._stop_list_op,
                'stop_list': self._stop_list
            }
        }
        pickle.dump(data, open(file_name, 'wb'))

    def load_index(self, file_name):
        '''
        Load the index from a serialized file
        '''

        # Read saved data
        data = pickle.load(open(file_name, 'rb'))

        # Compute term frequences from the stored index
        term_freqs = {}
        for key, value in data['index'].items():
            freq_sum = 0
            for entry in value:
                freq_sum += entry[1]
            term_freqs[key] = freq_sum

        # Get the document frequency for each term
        doc_freq = {}
        for key, value in data['index'].items():
            doc_ids = [entry[0] for entry in value]
            doc_freq[key] = doc_ids
        
        tf_in_doc_map = {}
        for doc_id, tfs in data['term_freqs_by_doc']:
            tf_in_doc_map[doc_id] = tfs

        # Create data structure with all necessary data
        read_data = {
            'index': data['index'],
            'num_tokens_in_doc': data['num_token_in_doc'],
            'term_freqs_by_doc': tf_in_doc_map,
            'options': data['options'],
            'tf': term_freqs,
            'df': doc_freq
        }

        return read_data

    def generate_stop_list(self, index, file_name):
        term_freqs = {}
        total_freq_sum = 0
        for key, value in index.items():
            freq_sum = 0
            for entry in value:
                freq_sum += entry[1]
            term_freqs[key] = freq_sum
            total_freq_sum += freq_sum

        sorted_freq = sorted(term_freqs.items(), key=operator.itemgetter(1), reverse=True)

        with open(file_name + '.txt', 'w') as f:
            f.write('stop_list_words\n')
            f.write('{}\n'.format(str([key for key, value in sorted_freq[0:15]])[1:-1]))

        stop_list_by_percentage = []
        threshold_percentage = 0.005
        print(total_freq_sum)
        for key, value in sorted_freq:
            percent = (float(value)/float(total_freq_sum))
            if (percent > threshold_percentage):
                stop_list_by_percentage.append(key)
            else:
                break
        
        with open(file_name + '_by_percentage.txt', 'w') as f:
            f.write('stop_list_words_by_percentage\n')
            f.write('{}\n'.format(str(stop_list_by_percentage)[1:-1]))

    def write_tables(self, index, file_name_prefix):
        '''
        Write the index to a human readable ascii file.
        This method writes two tables. 

        <file_name_prefix>_term_index.txt - Table as described in Task 2
        <file_name_prefix>_term_freq_table.txt - Containing the term | tf
        <file_name_prefix>_doc_freq_table.txt - Containing term | doc_id | tf
        '''
        t1name = file_name_prefix + '_term_index.txt'
        t2name = file_name_prefix + '_term_freq_table.txt'
        t3name = file_name_prefix + '_doc_freq_table.txt'

        term_freqs = {}
        for key, value in index.items():
            freq_sum = 0
            for entry in value:
                freq_sum += entry[1]
            term_freqs[key] = freq_sum

        sorted_freq = sorted(term_freqs.items(), key=operator.itemgetter(1), reverse=True)
        doc_freq = sorted(index.items(), key=operator.itemgetter(0))

        with open(t1name, 'w') as table1:
            table1.write('term,term_frequencies\n')
            for entry in doc_freq:
                doc_tfs = str(entry[1])[1:-1]
                doc_tfs = doc_tfs.replace("'",'')
                table1.write('{},{}\n'.format(entry[0], doc_tfs))

        with open(t2name, 'w') as table2:
            table2.write('term,term_frequency\n')
            for entry in sorted_freq:
                table2.write('{},{}\n'.format(entry[0], entry[1]))

        with open(t3name, 'w') as table3:
            table3.write('term,doc_ids,doc_frequency\n')
            for key, value in doc_freq:
                doc_ids = [entry[0] for entry in value]
                table3.write('{},{},{}\n'.format(key, str(doc_ids)[1:-1].replace("'",''), len(doc_ids)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an inverted index from the provided dataset.")
    parser.add_argument("data_directory", type=str, help="Directory in which the crawled data is stored")
    parser.add_argument("-c", "--case-folding", help="Convert corpus to lower case", action='store_true')
    parser.add_argument("-p", "--filter-punctuation", help="Strip all non-relevant punctuation from the corpus", action='store_true')
    parser.add_argument("-s", "--stop-list", help="Use Stop list to filter words", action='store_true')
    parser.add_argument("-n", "--no-clean", help="Do not clean the files in the data directory, already cleaned.", action='store_true')
    args = parser.parse_args()


    data_directory = args.data_directory
    options = {'case_folding': False, 'filter_punctuation': False, 'stop_list': False}

    if args.case_folding:
        options['case_folding'] = True

    if args.filter_punctuation:
        options['filter_punctuation'] = True
    
    if args.stop_list:
        options['stop_list'] = True

    indexer = Indexer(data_directory, options)
    if args.no_clean:
        indexer.generate_index_from_exisiting_corpus()
    else:
        indexer.generate_index()
