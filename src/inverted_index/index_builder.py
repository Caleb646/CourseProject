# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:43:18 2022

@author: Robin
"""

import json
import os
import metapy

# from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd
# import re
# from nltk import word_tokenize          
# from nltk.stem import WordNetLemmatizer

class CorpusProcessor:
    def __init__(self):
        self.absolute_path = os.path.dirname(__file__)
        self.relative_path = "../scraper/data/campuswire/"
        self.full_path = os.path.join(self.absolute_path, self.relative_path)
        self.json_files = []
        self.posts = []
        self.temp_corpus = {}

    def read_json(self):
        for folder in os.listdir(self.full_path):
            for file in os.listdir(os.path.join(self.full_path, folder)):
                if file.endswith(".json"):
                    self.json_files.append(folder + '/' + file)
        
        for file in self.json_files:
            datafile = open(self.full_path + file)
        data = json.load(datafile)
        self.posts = list(data.values())[0]
    
    def construct_corpus(self):
        for post_id, post_content in self.posts.items():
            current_post = post_content
            post_title = current_post['post']['title']
            post_body = current_post['post']['body']
            replies = []
            for messages in current_post['messages']:
                replies.append(messages['body'])
            self.temp_corpus[post_id] = ((post_title + ' ' + post_body + ' '.join(replies)).replace("\n", " "))
            
    def return_corpus(self):
        return self.temp_corpus
    
    def write_corpus(self):
        newpath = self.absolute_path + '/campuswire/'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        with open(newpath + 'campuswire.dat', 'w', encoding="utf-8") as file:
            for value in self.temp_corpus.values():
                file.write('{}\n'.format(value))
    
    def write_docid(self):
        newpath = self.absolute_path + '/campuswire/'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        with open(newpath + 'campuswire_docid.dat', 'w', encoding="utf-8") as file:
            for value in self.temp_corpus.keys():
                file.write('{}\n'.format(value))
                
    def make_index(self):
        metapy.index.make_inverted_index('config.toml')

    
# Code to build a document term frequency matrix, but this seems unnecessary if
# we're making use of metapy

# temp_corpus = pd.DataFrame({'post_id': temp_corpus.keys(), 'text': temp_corpus.values()})
# class Tokenizer(object):
#     def __init__(self):
#         self.stemmer = WordNetLemmatizer()
#     def __call__(self, doc):
#         regex_num_punctuation = '(\d+)|([^\w\s])'
#         regex_small_words = r'(\b\w{1,2}\b)'
#         return [self.stemmer.lemmatize(t) for t in word_tokenize(doc) 
#                 if not re.search(regex_num_punctuation, t) and not re.search(regex_small_words, t)]
# cv = CountVectorizer(tokenizer=Tokenizer()) 
# cv_matrix = cv.fit_transform(temp_corpus['text']) 
# df_df = pd.DataFrame(cv_matrix.toarray(), index=temp_corpus['post_id'].values, columns=cv.get_feature_names_out())
# test = cv.get_feature_names_out()
# df_df.columns.values


# a bit of test code

cp = CorpusProcessor()
cp.read_json()
cp.construct_corpus()
test_corpus = cp.return_corpus()
cp.write_corpus()
cp.write_docid()
cp.make_index()


idx = metapy.index.make_inverted_index('config.toml')
ranker = metapy.index.OkapiBM25()
query = metapy.index.Document()


# Search example to test

query.content('Exam 1 content')

top_docs = ranker.score(idx, query, num_results=5)

for num, (d_id, _) in enumerate(top_docs):
    content = idx.metadata(d_id).get('content')
    print("{}. {}...\n".format(num + 1, content[0:250]))
    
    
    
    
    
    
    
    
    
    
    
    
    
    