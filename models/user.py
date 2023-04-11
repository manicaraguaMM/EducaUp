import time
from .user_config import UserConfig

class User(object):

    def __init__(self,id=None,tg_id='',username='',is_admin=False,admin_lvl=0):
        self.id = id
        if not id:
            self.id = int(time.time()) + 1
        self.tg_id = tg_id
        self.username = username
        if is_admin==0 or is_admin=='0':
           self.is_admin = False
        else:
            self.is_admin = True
        self.admin_lvl = admin_lvl
        self.config:UserConfig = None
        self.admin_lvl_max = 999

    def set_admin(self,admin=True,lvl=1):
        self.is_admin = admin
        self.admin_lvl = lvl

    def create_config(self,id=None,ref_id='',cloud_host='',cloud_username='',cloud_password='',cloud_repo_id=4,zips=100, cloud_proxy=''):
        if not id:
            id = int(time.time()) + 1
        if ref_id=='':
            ref_id = self.tg_id
        self.config = UserConfig(id,self.username,cloud_host,cloud_username,cloud_password,cloud_repo_id,zips, cloud_proxy)

    def set_config(self,id,ref_id,cloud_host,cloud_username,cloud_password,cloud_repo_id,zips, cloud_proxy,cd):
        self.config = UserConfig(id,ref_id,cloud_host,cloud_username,cloud_password,cloud_repo_id,zips, cloud_proxy,cd)

    def to_save_query(self,table='users',update=True):
        admin = 0
        if self.is_admin:
            admin  = 1
        query = f"INSERT INTO `{table}` (id,tg_id,username,is_admin,admin_lvl) VALUES ({self.id},'{self.tg_id}','{self.username}',{admin},{self.admin_lvl});"
        if update:
            query = f"UPDATE `{table}` SET tg_id='{self.tg_id}', username='{self.username}', is_admin={admin}, admin_lvl={self.admin_lvl} WHERE username='{self.username}';"
        if self.config:
            query += self.config.to_save_query(update=update)
        return query

    def to_delete_query(self,table='users'):
        config_query = ''
        if self.config:
            config_query = self.config.to_delete_query()
        return f"DELETE FROM `{table}` WHERE username='{self.username}';" + config_query