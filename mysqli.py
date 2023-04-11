# require libraries sqlite3
import pymysql
import config

def connect():
    return pymysql.connect(autocommit=True,
       host=config.DB_HOST,                 # your host, usually localhost
       user=config.DB_HOST_USERNAME,        # your username
       passwd=config.DB_HOST_PASSWORD,      # your password
       db=config.DB_NAME)                   # name of the data base

def create_table(table_name='newtable',structures={}):
    CONN = connect()
    try:
        cur = CONN.cursor()
        sql  = 'CREATE TABLE IF NOT EXISTS `users` ('
        sql += '`id` int(11) NOT NULL DEFAULT current_timestamp(),'
        for key in structures:
            try:
                type = structures[key]['type']
                value = structures[key]['value']
            except:
                type = 'text'
                value = structures[key]
            sql += f'`{key}` {type} '
            if value=='' or value == None:
               sql += f'`NOT NULL,'
            if value!='':
               sql += f'`DEFAULT {value},'
        sql += 'PRIMARY KEY (`id`)'
        sql += ') ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;'
        cur.execute(sql)
        close(CONN)
        return True
    except:pass
    return False

def query(query:str):
    CONN = connect()
    try:
        cur = CONN.cursor()
        result = 0
        for q in (str(query)).split(';'):
            if q!='':
               result += cur.execute(q)
        close(CONN)
        if result>0:
           return True
        return False
    except Exception as ex:
        print(str(ex))
    return False

def query_fetch(query:str):
    CONN = connect()
    try:
        cur = CONN.cursor()
        result = cur.execute(query)
        fetch = cur.fetchall()
        close(CONN)
        return fetch
    except Exception as ex:
        print(str(ex))
    return None

def close(CONN):
    try:
        CONN.close()
        return True
    except Exception as ex:
        print(str(ex))
    return False