from asyncpg import Connection


class LikeState:
    def __init__(self, user_id: int,
                 comment_id: str,
                 topic_id: str,
                 total_likes: int,
                 pool: Connection):
        self.user_id = user_id
        self.comment_id = comment_id
        self.topic_id = topic_id
        self.total_likes = total_likes
        self.pool = pool

    def is_on(self) -> bool:
        pass

    async def switch(self):
        pass

    def __eq__(self, other):
        return all([self.is_on() == other.is_on(),
                    self.user_id == other.user_id,
                    self.comment_id == other.comment_id,
                    self.total_likes == other.total_likes])


class Like:
    @classmethod
    async def get(cls, user_id: int, comment_id: str, topic_id: str, pool: Connection):
        query = f"SELECT " \
                f"(SELECT COUNT(*) FROM likes WHERE comment_id = " \
                f"'{comment_id}') AS total," \
                f"(SELECT COUNT(*) FROM likes WHERE user_id = {user_id} " \
                f"AND comment_id = '{comment_id}' ) AS personal;"

        result = await pool.fetch(query)
        if result[0][1] == 0:
            like_state = LikeOff(user_id, comment_id, topic_id, result[0][0], pool)
        elif result[0][1] == 1:
            like_state = LikeOn(user_id, comment_id, topic_id, result[0][0], pool)
        else:
            raise Exception("cant detect type of like")
        return Like(like_state)

    def __init__(self, like: LikeState):
        self.like = like

    def set_current(self, like: LikeState) -> None:
        self.like = like

    async def switch(self) -> None:
        self.like = await self.like.switch()

    def is_on(self) -> bool:
        return self.like.is_on()

    def get_total_likes(self) -> int:
        return self.like.total_likes

    def __eq__(self, other):
        return self.like == other.like


class LikeOn(LikeState):

    def is_on(self) -> bool:
        return True

    async def switch(self) -> LikeState:
        query = f"DELETE FROM likes WHERE user_id = {self.user_id} " \
                f"AND comment_id = '{self.comment_id}';"

        await self.pool.fetch(query)
        self.total_likes -= 1
        return LikeOff(self.user_id, self.comment_id, self.topic_id,
                       self.total_likes, self.pool)


class LikeOff(LikeState):

    def is_on(self) -> bool:
        return False

    async def switch(self) -> LikeState:
        query = f"INSERT INTO likes (user_id, comment_id, topic_id) VALUES " \
                f"({self.user_id}, '{self.comment_id}', '{self.topic_id}');"

        await self.pool.fetch(query)
        self.total_likes += 1
        return LikeOn(self.user_id, self.comment_id, self.topic_id,
                      self.total_likes, self.pool)
