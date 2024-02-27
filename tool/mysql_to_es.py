import asyncio
from database import mysql

async def mysql_to_es():
    linkage_all = await mysql.query_table_linkage_all()
    for linkage in linkage_all:
        print(f"url: {linkage.url} title: {linkage.title} widget: {linkage.weight} people: {linkage.people} m_type: {linkage.m_type}")


loop = asyncio.get_event_loop()
loop.run_until_complete(mysql_to_es())
