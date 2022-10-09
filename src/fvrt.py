from asyncpg import Connection


class FavoriteState:
    def __init__(self, user_id: int,
                 comment_id: str,
                 pool: Connection):
        self.user_id = user_id
        self.comment_id = comment_id
        self.pool = pool

    def is_on(self) -> bool:
        pass

    async def switch(self):
        pass

    def __eq__(self, other) -> bool:
        return self.is_on() == other.is_on() \
               and self.user_id == other.user_id \
               and self.comment_id == other.comment_id


class Favorite:
    @classmethod
    async def get(cls, user_id: int, comment_id: str, pool: Connection):
        query = f"SELECT COUNT(*) as is_on FROM favorites " \
                f"WHERE user_id = {user_id} " \
                f"AND comment_id = '{comment_id}';"

        result = await pool.fetch(query)
        if result[0][0] == 0:
            favorite_state = FavoriteOff(user_id, comment_id, pool)
        elif result[0][0] == 1:
            favorite_state = FavoriteOn(user_id, comment_id, pool)
        else:
            raise Exception(f"Unresolved quantity in favorites "
                            f"where {user_id=} and {comment_id=}")
        return Favorite(favorite_state)

    def __init__(self, favorite: FavoriteState):
        self.favorite = favorite

    def set_current(self, favorite: FavoriteState):
        self.favorite = favorite

    async def switch(self):
        self.favorite = await self.favorite.switch()

    def is_on(self):
        return self.favorite.is_on()

    def __eq__(self, other):
        return self.favorite == other.favorite


class FavoriteOn(FavoriteState):

    def is_on(self):
        return True

    async def switch(self):
        query = f"DELETE FROM favorites WHERE user_id = {self.user_id} " \
                f"AND comment_id = '{self.comment_id}';"

        await self.pool.fetch(query)
        return FavoriteOff(self.user_id, self.comment_id, self.pool)


class FavoriteOff(FavoriteState):

    def is_on(self):
        return False

    async def switch(self):
        query = f"INSERT INTO favorites (user_id, comment_id) VALUES " \
                f"({self.user_id}, '{self.comment_id}');"

        await self.pool.fetch(query)
        return FavoriteOn(self.user_id, self.comment_id, self.pool)
