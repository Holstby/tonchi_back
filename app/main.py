import datetime

from fastapi import FastAPI
from pydantic import BaseModel
import redis


REDIS_URL = 'redis://redis:6379/0'

class TgAccount(BaseModel):
    uid: int
    is_premium: bool
    default_lang: str


class Item(BaseModel):
    uid: int


class CoverItem(Item):
    type: str = 'default'
    bg_color: str


class User(BaseModel):
    onboarding_is_done: bool
    balance: int
    items: list[Item]


class AllData(BaseModel):
    first_entry_dt: datetime.datetime
    last_entry_dt: datetime.datetime
    tg_account: TgAccount
    user: User


app = FastAPI()

example_data = AllData(
    first_entry_dt=datetime.datetime(2020, 1, 1, 16, 00),
    last_entry_dt=datetime.datetime.now(datetime.timezone.utc),
    tg_account=TgAccount(
        uid=1,
        is_premium=False,
        default_lang='en',
    ),
    user=User(
        onboarding_is_done=True,
        balance=100,
        items=[CoverItem(uid=23123, bg_color='#FFFFFF')],
    )
)


@app.get("/player/{player_id}/all_data", response_model=AllData | None)
async def get_data(player_id: int):
    redis_clnt = redis.Redis.from_url(REDIS_URL)

    data = redis_clnt.get(name=str(player_id))
    if data is None:
        return
    model = AllData.model_validate_json(data)
    return model


@app.post("/player/{player_id}/all_data")
async def post_data(player_id: int, data: AllData):
    print(f"Data received. player_id : {player_id}; data: {data.model_dump_json()}")
    redis_clnt = redis.Redis.from_url(REDIS_URL)
    redis_clnt.set(name=str(player_id), value=data.model_dump_json())
