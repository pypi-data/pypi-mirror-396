from .base import *


def sql_engine(
        username:str=None, 
        password:str=None, 
        host:str=None, 
        port:str=None,
        database:str=None,
        drivername:str="mysql",
    ):
    r"""MySQL Engine
    username : 접속 사용자 정보 
    password : 접속 사용자 비밀번호
    host     : 접속주소 
    port     : 접속주소 Port
    database : DataBase 이름 """
    # db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    sql_info = {
        "username":username,
        "password":password,
        "host":host,
        "port":port, 
        "database":database,
        "drivername":drivername,
    }
    url_db = sqlalchemy.engine.URL.create(**sql_info)
    engine = sqlalchemy.create_engine(url_db, echo=False)
    return engine # pandas.read_sql(sql_query, engine)


def sql_tables(engine, raw=False):
    r""" 해당 DataBase 의 Table 정보 출력하기
    engine : sql_engine() 엔진정보
    raw    : table info Raw """
    meta = MetaData()
    meta.reflect(bind=engine)
    table_dict = dict(meta.tables)
    if raw:
        return table_dict
    return sorted(table_dict.keys())
