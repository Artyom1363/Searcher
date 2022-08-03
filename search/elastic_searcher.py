from datetime import datetime

import elasticsearch_dsl
from elasticsearch_dsl import Document, Date, Nested, Boolean, Index
from elasticsearch_dsl import analyzer, Completion, Keyword, Text, Search
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

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

    @classmethod
    def get_type(cls, elastic_obj) -> str:
        if isinstance(elastic_obj, dict):
            return elastic_obj['_source']['type']
        elif isinstance(elastic_obj, elasticsearch_dsl.response.hit.Hit):
            return elastic_obj['type']


class ElasticSentenceCreator(ElasticValueCreator):
    name = "ElasticSentenceCreator"

    @classmethod
    def should_create(cls, elastic_obj) -> bool:
        return cls.get_type(elastic_obj) == "Sentence"

    @classmethod
    def create(cls, elastic_obj) -> Sentence:
        if isinstance(elastic_obj, dict):
            return cls.create_from_dict(elastic_obj)
        elif isinstance(elastic_obj, elasticsearch_dsl.response.hit.Hit):
            return cls.create_from_elastic_hit(elastic_obj)

    @classmethod
    def create_from_elastic_hit(cls, elastic_hit) -> Sentence:
        elastic_obj_dict = cls.dict_from_elastic_hit(elastic_hit)
        kwargs = dict(filter(lambda x: x[1] != "meta", elastic_obj_dict.items()))
        kwargs['_id'] = elastic_obj_dict["meta"]["id"]
        kwargs['_type'] = kwargs.pop('type')
        return Sentence(**kwargs)

    @classmethod
    def create_from_dict(cls, elastic_dict) -> Sentence:
        kwargs = elastic_dict['_source']
        kwargs['_id'] = elastic_dict['_id']
        kwargs['_type'] = kwargs.pop('type')
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
                            index_topics: str = "topics",
                            limit: int = 3) -> list[tuple[str, str]]:
        response = Search(index=index_topics, using=using).query("match", title=message).execute()
        topics = []
        hits_counter = 0
        for hit in response:
            if hits_counter >= limit:
                break
            hits_counter += 1
            topics.append((hit['title'], hit.meta['id']))
        return topics

    @classmethod
    def get_comments_by_topic_id(cls,
                                 id_: str = None,
                                 using=client,
                                 index_comments: str = "comments",
                                 limit: int = 3) -> list[Value]:
        response = Search(index=index_comments, using=using).query("match", topic_id=id_).execute()
        comments = []
        hits_counter = 0
        for hit in response:
            if hits_counter >= limit:
                break
            hits_counter += 1
            for creator in cls.elastic_value_creators:
                if creator.should_create(hit):
                    comments.append(creator.create(hit))

        return comments

    @classmethod
    def get_topic_by_id(cls,
                        id_: str,
                        using=client,
                        index_topics: str = "topics") -> str:
        try:
            response = using.get(index=index_topics, id=id_)
        except NotFoundError:
            return None
        except ValueError:
            return None
        except Exception:
            return None
        else:
            return response['_source']['title']

    @classmethod
    def get_comment_by_id(cls,
                          id_: str,
                          using=client,
                          index_comments: str = "comments") -> Value:
        try:
            response = using.get(index=index_comments, id=id_)
        except NotFoundError:
            print("NotFoundError")
            return None
        except ValueError:
            print("ValueError")
            return None
        except Exception:
            print("Exception")
            return None
        else:
            hit = response
            for creator in cls.elastic_value_creators:
                if creator.should_create(hit):
                    return creator.create(hit)
