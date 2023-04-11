import os
import config
import database
import time

import educa
import repouploader

from pyobigram.client import ObigramClient
from pyobigram.ttui import TTUI
from pyobidl.downloader import Downloader
from pyobidl.utils import sizeof_fmt,createID
from models.user import User

import ProxyCloud
import zipfile

DOWNLOADERS = {}
BOT_DOWNLOADERS = {}
RESPS = {}

def cancel_download(update,bot:ObigramClient):
    global DOWNLOADERS
    global BOT_DOWNLOADERS
    dl_id = str(update.data).replace('_','')
    if dl_id in DOWNLOADERS:
        DOWNLOADERS[dl_id].stop()
    if dl_id in BOT_DOWNLOADERS:
        BOT_DOWNLOADERS[dl_id]['stoping'] = True
    pass

def progress_downloader(dl:Downloader,filename,index,total,speed,time,args):
    try:
        bot:ObigramClient = args[0]
        message = args[1]
        tui:TTUI = args[2]
        args = {}
        args['task_id'] = dl.id
        args['filename'] = filename
        args['index'] = sizeof_fmt(index)
        args['total'] = sizeof_fmt(total)
        args['speed'] = sizeof_fmt(speed)
        args['time'] = sizeof_fmt(time)
        parse_mode,ui_text,markups = tui.render('dl',section='downloading',args=args)
        reply_markup = tui.parse_markups(markups)
        bot.edit_message(message,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)
    except:pass
    pass

def progress_download_bot(bot:ObigramClient,filename,index,total,speed,time,args):
    global BOT_DOWNLOADERS
    try:
        message = None
        dl_id = ''
        tui:TTUI = None
        try:
            message = args[0]
            dl_id = args[1]
            tui = args[2]
        except:pass
        if dl_id in BOT_DOWNLOADERS:
            BOT_DOWNLOADERS[dl_id]['filename'] = filename
        args = {}
        args['task_id'] = dl_id
        args['filename'] = filename
        args['index'] = sizeof_fmt(index)
        args['total'] = sizeof_fmt(total)
        args['speed'] = sizeof_fmt(speed)
        args['time'] = sizeof_fmt(time)
        parse_mode,ui_text,markups = tui.render('dl',section='downloading',args=args)
        reply_markup = tui.parse_markups(markups)
        bot.edit_message(message,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)
    except:pass
    if dl_id in BOT_DOWNLOADERS:
       if BOT_DOWNLOADERS[dl_id]['stoping']:
           stop.append(1)
    pass

def repo_upload_progress(filename, index, total, speed, time, args):
    try:
        bot = args[0]
        message = args[1]
        tui = args[2]
        task_id = args[2]

        args = {}
        args['task_id'] = task_id
        args['filename'] = filename
        args['index'] = sizeof_fmt(index)
        args['total'] = sizeof_fmt(total)
        args['speed'] = sizeof_fmt(speed)
        args['time'] = sizeof_fmt(time)

        parse_mode,ui_text,markups = tui.render('up',section='uploading',args=args)
        reply_markup = tui.parse_markups(markups)
        bot.edit_message(message,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)

    except Exception as ex:
        print(str(ex))


def repo_handle(update,bot:ObigramClient):
    global RESPS
    global DOWNLOADERS
    global BOT_DOWNLOADERS

    try:
        message_to_edit = update.message
        resp_id = update.data

        result = []
        output = None
        stoped = False

        if resp_id in RESPS:
            data = RESPS[resp_id]
            tui:TTUI = data['tui']
            user:User = data['user']
            infos = data['data']
            proxy = ProxyCloud.parse(user.config.cloud_proxy)
        
            for inf in infos:
                is_file = False
                url = ''
                fname = inf['fname']
                location = None
                if 'location' in inf:
                    is_file = True
                    location = inf['location']
                if 'furl' in inf:
                    url = inf['furl']
                if is_file:
                    if bot.contain_file(location):
                       dl_id = createID()
                       args = {'task_id':dl_id}
                       BOT_DOWNLOADERS[dl_id] = {'filename':'','stoping':False}
                       parse_mode,ui_text,markups = tui.render('dl',section='starting_file',args=args)
                       reply_markup = tui.parse_markups(markups)
                       bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)
               
                       try:
                          output = bot.mtp_download_file(location,'',progress_download_bot,(message_to_edit,dl_id,tui))
                       except Exception as ex:
                           pass

                       filename = BOT_DOWNLOADERS[dl_id]['filename']
                       stoping = BOT_DOWNLOADERS[dl_id]['stoping']
                       if not stoping:pass
                       else:
                           if output:
                              os.unlink(output)
                           output = None
                           stoped = True
                           args={}
                           args['down_url'] = ''
                           args['down_filename'] = filename
                           parse_mode,ui_text,markups = tui.render('dl',section='cancel',args=args)
                           bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
                else:
                    dl = Downloader()
                    dl.filename = fname
                    DOWNLOADERS[dl.id] = dl

                    args = {'task_id':dl.id}
                    parse_mode,ui_text,markups = tui.render('dl',section='starting',args=args)
                    reply_markup = tui.parse_markups(markups)
                    bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)

                    try:
                        output = dl.download_url(url,progressfunc=progress_downloader,args=(bot,message_to_edit,tui))
                    except:pass

                    if not dl.stoping:pass
                    else:
                        if output:
                            os.unlink(output)
                        output = None
                        stoped = True
                        args={}
                        args['down_url'] = ''
                        args['down_filename'] = ''
                        if dl.filename:
                            args['down_filename'] = dl.filename
                        parse_mode,ui_text,markups = tui.render('dl',section='cancel',args=args)
                        bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
                    DOWNLOADERS.pop(dl.id)
                    pass

    except:
        parse_mode,ui_text,markups = tui.render('dl',section='error',args=args)
        bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)

    if output:
        zipname = str(output).split('.')[0]
        mult = zipfile.MultiFile(zipname,1024 * 1024 * user.config.zips,ext='.rar')
        zip = zipfile.ZipFile(mult,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(output)
        zip.close()
        mult.close()
        session = repouploader.create_session(proxy)
        sessid = createID()
        for file in mult.files:
            resp = session.upload_file(file,repo_upload_progress,(bot,message_to_edit,tui,sessid))
            if resp:
               result.append({'fname':file,'url':resp.url})
        os.unlink(output)
        for file in mult.files:
            os.unlink(file)

    if len(result) > 0:
        bot.delete_message(message_to_edit)
        parse_mode,ui_text,markups = tui.render('resp_url',section='result')
        txtname = str(result[0]['fname']).split('.')[0] + '.txt'
        with open(txtname,'w') as txt:
            for item in result:
                txt.write(str(item['url'])+'\n')
        bot.send_file(message_to_edit.chat.id,txtname,caption=ui_text,reply_to_message_id=message_to_edit.reply_to_message.message_id)
        os.unlink(txtname)
        pass
    else:
        if not stoped:
            parse_mode,ui_text,markups = tui.render('resp_url',section='no_result')
            bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)

    pass

def process_all(update,bot:ObigramClient,user:User,tui:TTUI,args={}):
    global DOWNLOADERS
    global BOT_DOWNLOADERS
    global RESPS
    message = update.message
    text = ''
    try:
        text = message.text
    except:pass
    
    if '/start' in text:
        parse_mode,ui_text,markups = tui.render('start_cmd',args=args)
        reply_markup = tui.parse_markups(markups)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
        return

    if '/account' in text:
        text = str(text).replace('/account ','')
        if user:
            account = str(text).split(' ')
            if len(account)>0:
                user.config.cloud_username = account[0]
            if len(account)>1:
                user.config.cloud_password = account[1]
            args['cloud_username'] = user.config.cloud_username
            args['cloud_password'] = user.config.cloud_password
            text = '/my'

    if '/proxy' in text:
        text = str(text).replace('/proxy ','')
        if user:
            proxy = text
            user.config.cloud_proxy = proxy
            if user.config.cloud_proxy!='':
                args['proxy'] = True
            else:
                args['proxy'] = False
            text = '/my'

    if '/host' in text:
        text = str(text).replace('/host ','')
        if user:
            host = text
            user.config.cloud_host = host
            args['cloud_host'] = user.config.cloud_host
            text = '/my'

    if '/zip' in text:
        text = str(text).replace('/zip ','')
        if user:
            zip = 99
            try:
                zip = int(text)
            except:pass
            user.config.zips = zip
            args['user_zips'] = user.config.zips
            text = '/my'

    if '/my' in text:
        parse_mode,ui_text = tui.render('user_info',args=args)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        return

    if '/perm' in text: # add user permision
        text = str(text).replace('/perm ','')
        if user.is_admin:
            users = str(text).split(' ')
            for perm in users:
                args['perm_user'] = perm
                user_exist = database.get_user_from(username=perm)
                if user_exist:
                    parse_mode,ui_text = tui.render('perm_user',section='exist',args=args)
                    bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                else:
                    newuser = User(tg_id=str(int(time.time())),username=perm)
                    newuser.create_config()
                    newuser.set_admin(lvl=(user.admin_lvl-1))
                    saved = database.save_user(newuser)
                    if saved:
                        parse_mode,ui_text = tui.render('perm_user',section='permed',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                    else:
                        parse_mode,ui_text = tui.render('perm_user',section='error',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/ban' in text:
        text = str(text).replace('/ban ','')
        if user.is_admin:
            users = str(text).split(' ')
            for ban in users:
                args['ban_user'] = ban
                args['ban_lvl'] = user.admin_lvl
                user_exist = database.get_user_from(username=ban)
                if user_exist:
                    args['ban_lvl'] = user_exist.admin_lvl
                    if user.admin_lvl>user_exist.admin_lvl:
                        if database.delete_user(username=user_exist.username):
                           parse_mode,ui_text = tui.render('ban_user',section='baned',args=args)
                           bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                        else:
                            parse_mode,ui_text = tui.render('ban_user',section='error',args=args)
                            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                    else:
                        parse_mode,ui_text = tui.render('ban_user',section='error_lvl',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                else:
                    parse_mode,ui_text = tui.render('ban_user',section='error',args=args)
                    bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if 'http' in text:
        url = text
        if 'youtube' in text:
            pass
        else:
            dl = Downloader()
            infos = dl.download_info(url)
            if infos:
                i = 0
                for item in infos:
                    item['fsize'] = sizeof_fmt(item['fsize'])
                    infos[i] = item
                args['resp_id'] = dl.id
                args['infos'] = infos
                RESPS[dl.id] = {'tui':tui,'user':user,'data':infos}
                parse_mode,ui_text,markups = tui.render('resp_url',args=args)
                reply_markup = tui.parse_markups(markups)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
                pass

        pass

    if bot.contain_file(message):
        resp_id = createID()
        infos = []
        finfo = bot.mtp_get_file_info(message)
        infos.append(finfo)
        if infos:
            i = 0
            for item in infos:
                item['fsize'] = sizeof_fmt(item['fsize'])
                infos[i] = item
            args['resp_id'] = resp_id
            args['infos'] = infos
            RESPS[resp_id] = {'tui':tui,'user':user,'data':infos}
            parse_mode,ui_text,markups = tui.render('resp_url',args=args)
            reply_markup = tui.parse_markups(markups)
            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
            


    pass


ACCES_FREE = False
def message_handle(update,bot:ObigramClient):
    global ACCES_FREE

    tui = TTUI('templates/')

    message = update.message
    text = ''
    try:
        text = message.text
    except:pass
    username = message.chat.username

    user:User = database.get_user_from(username=username)
    access = True

    if user:
        pass
    else:
        if ACCES_FREE:
            user = User(tg_id=str(message.sender.id),username=username)
            user.create_config()
        elif username == config.TG_ADMIN:
            user = User(tg_id=str(message.sender.id),username=username)
            user.set_admin(lvl=999)
            user.create_config()
        else:
            access = False
                                                                  
    if not access:
        parse_mode,ui_text,markups = tui.render('not_acces',args)
        reply_markup = tui.parse_markups(markups)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
        return

    if '/free' in text:
        if user.is_admin and user.admin_lvl==user.admin_lvl_max:
           if ACCES_FREE:
              ACCES_FREE = False
           else:
               ACCES_FREE = True

    args = {}
    if user:
        user.tg_id = str(message.sender.id)
        args['username'] = user.username
        args['tg_id'] = user.tg_id
        args['is_admin'] = user.is_admin
        args['admin_lvl'] = user.admin_lvl

        args['cloud_host'] = user.config.cloud_host
        args['cloud_username'] = user.config.cloud_username
        args['cloud_password'] = user.config.cloud_password
        args['cloud_repo_id'] = user.config.cloud_repo_id
        args['user_zips'] = user.config.zips
        if user.config.cloud_proxy!='':
           args['proxy'] = True
        else:
           args['proxy'] = False

    process_all(update,bot,user,tui,args)

    if user:
       database.save_user(user)


if __name__ == '__main__':
    bot = ObigramClient(config.BOT_TOKEN,api_id=config.TG_API_ID,api_hash=config.TG_API_HASH)
    bot.onMessage(message_handle)
    bot.onCallbackData('/rup_',repo_handle)
    bot.onCallbackData('/cancel_',cancel_download)
    print('bot is runing!')
    bot.run();