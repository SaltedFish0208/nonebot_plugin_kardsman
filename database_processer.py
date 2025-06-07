#这里存放数据库的操作
import sqlite3
from .config import Config
from nonebot import get_plugin_config

plugin_config: Config = get_plugin_config(Config)
Kards_resource = plugin_config.Kards_resource

database = f"{Kards_resource}/cards.db"

#从数据库获取某个表的某条数据
def FetchData(tablename, columnname, rule):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'SELECT {columnname} FROM {tablename} WHERE {rule}')
    backData = sqlCursor.fetchall()
    sqlConnection.close()
    return backData

#模糊查询并返回结果 SELECT * from app_info where appName like '%网%';
def FuzzyQuery(tablename, columnname, keyword):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'SELECT * FROM {tablename} WHERE {columnname} LIKE "%{keyword}%"')
    backData = sqlCursor.fetchall()
    sqlConnection.close()
    return backData

#模糊查询两列并返回结果
def FuzzyQuery2c(tablename, columnname1, columnname2, keyword):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'SELECT * FROM {tablename} WHERE {columnname1} LIKE "%{keyword}%" OR {columnname2} LIKE "%{keyword}%"')
    backData = sqlCursor.fetchall()
    sqlConnection.close()
    return backData

#随机选择一个条目
def RandomChoice(tablename):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'SELECT * FROM {tablename} ORDER BY RANDOM() LIMIT 1;')
    backData = sqlCursor.fetchall()
    sqlConnection.close()
    return backData

#修改某条数据
def UpdateData(tablename, columnname, newdata, rule):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'UPDATE {tablename} SET {columnname}={newdata} WHERE {rule}')
    sqlConnection.commit()
    sqlConnection.close()
    return "ok"

#查询表内是否有某条目，是则返回True，否则返回False
def QueryDataExist(tablename, columnname, rule):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'SELECT {columnname} FROM {tablename} WHERE EXISTS(SELECT {columnname} FROM {tablename} WHERE {rule})')
    backData = sqlCursor.fetchall()
    sqlConnection.close()
    if len(backData) > 0:
        return True
    else:
        return False
    
#向数据库写入数据 tablename=表名 columnname=列名 writeindata=写入数据    
def WriteInData(tablename:str, columnname:str, writeindata:str):
    sqlConnection = sqlite3.connect(database)
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute(f'INSERT INTO {tablename} ({columnname}) VALUES ({writeindata})')
    sqlConnection.commit()
    sqlConnection.close()