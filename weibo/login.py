# coding:utf-8
# import导包部分
import requests
import base64
import re
import rsa
import urllib
import json
import binascii

'''
#INFO信息说明
1， 在提交POST请求之前， 需要GET 获取两个参数。
       地址是：http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)
       得到的数据中有 "servertime" 和 "nonce" 的值， 是随机的，其他值貌似没什么用。
2， 通过httpfox/chrome源码分析 观察POST 的数据， 参数较复杂，其中 “su" 是加密后的username, "sp"是加密后的password。"servertime" 和 ”nonce" 是上一步得到的。其他参数是不变的。
    username 经过了BASE64 计算： username = base64.encodestring( urllib.quote(username) )[:-1];
    password 经过了三次SHA1 加密， 且其中加入了 servertime 和 nonce 的值来干扰。
    即： 两次SHA1加密后， 将结果加上 servertime 和 nonce 的值， 再SHA1 算一次。
'''
# user,password用户名密码,使用自己注册的sina用户名密码
class Login(object):
    def __init__(self):
        self.username = '账号'
        self.password = '密码'
        self.url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625'
        self.url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'

    def PreLogin(self):
        session = requests.session()
        # get servertime,nonce, pubkey,rsakv获取登录session相关登录时间等信息
        resp = session.get(self.url_prelogin,headers={'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
        json_data = re.search('\((.*)\)', resp.content.decode()).group(1)
        data = json.loads(json_data)
        servertime = data['servertime']
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']

        # calc su，第一步加密用户名
        su = base64.b64encode(urllib.parse.quote(self.username).encode())
        # calc sp，第二步，加密密码
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
        sp = binascii.b2a_hex(rsa.encrypt(message.encode(), key))
        # post reqest,第三部，提交请求
        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsakv': rsakv,
}
        return session,postdata

    def Login(self,session,postdata):
        resp = session.post(self.url_login, data=postdata)
        login_url = re.findall("replace\('(.*)'\)", resp.content.decode('gbk'))[0]
        resp = session.get(login_url)
        uid = re.findall('"uniqueid":"(\d+)",', resp.content.decode('gbk'))[0]
        url = "http://weibo.com/u/" + uid
        resp = session.get(url)
        return session.cookies

    def AutoLogin(self):
        session,postdata = self.PreLogin()
        cookiejar = self.Login(session,postdata)
        cookie = cookiejar.get_dict()
        return cookie

if __name__ == '__main__':
    loger =  Login()
    loger.AutoLogin()