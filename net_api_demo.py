'''
Version:1.0.2
Author:TAber-W
Github:https://github.com/TAber-W

注意：若最后返回错误uid，可通过加减时间戳，重启服务器来清除缓存

2022 8 29 
增加登陆cookie请求，保存cookie，（未加入cookie有效性检查，下版本更新）
'''
from ast import keyword, parse
from http import cookies
import requests
import re
import cv2
import base64
import numpy as np
import datetime
import urllib.parse
import os


global key
key_status = 0
'''realIP参数，解决460错误'''
realIP = "?realIP="

'''通过opencv编码based64生成图片'''
def decode_base64_cv_img(base64_data):
    global cookie_s
    img = base64.b64decode(base64_data)
    img_array = np.fromstring(img, np.uint8)  # 转换np序列
    img_raw = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 转换Opencv格式BGR
    img_gray = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)  # 转换灰度图
    path = "/Users/apple/Desktop/netmusic/app/.hyper_music.txt"
    while(1):
        cv2.imshow("img bgr", img_raw)
        code = qr_code_check()[2]
        r = qr_code_check()[3]
        if code == "800":
            cv2.destroyAllWindows()
            print("二维码过期，请重新登陆")
            break
        if code == "803":
            cv2.destroyAllWindows()
            #print(r.text)
            cookie_s=re.findall(r'"cookie":"(.+?)"}',r)[0]
            Note=open(path,mode='w')
            Note.write(cookie_s)
            print("登陆成功")
            break
        if code == "801":
            print("等待扫码")
         
        if code == "802":
            print("等待授权")
       
           
        #print(qr_code_check()[0],code)
        cv2.waitKey(1000)
    
'''服务器ip和端口，若是本地运行，ip则为localhost或127.0.0.1'''
def serve_ip():
    ip = ""
    return ip

'''利用key_status确保所有函数使用的是一个key，在decode_base64_cv_img
生成二维码时会判断是否过期。否则不会生成新key。
'''
def get_qr_key():
    global key_status,key_new
    keywords="/login/qr/key"
    get_link = serve_ip()+keywords+"?"+get_time_update()
    r = requests.get(get_link)
    if  key_status == 0:
        key = re.findall(r'":"(.+?)"}',r.text)
        key_status = 1
        key_new = key[0]
    return key_new

'''获取登陆二维码图片的base64编码'''
def get_qr_img():
    keywords = "/login/qr/create"
    get_link = serve_ip()+keywords+"?"+"key="+get_qr_key()+"&qrimg=true"+"&"+get_time_update()
    r = requests.get(get_link)
    img_base64 = re.findall(r'base64,(.+?)"}',r.text)
    decode_base64_cv_img(img_base64[0])

'''时间戳：年月日时分秒'''
def get_time_update():
    i = datetime.datetime.now()
    time = "timestamp="+str(i.year)+str(i.month)+str(i.day)+str(i.hour)+str(i.minute)+str(i.second)
    return time

'''获取登陆状态'''
def get_login_statu():
    keywords = "/login/status"
    get_link = serve_ip()+keywords
    r = requests.get(get_link)
    code = re.findall(r'code":(.+?),"',r.text)[0]
    #print(get_link,r.text)
    if code == "200":
        return "logined"
    else:
        return "loginull"
'''获取用户uid'''
def get_uid():
    if get_login_statu() == "logined":
        keywords = "/user/account"
        get_link = serve_ip()+keywords+"?cookie="+read_cookie_file()
        r = requests.get(get_link)
        uid = re.findall(r'id":(.+?),"userName":',r.text)[0]
        return uid
    else:
        print("未登陆或登录异常！")
        return 0

'''检查二维码状态'''
def qr_code_check():
    
    keywords = "/login/qr/check"
    get_link = serve_ip()+keywords+"?key="+ get_qr_key() +"&"+get_time_update()
    r = requests.get(get_link)
    qr_code_status = re.findall(r'message":"(.+?)","cookie"',r.text)[0]
    code = re.findall(r'code":(.+?),"message"',r.text)[0]
    return qr_code_status,get_link,code,r.text

'''获取首页轮播信息'''
def get_banner_info():
    keywords = "/banner?type=0"
    get_link = serve_ip()+keywords
    r = requests.get(get_link)
    info_type = re.findall(r'"typeTitle":"(.+?)","url"',r.text)
    print(info_type)
    return info_type

'''获取每日推荐'''
def get_daily_rec():
    keywords = "/recommend/songs"
    get_link = serve_ip()+keywords+"?cookie="+read_cookie_file()
    r = requests.get(get_link)
    print(r.text)


'''检查是否存在本地cookie'''
def check_cookie_file():
    path = "/Users/apple/Desktop/netmusic/app/.hyper_music.txt"
    a = os.path.exists(path)
    if a!=True:
        get_qr_img()

'''从文件读取cookie'''
def read_cookie_file():
    path = "/Users/apple/Desktop/netmusic/app/.hyper_music.txt"
    with open(path, "r", encoding='utf-8') as f:  #打开文本
        data = f.read()   #读取文本
        #print(data)
    return data

'''获取用户信息，歌单数量，mv数量等'''
def get_user_info():
    keywords = "/user/subcount"
    get_link = serve_ip()+keywords+"?cookie="+read_cookie_file()
    r = requests.get(get_link)
    print(r.text)

'''获取账号信息，头像，签名等'''
def get_account_info():
    keywords = "/user/account"
    get_link = serve_ip()+keywords+"?cookie="+read_cookie_file()
    r = requests.get(get_link)
    print(r.text)

    


#check_cookie_file()
#print (get_uid())
#get_daily_rec()
get_account_info()


