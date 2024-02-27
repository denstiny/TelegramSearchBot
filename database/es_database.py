import asyncio
from elasticsearch import AsyncElasticsearch,helpers


class esSearch():
    def __init__(self,index:str):
        self.es = AsyncElasticsearch("http://localhost:9200")
        self._index = index


    async def count(self):
        return (await self.es.cat.count(index="telegram",params={"format": "json"}))[0]["count"]
    async def create_index(self,body):
        if not await self.es.indices.exists(index=self._index):
            await self.es.indices.create(index=self._index,body=body)
        else:
            await self.es.indices.delete(index=self._index)
            await self.es.indices.create(index=self._index,body=body)

    async def index(self,id,body):
        await self.es.index(index=self._index,id = id,body = body)

    async def exits_index(self,id):
        return await self.es.exists(index=self._index,id = id)

    async def del_all(self):
        await self.es.delete_by_query(index=self._index,body={"query": {"match_all": {}}},refresh=True)

    def get_es(self):
        return self.es

    async def buik(self,bodys):
        await helpers.async_bulk(self.es,bodys)

    async def stream_buik(self,bodys):
        async for ok,result in helpers.async_streaming_bulk(self.es,bodys):
            action, result = result.popitem()
            if not ok:
                print("failed to %s document %s" % ())

    async def query(self,body):
        search_body = {
                "query": body,
                "size": 9999
                }
        resutl = await self.es.search(index=self._index,body=body)
        #print(resutl)
        return resutl

    async def ik_word(self,keyboard):
        return await self.es.indices.analyze(body={"analyzer": "ik_max_word","text": [keyboard]})

    async def query_all(self):
        search_body = {
                "query": {
                    "match_all": {}
                    },
                "size": 20
                }

        reult =  await self.es.search(index=self._index,body=search_body)
        return reult

    async def close(self):
        await self.es.close()

    async def del_data(self,id):
        await self.es.delete(index=self._index,id=id)

async def check_main():
    es = esSearch("telegram")
    await mysql_to_es.mysql_to_es()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_main())
