from elasticsearch import Elasticsearch
import os

es = None
if os.getenv('ELASTICSEARCH_HOST'):
    es = Elasticsearch([os.getenv('ELASTICSEARCH_HOST')], sniff_on_start=False, )
