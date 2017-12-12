#!/usr/bin/env python3

# CS6200 - Fall 2017
# Project
# Author: Shreysa Sharma
# Date: December 2nd,  2017

import os
import re
import sys
import math
import pickle
import logging
import argparse
import operator
from xml.dom import minidom

class BM25:

    def __init__(self, saved_index_file_name, use_prf, stop_list_file):
        self._saved_index_file_name = saved_index_file_name
        self._use_prf = use_prf
        self._stop_list_file = stop_list_file
        self._stop_list = {}
        self._indexed_data = {}

        if self._stop_list_file != '':
            with open(self._stop_list_file, 'r') as f:
                for line in f:
                    self._stop_list[line.strip()] = True

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

        logging.info("Reading saved index from: '{}'".format(self._saved_index_file_name))
        self.load_index_file()
        self._indexed_options = self._indexed_data['options']

        logging.info('Index data read - index was created with the following options:')
        logging.info('\tCase Folded: {:b}'.format(self._indexed_options['case_folding']))
        logging.info('\tFiltered Punctuation: {:b}'.format(self._indexed_options['punctuation']))
        logging.info('\tUsed Stop list: {:b}'.format(self._indexed_options['use_stop_list']))
        if self._indexed_options['use_stop_list']:
            logging.info('\tStop list entries: {:b}'.format(self._indexed_options['stop_list']))

        self.set_scoring_constants()

    def set_scoring_constants(self):
        if self._indexed_data == {}:
            logging.error('Index data not loaded')

        logging.info('Setting constants for the BM25 algorithm')

        # Constants - BM25
        self._k1 = 1.2
        self._k2 = 100
        self._b = 0.75
        self._r = 0
        self._R = 0

        # Constants - Pseudo-Relevance Feedback
        self._prf_num_docs = 10   # Number of top documets to consider
        self._prf_num_terms = 30  # Number of terms to expand query by
        self._prf_num_terms_per_doc = int(self._prf_num_terms / self._prf_num_docs)
        self._prf_num_iterations = 1 # Number of PRF iterations to run

        # Compute meanDocLength
        doc_lengths = self._indexed_data['num_tokens_in_doc']
        self._num_docs_in_corpus = len(doc_lengths)

        num_tokens_total = 0
        for _, num_tokens_in_doc in doc_lengths.items():
            num_tokens_total += num_tokens_in_doc

        self._avg_tokens_in_doc = math.floor(num_tokens_total / self._num_docs_in_corpus)

        logging.info('\tBM25 Constants')
        logging.info('\t k1 = {}'.format(self._k1))
        logging.info('\t k2 = {}'.format(self._k2))
        logging.info('\t b  = {}'.format(self._b))
        logging.info('\t r  = {}'.format(self._r))
        logging.info('\t R  = {}\n'.format(self._R))
        logging.info('\tPseudo-Relevance Feedback Parameters')
        logging.info('\t Num Docs to consider (k) = {}'.format(self._prf_num_docs))
        logging.info('\t Num terms to expand query by = {}'.format(self._prf_num_terms))
        logging.info('\t Num terms per top doc = {}\n'.format(self._prf_num_terms_per_doc))
        logging.info('\tnum_docs_in_corpus = {}'.format(self._num_docs_in_corpus))
        logging.info('\tavg_tokens_in_doc = {}'.format(self._avg_tokens_in_doc))
    
    def get_system_name(self):
        case_folding = self._indexed_options['case_folding']
        punctuation = self._indexed_options['case_folding']
        stop_list = self._indexed_options['use_stop_list']
        system_name = 'NOSTEM'
        
        if case_folding:
            system_name = system_name + '_CF'
        else:
            system_name = system_name + '_NOCF'

        if punctuation:
            system_name = system_name + '_PUNC'
        else:
            system_name = system_name + '_NOPUNC'
        
        if stop_list:
            system_name = system_name + '_STOP'
        else:
            system_name = system_name + '_NOSTOP'

        return system_name

    def compute_K(self, doc_id):
        num_tokens_in_doc = self._indexed_data['num_tokens_in_doc'][doc_id]
        return self._k1 * (1 - self._b + ((self._b * num_tokens_in_doc) / self._avg_tokens_in_doc))
    
    def get_term_freq_in_doc(self, term, doc_id):
        try:
            return self._indexed_data['index'][term][doc_id]
        except KeyError:
            return 0

    def compute_tfidf_score(self, term, doc_id):
        try:
            tf_in_doc = self._indexed_data['index'][term][doc_id]
            num_terms_in_doc = self._indexed_data['num_tokens_in_doc'][doc_id]
            tf = tf_in_doc / num_terms_in_doc
            df_term = 0
            if term in self._indexed_data['df']:
                df_term = len(self._indexed_data['df'][doc_id])
            idf = math.log(df_term / self._num_docs_in_corpus)
            return tf * idf
        except KeyError:
            return 0
    
    def get_doc_freq(self, df, term):
        '''
        Return the number of documents that a particular term 
        appears in. 
        '''
        try:
            return len(df[term])
        except KeyError:
            return 0

    def compute_bm25_score(self, parsed_query, doc_id):
        qf = parsed_query['qf']
        query_terms = parsed_query['query']
        tf = self._indexed_data['tf']
        df = self._indexed_data['df']

        total = 0
        for query_term in query_terms.split():
            n = self.get_doc_freq(df, query_term)
            if (n > self._num_docs_in_corpus):
                # Should not happen - added as a sanity check
                n = self._num_docs_in_corpus
            # x     = log( ((r+0.5)/(R-r+0.5)) / ((n-r+0.5)/(N-n-R+r+0.5)) )
            numer_x = ((self._r + 0.5) / (self._R - self._r + 0.5))
            denom_x = ((n - self._r + 0.5) / (self._num_docs_in_corpus - n - self._R + self._r + 0.5))
            x = math.log(numer_x / denom_x)

            # y     = ((k1+1)*f)/(K+f)
            tf_in_doc = self.get_term_freq_in_doc(query_term, doc_id)
            # y = ((self._k1 + 1) * tf[query_term]) / (self.compute_K(doc_id) + tf[query_term])
            y = ((self._k1 + 1) * tf_in_doc) / (self.compute_K(doc_id) + tf_in_doc)
            
            #z     = ((k2+1)*qf)/(k2+qf)
            z = ((self._k2 + 1) * qf[query_term]) / (self._k2 + qf[query_term])

            total = total + (x * y * z)
        
        return total
    
    def run_search(self, parsed_query):
        num_tokens_in_doc = self._indexed_data['num_tokens_in_doc']
        scores = {}
        for doc_id, _ in num_tokens_in_doc.items():
            scores[doc_id] = self.compute_bm25_score(parsed_query, doc_id)
        
        return sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

    def load_index_file(self):
        '''
        Load the index from a serialized file
        '''

        # Read saved data
        data = pickle.load(open(self._saved_index_file_name, 'rb'))

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

        index_mod = {}
        for term, doc_freqs in data['index'].items():
            docs_map = {}
            for k, v in doc_freqs:
                docs_map[k] = v
            data['index'][term] = docs_map
        
        tf_in_doc_map = {}
        for doc_id, tfs in data['term_freqs_by_doc']:
            tf_in_doc_map[doc_id] = tfs

        # Create data structure with all necessary data
        self._indexed_data = {
            'index': data['index'],
            'num_tokens_in_doc': data['num_token_in_doc'],
            'term_freqs_by_doc': tf_in_doc_map,
            'options': data['options'],
            'tf': term_freqs,
            'df': doc_freq
        }
    
    def get_top_terms_in_doc_tfidf(self, doc_id, tf_for_doc):
        tf_idf_scores = {}

        # Compute TF-IDF Scores for all terms in Doc doc_id
        for term, freq in tf_for_doc.items():
            tf_idf_term_score = self.compute_tfidf_score(term, doc_id)
            tf_idf_scores[term] = tf_idf_term_score
        
        # Sort terms in descending order - using TF-IDF scores
        sorted_scores = sorted(tf_idf_scores.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_scores

    def expand_query_for_prf(self, query_terms, results):
        '''
        Expand query for Pseudo-Relevance feedback
        1. Pick the top self._prf_num_docs from returned results
        2. Pick the top self._prf_num_terms_per_doc terms per doc (sorted by tf-idf)
        3. Expand the query terms with the additional terms and re-run the search
        '''
        top_docs = results[0:self._prf_num_docs]
        expanded_terms = []
        for entry in top_docs:
            doc_id = entry[0]
            tf_for_doc = self._indexed_data['term_freqs_by_doc'][doc_id]
            top_terms = self.get_top_terms_in_doc_tfidf(doc_id, tf_for_doc)
            ctr = 0

            # If there is a stop list ensure the top terms are not in the list
            if self._stop_list_file != '':
                for term in top_terms:
                    if term[0] in self._stop_list:
                        continue
                    else:
                        ctr += 1
                        expanded_terms.append(term)
    
                    if ctr >= self._prf_num_terms_per_doc:
                        break
            else:
                expanded_terms += top_terms[0:self._prf_num_terms_per_doc]
        
        return query_terms + ' ' + ' '.join([entry[0] for entry in expanded_terms])
    
    def remove_punctuation(self, query):
        punctuation_pattern1 = '[\"$\()\[\]\{\}\'#*&:;<=>?@_`+!~/|]+'
        punctuation_pattern2 = '[\.,%-]+\s'
        punctuation_pattern3 = '\s[\.,%-]+'
        processed_text = re.sub(punctuation_pattern1, ' ', query)
        processed_text = re.sub(punctuation_pattern2, ' ', processed_text)
        processed_text = re.sub(punctuation_pattern3, '', processed_text)
        return processed_text

    def parse_query(self, query_terms):
        query_terms = self.remove_punctuation(query_terms)
        qf = {}
        for token in query_terms.split():
            qf.setdefault(token, 0)
            qf[token] += 1

        processed_query = {
            'query': query_terms,
            'qf': qf
        }

        return processed_query

    def get_doc_query(self, item):
        return item.childNodes[2].data.strip()

    def get_doc_id(self, item):
        return item.childNodes[1].childNodes[0].data.strip()

    def read_queries_file(self, query_file_name):
        queries = []
        query_xml = minidom.parse(query_file_name)
        itemlist = query_xml.getElementsByTagName('DOC')
        for item in itemlist:
            doc_id = self.get_doc_id(item)
            doc_query = self.get_doc_query(item)
            queries.append({
                'id': doc_id,
                'query': doc_query
            })
        
        return queries

    def search_entries(self, query_file, query_file_xml):
        if (query_file_xml):
            queries = self.read_queries_file(query_file)
            for query in queries:
                query_id = query['id']
                query_terms = query['query']
                self.search(query_terms, query_id, 'query_' + str(query_id) + '.results')
        else:
            with open(query_file, 'r') as f:
                for i, query in enumerate(f):
                    self.search(query, i + 1)

    def search(self, query_terms, index, save_as = None):
        logging.info('Searching : [{}] - {}'.format(index, query_terms))
        processed_query = self.parse_query(query_terms)
        logging.info('\tprocessed_query: {}'.format(processed_query))

        sorted_results = self.run_search(processed_query)

        if self._use_prf:
            # Use pseudo-relevance feedback to enhance search results
            for i in range(self._prf_num_iterations):
                logging.info('\texpanding query for PRF')
                expanded_query = self.expand_query_for_prf(query_terms, sorted_results)
                processed_expanded_query = self.parse_query(expanded_query)
                logging.info('\texpanded query: {}'.format(expanded_query))
                logging.info('\texpanded processed_query: {}'.format(processed_expanded_query))
                sorted_results = self.run_search(processed_expanded_query)
        
        system_name = self.get_system_name()
        results_file = query_terms.strip().replace(' ', '_') + '_results_bm25.txt'        
        if save_as:
            results_file = save_as
        logging.info('\tSaving results to: {}'.format(results_file))

        with open(results_file, 'w') as f:
            for i, entry in enumerate(sorted_results[0:100]):    
                f.write('{} Q0 {} {} {} {}\n'.format(index, entry[0], i + 1, entry[1], system_name))

        #for i, entry in enumerate(sorted_results[0:100]):
        #    print('{} Q0 {} {} {} {}'.format(index, entry[0], i, entry[1], system_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a corpus using a saved inverted index.")
    parser.add_argument("saved_index_file_name", type=str, help="Path to the saved index file.")
    parser.add_argument("query_file", type=str, help="File containing queries to run")
    parser.add_argument("-x", "--xml", help="Specify if the query file is in XML format.", action="store_true")
    parser.add_argument("-p", "--prf", help="Use pseudo relevance feedback", action="store_true")
    parser.add_argument("-s", "--stop-list-file", help="Use stop list provided in the file", metavar='text', type=str, default='')
    args = parser.parse_args()

    saved_index_file_name = args.saved_index_file_name
    query_file = args.query_file
    query_file_xml = args.xml
    use_prf = args.prf
    stop_list_file = args.stop_list_file

    searcher = BM25(saved_index_file_name, use_prf, stop_list_file)
    searcher.search_entries(query_file, query_file_xml)
