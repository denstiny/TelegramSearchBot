from typing import Sequence
import uuid
import time
from loguru import logger
import sqlalchemy
from log import LOG
from sqlalchemy import BOOLEAN, DATETIME, INTEGER, TEXT, VARCHAR, Column, and_, asc, update
from sqlalchemy.inspection import inspect
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.mapper import event
from utils.fitter import fuzz,fuzzsort


engine = create_async_engine("mysql+asyncmy://root:123456@localhost/Telegram",
                        max_overflow=0,
                        pool_size= 100,
                        pool_timeout= 30,
                        pool_recycle= -1)

DBSession = async_sessionmaker(bind=engine,class_=AsyncSession)
#Base = declarative_base()

class Base(AsyncAttrs,DeclarativeBase):
    pass

class linkage(Base):
    __tablename__ = "linkage"
    id = Column(INTEGER,primary_key=True)
    title = Column(TEXT)
    url = Column(VARCHAR(255),unique=True)
    channel = Column(BOOLEAN)
    people = Column(VARCHAR(10))
    weight = Column(INTEGER)
    m_type = Column(INTEGER)

class administrator(Base):
    __tablename__ = "administrator"
    id = Column(INTEGER,primary_key=True)
    user = Column(TEXT) # 管理员用户
    m_type = Column(INTEGER) # 类型


""" 创建所有表 """
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

""" 删除所有表 """
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


""" 检查数据库 """
async def self_inspection():
    """ 检查数据库是否连接成功 """
    try:
        async with engine.connect() as conn:
            LOG.info("连接 mysql 成功")
            """ 检查表是否已经创建 """

            LOG.info("检查表是否存在")
            await init_db()
            def get_table_names(conn):
                inspecter = inspect(conn)
                return inspecter.get_table_names()
                
            table_names = await conn.run_sync(get_table_names)
            assert table_names
            tabnames = [linkage.__tablename__,
                        administrator.__tablename__]
            for tabname in tabnames:
                if tabname in tabnames:
                    LOG.info(f"{tabname} 表已存在")
                else:
                    LOG.warning(f"{tabname} 数据库表不存在")
                    quit()

    except sqlalchemy.exc.OperationalError as e:
        LOG.error(f"连接 mysql 失败: 请启动数据库 :{e}")
        quit()

""" 添加管理员用户 """
async def insert_table_administrator(user,m_type):
    if await query_administrator(user) != []:
        LOG.error(f"{user} 重复用户")
        return

    async with DBSession() as session:
        async with session.begin():
            new_row = administrator(user=user,m_type=m_type)
            session.add(new_row)
            LOG.info(f"添加用户: \n{user} {m_type}")

""" 查询管理员用户 """
async def query_administrator(keyboard: str):
    async with DBSession() as session:
        result = await session.execute(select(administrator).filter(administrator.user == keyboard))
        return result.unique().scalars().all()

""" 删除管理员用户 """
async def del_administrator(keyboard: str):
    if await query_administrator(keyboard) != []:
        async with DBSession() as session:
            async with session.begin():
                await session.execute(delete(administrator).filter(administrator.user == keyboard))
                return True
    else:
        return None

""" 查询管理员用户 """
async def query_administrator_all():
    async with DBSession() as session:
        result = await session.execute(select(administrator))
        return result.unique().scalars().all()


#    id = Column(INTEGER,primary_key=True)
#    title = Column(TEXT)
#    url = Column(TEXT)
#    weight = Column(INTEGER)
""" 添加一行link """
async def insert_table_linkage(title,url,people,channel:bool,weight=0,m_type=3):
    if await query_link_table_linkage(url) != []:
        #LOG.error(f"{url} 重复链接")
        return None
    async with DBSession() as session:
        async with session.begin():
            new_row = linkage(title=title,url=url,people=people,channel=channel,weight=weight,m_type=m_type)
            session.add(new_row)
            #LOG.info(f"表添加一行: \n{title} {url} {people} {channel} {weight} {m_type}")
            return True

async def update_table_linkage(url,title,weight):
    if await query_link_table_linkage(url) == []:
        LOG.error(f"{url} 没有这个链接")
        return None
    
    async with DBSession() as session:
        async with session.begin():
            await session.execute(update(linkage).filter(linkage.url == url).values(weight = weight,title = title))
            LOG.info(f"更新数据: {url} {title} {weight}")
            return True

""" 删除链接 """
async def del_table_linkage(url):
    if await query_link_table_linkage(url) == []:
        LOG.error(f"{url} 没有这个链接")
        return None
    
    async with DBSession() as session:
        async with session.begin():
            await session.execute(delete(linkage).filter(linkage.url == url))
            return True


""" 查询链接是否已经存储的到数据库  """
async def query_link_table_linkage(keyboard: str):
    async with DBSession() as session:
        query_res = await session.execute(select(linkage).filter(linkage.url == keyboard))
        return query_res.all()

async def query_table_linkage_all():
    async with DBSession() as session:
        query_res = await session.execute(select(linkage))
        result = query_res.unique().scalars().all()
        return result

""" 模糊查询数据 """
async def query_blur_title_linkage(keywords: str):
    async with DBSession() as session:
        rule =  and_(*[linkage.title.like(f"%{keyword}%") for keyword in keywords])
        result = await session.execute(select(linkage).filter(rule))
        result = result.unique().scalars().all()
        LOG.info(f"模糊查询 {keywords}: 得到 {len(result)}条")
        return result


""" 模糊查询并排序 """
async def query_blur_title_linkage_sort(keywords: str):
    async with DBSession() as session:
        rule =  and_(*[linkage.title.like(f"%{keyword}%") for keyword in keywords])
        result = await session.execute(select(linkage).filter(rule).order_by(linkage.weight.desc()))
        result = result.unique().scalars().all()
        LOG.info(f"模糊查询 {keywords}: 得到 {len(result)}条")
        return result

""" 对数据进行加工，过滤，排序，美化 """
async def futter_build(list: Sequence[linkage],keyboard:str):
    """ 排序 """
    def build_list(list: Sequence[linkage],keyboard:str):
        similarites = []
        for item in list:
            mark = fuzz(str(item.title),keyboard)
            similarites.append((item,mark))
        LOG.info(f"按分数构建 {len(list)} 条链接")
        return similarites

    sorted_queue = sorted(build_list(list,keyboard),
                          key=lambda x: x[1],
                          reverse=True)

    LOG.info(f"排序构建 {len(list)} 条链接")
    return [item[0] for item in sorted_queue]
