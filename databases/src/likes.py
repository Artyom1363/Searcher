from asyncpg import Connection


async def get_like(pool: Connection, user_id: int, comment_id: str):
    query = f"SELECT" \
            f"(SELECT COUNT(*) FROM likes WHERE comment_id = '{comment_id}') AS total," \
            f"( SELECT COUNT(*) FROM likes WHERE user_id = {user_id} " \
            f"and comment_id = '{comment_id}' ) AS personal;"

    result = await pool.fetch(query)
    if result[0][1] == 0:
        like_state = LikeOff(user_id, comment_id, result[0][0], False, pool)
    elif result[0][1] == 1:
        like_state = LikeOn(user_id, comment_id, result[0][0], True, pool)
    else:
        raise Exception("cant detect type of like")
    return Like(like_state)


class LikeState:
    def __init__(self, user_id: int,
                 comment_id: str, total_likes: int,
                 is_on: bool, pool: Connection):
        self.user_id = user_id
        self.comment_id = comment_id
        self.total_likes = total_likes
        self.is_on = is_on
        self.pool = pool

    def is_on(self):
        return self.is_on

    def is_off(self):
        return not self.is_on

    async def switch(self):
        pass


class Like:

    def __init__(self, like: LikeState):
        self.like = like

    def set_current(self, like: LikeState):
        self.like = like

    async def switch(self):
        self.like = await self.like.switch()

    def is_on(self):
        return self.like.is_on

    def is_off(self):
        return not self.like.is_off


class LikeOn(LikeState):
    async def switch(self):
        query = f"DELETE FROM likes WHERE user_id = {self.user_id} " \
                f"AND comment_id = '{self.comment_id}'"

        await self.pool.fetch(query)
        self.total_likes += 1
        self.is_on = False
        return LikeOff(self.user_id, self.comment_id, self.total_likes, self.is_on, self.pool)


class LikeOff(LikeState):
    async def switch(self):
        query = f"INSERT INTO likes (user_id, comment_id) values " \
                f"({self.user_id}, '{self.comment_id}')"

        await self.pool.fetch(query)
        self.total_likes -= 1
        self.is_on = True
        return LikeOn(self.user_id, self.comment_id, self.total_likes, self.is_on, self.pool)
