# _*_ encoding: utf-8 _*_
import requests
import time
import json
import os
import sys
from redis import StrictRedis
from nsq_msgmaker import publishnsqmessage
from multiprocessing import Pool
import random
#import pandas as pd
"""
    拿到streetid
"""
rdb = StrictRedis(host='192.168.100.90',port='6379')
proxy = {
    'http': 'http://127.0.0.1:1087',
    'https': 'http://127.0.0.1:1087'
}
headers = {
    'Accept':'application/json',
    'referer':'https://www.instagram.com/explore/locations/',
    'Access-Control-Allow-Credentials':'true',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'content-type':'application/json',
    'origin':'https://www.starnow.co.nz',
    'Referer':'https://www.starnow.co.nz/talent/?p=1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    #    'cookie': '登陆获得'
}
def get_id_from_pages():
    # 获取国家信息 {id, name, slug}
    # 先解析， 如果下一页不为null， 则继续请求下一页
    page = 1
    while page:
        try:#这里可能包含请求页面所需内容为空，请求报错等错误
            resp = getcountry_page(page)
            # 存下需要的的信息，这一步将信息保存为文件，为每个国家创建一个redis字段,然后将后面获得的uid放在国家下
            memberlist = resp['Members']
            for member in memberlist:
                id =  member['MemberID']
                name = member['DisplayName']
                print id,name
                with open('id_list','a+') as load_a:
                    load_a.write(str(id)+','+str(name)+'\n')
            #    get_img(id,name)
            # 如果有下一页
            page += 1
        except Exception,e:
            page += 1
            # 如果没有
            print e,
            #如果 为请求错误可以试着重连，如果为解析内容时错误，则uid+=1 不再重试

#给定一个页码，返回该页的国家信息
def volue_null(id,page):
    url = 'https://www.starnow.co.nz/api2/ProfileApi/ProfilePhotos?memberId={}&page={}&limit=30'.format(id,page)
    response = requests.get(url)
    res = json.loads(response.content)
    total_count = res['totalPhotoCount']
    imglist = res['data']
    return len(imglist)
def get_img(id_name):
  #  topic = 'starunvisitedalbum'
  #  img_list = []
    id = id_name.strip().split(',')[0]
  #  name = id_name.strip().split(',')[1]
    page = 0
    num = 0
    url = 'https://www.starnow.co.nz/api2/ProfileApi/ProfilePhotos?memberId={}&page={}&limit=30'.format(id, page)
    response = requests.get(url)
    res = json.loads(response.content)
    #print res
    total_count = res['totalPhotoCount']
    imglist = res['data']
    for img in imglist:
        num += 1
        img = img['imageLarge']
    #    print img
    #    img_list.append(img)
        downimg(id,img)
    while volue_null(id,page):
        page += 1
        url = 'https://www.starnow.co.nz/api2/ProfileApi/ProfilePhotos?memberId={}&page={}&limit=30'.format(id, page)
        response = requests.get(url)
        res = json.loads(response.content)
        total_count = res['totalPhotoCount']
        imglist = res['data']
        for img in imglist:
            num += 1
            img = img['imageLarge']
        #    print img
        #    img_list.append(img)
            downimg(id,img)
    #publishnsqmessage(topic,img_list)
    #print img_list
    #p = Pool(10)
    #for img in img_list:
    #    p.apply(downimg,(name,img,))
    #p.close()
    #p.join()

def downimg(id,img):
   # initial = name[0:1].lower()
    img_name = img.split('/')[-2]+'_'+img.split('/')[-1]
    new_img = requests.get(img).content
    new_path = os.path.join('./new_image',id)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    with open(os.path.join(new_path,img_name),'wb') as load_b:
        load_b.write(new_img)
    print id,img
def getcountry_page(page):
    url = "https://api.starnow.com/v1/talentdirectory/search"
    #data = {'page':page}
    data = {'Filters': [{'Key': "categoryId", 'Value': 0}, {'Key': "p", 'Value': page}]}
    payload = json.dumps(data)
    #co = get_cookie().get_random_cookie()
    #ua = get_UserAgent().get_random_useragent()
    #if ua and co:
    #    headers.setdefault('user-agent', ua)
#   #     headers.setdefault('cookie', co)
    #    headers.setdefault('cookie','mid=W3QMowAEAAHDSswyQFpl3loPm_6T; mcd=3; fbm_124024574287414=base_domain=.instagram.com; csrftoken=DNTTKc5tqyscPCohJSNHbC60sJoESgAY; ds_user_id=8468319744; sessionid=IGSC68f19e13373ed15a471ebaff8415523377aa48cfe7db5af83389d1c6b97097ae%3AstohzHm9xGc64GJjERZCIFAQvGbvWTez%3A%7B%22_auth_user_id%22%3A8468319744%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_platform%22%3A4%2C%22_token_ver%22%3A2%2C%22_token%22%3A%228468319744%3Ab1TRQWTUIzqYEpUMuA570eSAlqBGi76x%3Ad3dddbd20b47362159b6f47f8ae23a433c086ac2f435f7e7fdc14f760d0147af%22%2C%22last_refreshed%22%3A1537337065.6304681301%7D; csrftoken=DNTTKc5tqyscPCohJSNHbC60sJoESgAY; rur=ATN; urlgen="{\"97.64.120.51\": 25820}:1g2dM9:738vvzzHfo3H6K9UruUQIQ_KXqU')

    response = requests.request("post", url, data=payload, headers=headers)
    #response = requests.post(url, data=data, headers=headers)
    resp = json.loads(response.content)
    return resp






if __name__ == "__main__":
    p = Pool(20)
    id_list =[]
 #   id = sys.argv[1]
 #   name = sys.argv[2] 
 #   get_img(id,name)
    with open('id_list','r') as load_r:
        id_list = load_r.readlines()
    for id_name in id_list:
     #   get_img(id_name)
        p.apply_async(get_img,(id_name,))
    p.close()
    p.join()
 #   get_id_from_pages()
 #   get_img('4697962','Jamie')
