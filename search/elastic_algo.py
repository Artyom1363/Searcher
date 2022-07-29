
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, Index
from elasticsearch_dsl import analyzer, Completion, Keyword, Text
from elasticsearch import Elasticsearch
from search.config import USER, ELASTIC_PASSWORD, PATH_TO_CRT, ELASTIC_URL
from search.searcher import Searcher
from data_types.values import Value
from data_types.post import Post


client = Elasticsearch(
    ELASTIC_URL,
    ca_certs=PATH_TO_CRT,
    basic_auth=(USER, ELASTIC_PASSWORD)
)


class Comment(Document):
    author = Text(fields={'raw': Keyword()})
    content = Text()
    created_at = Date()
    topic_id = Text(fields={'raw': Keyword()})
    type = Text(fields={'raw': Keyword()})
    sentence = Text()

    class Index:
        name = "comments"

    def save(self, **kwargs):
        self.created_at = datetime.now()
        kwargs = dict(filter(lambda x: x[1] is not None, kwargs.items()))
        return super().save(**kwargs)

    
class Topic(Document):
    title = Text()
    created_at = Date()

    class Index:
        name = "topics"

    def save(self, **kwargs):
        self.created_at = datetime.now()
        kwargs = dict(filter(lambda x: x[1] is not None, kwargs.items()))
        return super().save(**kwargs)


class ElasticSearcher(Searcher):

    @classmethod
    def add_record(cls, post: Post = None, using=client, index_topic: str = None, index_comments: str = None):
        topic = Topic(title=post.get_key())
        meta_info = topic.save(using=client, return_doc_meta=True, index=index_topic)
        id_ = meta_info['_id']
        for value in post.get_values():
            comment = Comment(author=None, topic_id=id_, **value.get_info())
            comment.save(using=using, return_doc_meta=True, index=index_comments)

    @classmethod
    def append_comment_by_id(cls, id_: str = None, value: Value = None):
        pass
        # assert(id_ is not None)
