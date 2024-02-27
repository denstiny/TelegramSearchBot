import redis.asyncio as reddis
import asyncio

client = reddis.Redis(host="localhost",port=6379,db=0)
async def test():
    print(f"Ping successful: {await client.ping()}")
    await client.aclose()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
