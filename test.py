import asyncio
import info
from log import LOG
from database import mysql_to_es,es_database
import database
if __name__ == "__main__":

    async def main():
        es = es_database.esSearch(info.ES_INDEX)
        #await es.del_all()
        #await database.appen_index(title="中国万岁",url="asdf",people="12k",m_type=3,weight=3)
        #await mysql_to_es.mysql_to_es()
        #await asyncio.sleep(2)
        #rult = await es.query_all()
        print("id: ",await database.exits_index(id="asdf"))
        #print(rult)
        print("count: ",await es.count())
        #print(await es.get_es().info())
        #LOG.info("开始搜索")
        #rult = await es.query(body={
        #    "query": {"match": { "title": "中国" } },
        #    "highlight" : {
        #        "pre_tags" : ["<tag1>", "<tag2>"],
        #        "post_tags" : ["</tag1>", "</tag2>"],
        #        "fields" : {
        #            "content" : {}
        #            }
        #        }
        #    })
        rult = await database.query("大其力玩咖群")
        print(rult)
        #LOG.info("搜索完成")
        await es.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
