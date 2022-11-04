from src.data_types.fvrt import  Favorite
from src.data_types.likes import Like
from src.data_types.values import Value


class Comment:
    def __init__(self, value: Value, like: Like, favorite: Favorite, topic_id: str = None):
        self.value = value
        self.like = like
        self.favorite = favorite
        self.topic_id = topic_id

    def get_value(self):
        return self.value

    def get_like(self):
        return self.like

    def get_favorite(self):
        return self.favorite

    def get_id(self):
        return self.value.get_id()

    def __lt__(self, other):
        return self.like.get_total_likes() < other.like.get_total_likes()
