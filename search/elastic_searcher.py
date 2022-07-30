from datetime import datetime

import elasticsearch_dsl
from elasticsearch_dsl import Document, Date, Nested, Boolean, Index
from elasticsearch_dsl import analyzer, Completion, Keyword, Text, Search
from elasticsearch import Elasticsearch

from search.config import USER, ELASTIC_PASSWORD, PATH_TO_CRT, ELASTIC_URL
from search.searcher import Searcher

from data_types.values import Value, Sentence
from data_types.post import Post

client = Elasticsearch(
    ELASTIC_URL,
    ca_certs=PATH_TO_CRT,
    basic_auth=(USER, ELASTIC_PASSWORD)
)


class ElasticValueCreator:
    name = "ElasticValueCreator"

    @classmethod
    def should_create(cls, elastic_obj) -> bool:
        pass

    @classmethod
    def create(cls, elastic_obj):
        pass

    @classmethod
    def dict_from_hit_meta(cls, value) -> dict:
        dict_ = {}
        for key in dir(value):
            dict_[key] = value[key]
        return dict_

    @classmethod
    def dict_from_elastic_hit(cls, hit: elasticsearch_dsl.response.hit.Hit) -> dict:
        assert (isinstance(hit, elasticsearch_dsl.response.hit.Hit))
        dict_ = {}
        for key in dir(hit):
            if key == 'meta':
                dict_[key] = cls.dict_from_hit_meta(hit.meta)
                continue
            dict_[key] = hit[key]
        return dict_


class ElasticSentenceCreator(ElasticValueCreator):
    name = "ElasticSentenceCreator"

    @classmethod
    def should_create(cls, elastic_obj) -> bool:
        return elastic_obj['type'] == 'Sentence'

    @classmethod
    def create(cls, elastic_obj) -> Sentence:
        elastic_obj_dict = cls.dict_from_elastic_hit(elastic_obj)
        kwargs = dict(filter(lambda x: x[1] != "meta", elastic_obj_dict.items()))
        kwargs['id_'] = elastic_obj_dict["meta"]["id"]
        kwargs['type_'] = kwargs.pop('type')
        return Sentence(**kwargs)


class Comment(Document):
    author = Text(fields={'raw': Keyword()})
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
    elastic_value_creators = [ElasticSentenceCreator]

    @classmethod
    def add_record(cls, post: Post = None, using=client, index_topic: str = None, index_comments: str = None):
        topic = Topic(title=post.get_key())
        meta_info = topic.save(using=client, return_doc_meta=True, index=index_topic)
        id_ = meta_info['_id']
        for value in post.get_values():
            comment = Comment(author=None, topic_id=id_, type=value.get_type(), **value.get_info())
            comment.save(using=using, return_doc_meta=True, index=index_comments)

    @classmethod
    def append_comment_by_id(cls, id_: str = None, value: Value = None, using=client, index_comments: str = None):
        comment = Comment(author=None, topic_id=id_, **value.get_info())
        comment.save(using=using, return_doc_meta=True, index=index_comments)

    @classmethod
    def get_relevant_topics(cls,
                            message: str,
                            using=client,
                            index_topics: str = "topics") -> list[tuple[str, str]]:
        response = Search(index=index_topics, using=using).query("match", title=message).execute()
        topics = []
        for hit in response:
            topics.append((hit['title'], hit.meta['id']))
        return topics

    @classmethod
    def get_comments_by_topic_id(cls,
                                 id_: str = None,
                                 using=client,
                                 index_comments: str = "comments") -> list[Value]:
        response = Search(index=index_comments, using=using).query("match", topic_id=id_).execute()
        comments = []
        for hit in response:
            for creator in cls.elastic_value_creators:
                if creator.should_create(hit):
                    comments.append(creator.create(hit))

        return comments
