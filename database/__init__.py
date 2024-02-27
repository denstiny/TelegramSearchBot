import asyncio
from database import es_database
from asyncache import cached
from database import mysql
from cachetools import TTLCache
from log import LOG
import info

ES = es_database.esSearch(index=info.ES_INDEX)

class linkage():
    title = ""
    url = ""
    people = ""
    weight = 0
    m_type = 3
    score = 0.0

    def __init__(self,title,url,people,weight,m_type,score) -> None:
        self.title = title
        self.url = url
        self.people = people
        self.weight = weight
        self.m_type = m_type
        self.score = score

    def __str__(self) -> str:
        return f"{self.title} {self.url} {self.weight} {self.people} {self.m_type}{self.score}"

async def exits_index(id):
    return await ES.exits_index(id)

async def appen_index(title,url,people,weight=0,m_type=3):
    if await ES.exits_index(url):
        return None
    await ES.index(id=url,body={
        "url": url,
        "title": title,
        "widget": weight,
        "people": people,
        "m_type": m_type
    })
    await mysql.insert_table_linkage(title=title,url=url,weight=weight,m_type=m_type,people=people,channel=m_type == 3)
    LOG.info(f"添加 {title}")
    return True


async def del_all():
    await ES.del_all()

async def create_index():
    await ES.create_index(body={
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
                "search_analyzer": "ik_max_word"
            },
            "widget": {"type": "keyword"},
            "people": {"type": "keyword"},
            "m_type": {"type": "keyword"}
            }
        }
    })

async def query(keyboard):
    if len(keyboard) == 0:
        return

    #print("分词测试",await ES.ik_word(keyboard))
    result = await ES.query(body={
        #"query": {"match": { "title": {"query": keyboard, "operator": "and"} } },
        "query": {
            "bool": {
                "should" : [
                    {
                        "match": {
                            "title": {
                                "query" : keyboard , "operator" : "and", "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "term": {
                            "title": keyboard
                        }
                    }
                ]
            }
        },
        "size": 9999
    })
    hits = result.get('hits',{}).get('hits',[])
    return hits

async def del_data(id):
    if len(id) == 0:
        return

    await ES.del_data(id)
