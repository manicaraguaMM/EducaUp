class UserConfig(object):
    def __init__(self,id,ref_id,cloud_host,cloud_username,cloud_password,cloud_repo_id,zips, cloud_proxy,cd='/'):
        self.id = id
        self.ref_id = ref_id
        self.cloud_host = cloud_host
        self.cloud_username = cloud_username
        self.cloud_password = cloud_password
        self.cloud_repo_id = cloud_repo_id
        self.zips = zips
        self.cloud_proxy = cloud_proxy
        self.cd = cd

    def to_save_query(self,table='configs',update=True):
        query = f"INSERT INTO `{table}` (id,ref_id,cloud_host,cloud_username,cloud_password,cloud_repo_id,zips,cloud_proxy,cd) VALUES ({self.id},'{self.ref_id}','{self.cloud_host}','{self.cloud_username}','{self.cloud_password}','{self.cloud_repo_id}','{self.zips}','{self.cloud_proxy}','{self.cd}');"
        if update:
            query = f"UPDATE `{table}` SET id='{self.id}', ref_id='{self.ref_id}', cloud_host='{self.cloud_host}', cloud_username='{self.cloud_username}', cloud_password='{self.cloud_password}', cloud_repo_id='{self.cloud_repo_id}', zips={self.zips}, cloud_proxy='{self.cloud_proxy}', cd='{self.cd}' WHERE ref_id='{self.ref_id}';"
        return query

    def to_delete_query(self,table='configs'):
        return f"DELETE FROM `{table}` WHERE ref_id='{self.ref_id}';"