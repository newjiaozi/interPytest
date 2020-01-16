import sqlite3
from com.src.test.logger import logger
import os

def createTable():
    sqlite3_path = os.path.join(os.path.dirname(__file__), "..", "config", "db.sqlite3")
    conn = sqlite3.connect(sqlite3_path)
    cursor = conn.cursor()
    cursor.execute('''create table tmpDictJson(tmpKey varchar(11) primary key,tmpValue varchar(5000)); ''')
    conn.commit()
    conn.close()

def getCursor():
    sqlite3_path = os.path.join(os.path.dirname(__file__), "..", "config", "db.sqlite3")
    conn = sqlite3.connect(sqlite3_path)
    cursor = conn.cursor()
    return conn,cursor

def insertTmp(conn,cursor,tmpKey,tmpValue):
    sql = '''insert into tmpDictJson(tmpKey,tmpValue) values(?,?)'''
    cursor.execute(sql, (tmpKey,tmpValue))
    conn.commit()

def updateTmp(conn,cursor,tmpKey,tmpValue):
    if getTmp(cursor,tmpKey):
        sql = '''update tmpDictJson set tmpValue = ? where tmpKey= ?'''
        cursor.execute(sql, (tmpValue,tmpKey))
        conn.commit()
    else:
        insertTmp(conn, cursor, tmpKey, tmpValue)

def getTmp(cursor,tmpKey):
    sql = '''select tmpValue from tmpDictJson where tmpKey=?'''
    cursor.execute(sql,(tmpKey,))
    res = cursor.fetchone()
    if res:
        return res[0]
    else:
        return None


if __name__ == "__main__":
    pass