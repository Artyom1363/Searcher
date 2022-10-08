from asyncpg import Connection


class FavoriteState:
    def __init__(self, user_id: int,
                 comment_id: str, is_on: bool,
                 pool: Connection):
        self.user_id = user_id
        self.comment_id = comment_id
        self.is_on = is_on
        self.pool = pool

    def is_on(self):
        return self.is_on

    def is_off(self):
        return not self.is_on

    async def switch(self):
        pass


class Favorite:
    @classmethod
    async def get(cls, pool: Connection, user_id: int, comment_id: str):
        query = f"SELECT" \
                f"( SELECT COUNT(*) FROM favorites WHERE user_id = {user_id} " \
                f"and comment_id = '{comment_id}' ) AS is_on;"

        result = await pool.fetch(query)
        if result[0][0] == 0:
            favorite_state = FavoriteOff(user_id, comment_id, False, pool)
        elif result[0][0] == 1:
            favorite_state = FavoriteOn(user_id, comment_id, True, pool)
        else:
            raise Exception(f"Unresolved quantity in favorites where {user_id=} and {comment_id=}")
        return Favorite(favorite_state)

    def __init__(self, favorite: FavoriteState):
        self.favorite = favorite

    def set_current(self, favorite: FavoriteState):
        self.favorite = favorite

    async def switch(self):
        self.favorite = await self.favorite.switch()

    def is_on(self):
        return self.favorite.is_on

    def is_off(self):
        return not self.favorite.is_off


class FavoriteOn(FavoriteState):
    async def switch(self):
        query = f"DELETE FROM favorites WHERE user_id = {self.user_id} " \
                f"AND comment_id = '{self.comment_id}'"

        await self.pool.fetch(query)
        self.is_on = False
        return FavoriteOff(self.user_id, self.comment_id, self.is_on, self.pool)


class FavoriteOff(FavoriteState):
    async def switch(self):
        query = f"INSERT INTO favorites (user_id, comment_id) values " \
                f"({self.user_id}, '{self.comment_id}')"

        await self.pool.fetch(query)
        self.is_on = True
        return FavoriteOn(self.user_id, self.comment_id, self.is_on, self.pool)
