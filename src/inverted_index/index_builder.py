# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:43:18 2022

@author: Robin
"""

from multiprocessing import Process, Pipe

import json
import os
import metapy
from fnmatch import fnmatch


class CorpusProcessor:
    def __init__(self):
        self.absolute_path = os.path.dirname(__file__)
        self.relative_path = "data/"
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
            self.posts.append(list(data.items()))
            
        self.coursera_data = self.posts[1]
        self.campuswire_data = self.posts[0][0][1]
    
    def construct_corpus(self):
        for post_id, post_content in self.campuswire_data.items():
            current_post = post_content
            post_title = current_post['post']['title']
            post_body = current_post['post']['body']
            post_url = 'https://campuswire.com/c/G984118D3/feed/' + str(current_post['post']['number'])
            replies = []
            for messages in current_post['messages']:
                replies.append(messages['body'])
            self.temp_corpus[post_id] = ((post_url + ' ' + post_title + ' ' + post_body + ' '.join(replies)).replace("\n", " "))

        for post_id, post in enumerate(self.coursera_data):
            index_id = 'Coursera' + str(post_id)
            current_post = post[0] + str(post[1].values())
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
        path = os.path.join(self.absolute_path, "config.toml")
        #metapy.index.make_inverted_index('config.toml')
        return metapy.index.make_inverted_index(path)

def handle_query(string):
    cp = CorpusProcessor()
    # cp.read_json()
    # cp.construct_corpus()
    # cp.write_corpus()
    # cp.write_docid()
    
    config_dir = str(os.path.dirname(__file__))
    current = os.curdir
    # NOTE (Caleb): I had issues being in the wrong directory when this function would run.
    # So I just change the working directory to the index_builder.py directory before setting
    # up Metapy. I change back to the original directory after.
    os.chdir(config_dir)
    idx = cp.make_index()

    ranker = metapy.index.OkapiBM25()
    query = metapy.index.Document()

    # Search example to test
    query.content(string)
    top_docs = ranker.score(idx, query, num_results=5)

    print("Returning the top ranked documents.")
    # Change back to original directory
    os.chdir(current)

    # Returns top num_results
    res_data = []
    for num, (d_id, _) in enumerate(top_docs):
        content = idx.metadata(d_id).get('content')
        res_data.append("[{}] {}...\n".format(num + 1, content[0:250]))
    return res_data

# AWS Lambda functions pass an event variable to the function handler
# This is the variable's format.
mock_aws_lambda_event = [
    {'version': '2.0', 
    'routeKey': '$default', 
    'rawPath': '/', 
    'rawQueryString': '', 
    'headers': {
        'content-length': '18', 
        'x-amzn-tls-version': 'TLSv1.2', 
        'x-forwarded-proto': 'https', 
        'postman-token': '', 
        'x-forwarded-port': '443', 
        'x-forwarded-for': '', 
        'accept': '*/*', 
        'x-amzn-tls-cipher-suite': '', 
        'x-amzn-trace-id': '', 
        'host': '', 
        'content-type': 'application/json', 
        'cache-control': 'no-cache', 
        'accept-encoding': 'gzip, deflate, br', 
        'user-agent': ''
        }, 
    'requestContext': {
        'accountId': 'anonymous', 
        'apiId': '', 
        'domainName': '', 
        'domainPrefix': '', 
        'http': {
            'method': 'POST', 
            'path': '/', 
            'protocol': 'HTTP/1.1', 
            'sourceIp': '184.60.153.38', 
            'userAgent': 'PostmanRuntime/7.29.2'
            }, 
        'requestId': 'eea7ddf5-d85c-42e9-92c2-a03fd2f20db3', 
        'routeKey': '$default', 
        'stage': '$default', 
        'time': '16/Nov/2022:15:17:06 +0000', 
        'timeEpoch': 1668611826219
        }, 
        'body': '{"query" : "test"}', 
        'isBase64Encoded': False
    }
]

def lambda_handler(event, context):
    if isinstance(event, list):
        event = event[0]
    assert isinstance(event, dict), "Event [{}] is not of type dict but [{}]".format(str(event), type(event))
    query_params = event.get("queryStringParameters", None)
    body = event.get("body", None)
    query = event.get("query", None)

    # try to use query params to complete the request
    if query_params and "query" in query_params:
        return json.dumps(handle_query(query_params["query"]))

    # try to use the body to complete the request
    if body and "query" in body:
        body = json.loads(body)
        if isinstance(body, list):
            body = body[0]
        return json.dumps(handle_query(body["query"]))

    # 
    if query:
        return json.dumps(handle_query(query))

    print("Could not successfully query with event of: [{}]".format(str(event)))
    raise KeyError