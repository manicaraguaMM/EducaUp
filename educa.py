import os
import time
import socks
import socket
import uuid
import requests
from random import randint
from functools import partial
from bs4 import BeautifulSoup
from ProxyCloud import ProxyCloud
from requests_toolbelt import MultipartEncoder
from requests_toolbelt import MultipartEncoderMonitor
import requests_toolbelt as rt
import json

class CallingUpload:
	def __init__(self, func,filename,args):
		self.func = func
		self.args = args
		self.filename = filename
		self.time_start = time.time()
		self.time_total = 0
		self.speed = 0
		self.last_read_byte = 0
	def __call__(self,monitor):
		self.speed += monitor.bytes_read - self.last_read_byte
		self.last_read_byte = monitor.bytes_read
		tcurrent = time.time() - self.time_start
		self.time_total += tcurrent
		self.time_start = time.time()
		if self.time_total>=1:
			clock_time = (monitor.len - monitor.bytes_read) / (self.speed)
			if self.func:
				self.func(self.filename,monitor.bytes_read,monitor.len,self.speed,clock_time,self.args)
			self.time_total = 0
			self.speed = 0

class EducaCli(object):
    def __init__(self,user,passw,proxy:ProxyCloud=None):
        self.username = user
        self.password = passw
        self.host = 'https://educa.uho.edu.cu/'
        self.proxy = None
        if proxy :
           self.proxy = proxy.as_dict_proxy()
        self.session = requests.Session()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'}

    def login(self):
        url = self.host + '/wp-login.php'
        resp = self.session.get(url,proxies=self.proxy,headers=self.headers)
        
        payload = {}
        payload['log'] = self.username
        payload['pwd'] = self.password
        payload['wp-submit'] = 'Acceder'
        payload['redirect_to'] = f'{self.host}wp-admin/'
        payload['testcookie'] = '1'
        
        resp = self.session.post(url,data=payload,proxies=self.proxy,headers=self.headers)
        
        if resp.url!=url:
            print('Login exito')
            return True

        print('Login faild')
        return False

    def createID(self,count=8):
        from random import randrange
        map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        id = ''
        i = 0
        while i<count:
            rnd = randrange(len(map))
            id+=map[rnd]
            i+=1
        return id

    def upload(self,file,id='',progressfunc=None,args=()):
        try:

            self.session.get(f'{self.host}wp-admin/admin.php?page=recursos-educativos-pregrado-admin',proxies=self.proxy,headers=self.headers)

            if id=='':
               id = self.createID(9)
            
            of = open(file,'rb')
            b = uuid.uuid4().hex
            upload_data = {
                'nombre':(None,''),
                'descripcion':(None,''),
                'id_categoria':(None,''),
                'carrera':(None,''),
                'id_disciplina':(None,''),
                'enlace':(None,''),
                'archivo':(None,''),
                }
            upload_file = {
                's97304e7e':(file,of,'application/octet-stream'),
                **upload_data
                }
            post_file_url = self.host + 'ci_portal_uho/index.php/recursos_pre/my_grocery_recursos_pred/upload_file/archivo'
            encoder = rt.MultipartEncoder(upload_file,boundary=b)
            progrescall = CallingUpload(progressfunc,file,args)
            callback = partial(progrescall)
            monitor = MultipartEncoderMonitor(encoder,callback=callback)
            resp = self.session.post(post_file_url,data=monitor,headers={"Content-Type": "multipart/form-data; boundary="+b,**self.headers
                                                                         },proxies=self.proxy)
            of.close()
            jsondata = json.loads(resp.text)
            return jsondata['files']
        except Exception as ex:
            print(str(ex))
            return None

#cli = EducaCli('livansr','delia0021.')
#loged = cli.login()
#if loged:
#    data = cli.upload('requirements.zip')
#    print(data)