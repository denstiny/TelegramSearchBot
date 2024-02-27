# -*- coding: UTF-8 -*-
"""

 @author      : denstiny (2254228017@qq.com)
 @file        : test.es
 @created     : 星期五 2月 23, 2024 17:28:55 CST
 @github      : https://github.com/denstiny
 @blog        : https://denstiny.github.io

"""
import time
from datetime import datetime
from elasticsearch import Elasticsearch
import json

es = Elasticsearch("http://localhost:9200")

doc = {
    'title': 'The quick brown fox',
    'content': 'The quick brown fox jumps over the lazy dog'
}
doc1 = {
    'title': 'The quick brown fox1',
    'content': 'The quick brown fox jumps over the lazy dog1'
}
doc2 = {
    'title': 'The quick brown fox2',
    'content': 'The quick brown fox jumps over the lazy dog2',
}

# index the document
es.index(index='my_index', id='121', body=doc,refresh=True)
es.index(index='my_index', id='212', body=doc1,refresh=True)
es.index(index='my_index', id='1212', body=doc2,refresh=True)

#time.sleep(2)

query = {
    'query': {
        "match_all": {}
    }
}
print(es.search(index="my_index",body=query))

#print(es.indices.analyze(body={"analyzer": "ik_max_word","text": ["黑马程序员"]}))

es.delete_by_query(index="my_index",body={"query": {"match_all": {}}},refresh=True)

#data = {
#    'doc': {
#        'content': 'A quick brown fox'
#    }
#}
## update the document
#es.update(index='my_index', id=1, body=data)
