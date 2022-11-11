# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:43:18 2022

@author: Robin
"""

import json
import os
import metapy
from fnmatch import fnmatch


class CorpusProcessor:
    def __init__(self):
        self.absolute_path = os.path.dirname(__file__)        
        self.absolute_path = os.path.dirname(__file__)
        self.relative_path = "../scraper/data/"
        self.full_path = os.path.join(self.absolute_path, self.relative_path)
        self.json_files = []
        self.posts = []
        self.temp_corpus = {}
        self.coursera_data = []
        self.campuswire_data = []

    def read_json(self):
        for path, subdirs, files in os.walk(self.full_path):
            for name in files:
                if fnmatch(name, '*.json'):
                    self.json_files.append(os.path.join(path, name))

        for file in self.json_files:
            datafile = open(file)
            data = json.load(datafile)
            self.posts.append(list(data.values()))
            
        self.coursera_data = self.posts[1]
        self.campuswire_data = self.posts[0][0]
    
    def construct_corpus(self):
        for post_id, post_content in self.campuswire_data.items():
            current_post = post_content
            post_title = current_post['post']['title']
            post_body = current_post['post']['body']
            replies = []
            for messages in current_post['messages']:
                replies.append(messages['body'])
            self.temp_corpus[post_id] = ((post_title + ' ' + post_body + ' '.join(replies)).replace("\n", " "))

        for post_id, post in enumerate(self.coursera_data):
            index_id = 'Coursera' + str(post_id)
            current_post = list(post.values())[0]
            self.temp_corpus[index_id] = ((current_post).replace("\n", " "))

    def return_corpus(self):
        return self.temp_corpus
    
    def write_corpus(self):
        newpath = self.absolute_path + '/corpus/'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        with open(newpath + 'corpus.dat', 'w', encoding="utf-8") as file:
            for value in self.temp_corpus.values():
                file.write('{}\n'.format(value))
    
    def write_docid(self):
        newpath = self.absolute_path + '/corpus/'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        with open(newpath + 'corpus_docid.dat', 'w', encoding="utf-8") as file:
            for value in self.temp_corpus.keys():
                file.write('{}\n'.format(value))
                
    def make_index(self):
        metapy.index.make_inverted_index('config.toml')


# a bit of test code

# cp = CorpusProcessor()
# cp.read_json()
# cp.construct_corpus()
# test_corpus = cp.return_corpus()
# cp.write_corpus()
# cp.write_docid()
# cp.make_index()


# idx = metapy.index.make_inverted_index('config.toml')
# ranker = metapy.index.OkapiBM25()
# query = metapy.index.Document()


# Search example to test

# query.content('Exam 1 content')

# top_docs = ranker.score(idx, query, num_results=5)

# for num, (d_id, _) in enumerate(top_docs):
#     content = idx.metadata(d_id).get('content')
#     print("{}. {}...\n".format(num + 1, content[0:250]))
    
    
    
    
    
    
    
    
    
    
    
    
    
    