import mysqli
from models.user import User
from models.user_config import UserConfig


def get_users():
    result = mysqli.query_fetch('SELECT * FROM `users`')
    user_list = []
    if result:
        for ur in result:
            user = User(*ur)
            query = "SELECT * FROM `configs` WHERE ref_id='"+user.username+"'"
            config = mysqli.query_fetch(query)
            if config:
                if len(config)>0:
                    cfg = config[0]
                    user.set_config(*cfg)
            user_list.append(user)
    return user_list

def get_user_from(username=None,tg_id=None):
    users = get_users()
    for user in users:
        if username:
            if user.username==username:
               return user
        if tg_id:
            if user.tg_id==tg_id:
               return user
    return None

def save_user(user:User=None):
    if user:
        update = False
        get_user = get_user_from(user.username,user.tg_id)
        if get_user:
            update = True
        query = user.to_save_query(update=update)
        completed = mysqli.query(query)
        return completed
    return False

def delete_user(username=None,tg_id=None):
    users = get_users()
    query = ''
    for user in users:
        if username:
            if user.username==username:
               query = user.to_delete_query()
               break
        if tg_id:
            if user.tg_id==tg_id:
               query = user.to_delete_query()
               break
    result = False
    for q in str(query).split(';'):
        if q!='':
           result = mysqli.query(q)
    return result