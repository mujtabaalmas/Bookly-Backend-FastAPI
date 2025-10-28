import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY_TIME = 3600

token_block_list = redis.from_url(Config.REDIS_URL)
# Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
# )


async def add_jti_to_blocklist(jti: str) -> None:
    await token_block_list.set(name=jti, value="", ex=JTI_EXPIRY_TIME)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_block_list.get(jti)
    return jti is not None
