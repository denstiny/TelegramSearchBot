import asyncio
from database import mysql
from database import es_database
import info

async def mysql_to_es():
    es = es_database.esSearch(info.ES_INDEX)
    print("创建索引")
    await es.create_index(body={
        "settings": {
            "number_of_shards": 4,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "url": {"type": "keyword"},
                "title": {
                    "type":"text",
                    "index": True,
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_smart"
                },
                "widget": {"type": "keyword"},
                "people": {"type": "keyword"},
                "m_type": {"type": "keyword"}
                }
            }
        }
    )
    #await es_database.es.indices.create(index="telegram",mappings=request_body)

    print("添加数据")
    linkage_all = await mysql.query_table_linkage_all()
    async def build_bodys(linkage_all):
        for linkage in linkage_all:
            yield {
                    "_index": "telegram",
                    "_source": {
                        "url": linkage.url,
                        "title": linkage.title,
                        "widget": linkage.weight,
                        "people": linkage.people,
                        "m_type": linkage.m_type
                        },
                    "_id": linkage.url
                    }
    #await es.del_all()
    #await es.index(id=linkage.url,body=body)
    #await es.buik(build_bodys(linkage_all))
    await es.stream_buik(build_bodys(linkage_all))
    #await helpers.async_bulk(es.get_es(),build_bodys(linkage_all))
    #print(await es.get_es().cat.count(index="telegram",params={"format": "json"}))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mysql_to_es())
