
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean
from elasticsearch_dsl import analyzer, Completion, Keyword, Text
from elasticsearch import Elasticsearch
from searcher.config import USER, ELASTIC_PASSWORD, PATH_TO_CRT, ELASTIC_URL


client = Elasticsearch(
    ELASTIC_URL,
    ca_certs=PATH_TO_CRT,
    basic_auth=(USER, ELASTIC_PASSWORD)
)


first_strip = analyzer('first_analizer',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"]
)


class Comment(Document):
    author = Text(fields={'raw': Keyword()})
    content = Text()
    created_at = Date()
    
    class Index:
        name = 'comments'

    
    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)

    
class Topic(Document):
    title = Text()
    created_at = Date()
    category = Text(
        analyzer=first_strip,
        fields={'raw': Keyword()}
    )

    class Index:
        name = 'topics'

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)