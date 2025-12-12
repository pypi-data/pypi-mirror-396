import os
import sys
import time
import json
import hmac
import hashlib
import codecs
import base64
import ssl
import six
import six.moves.urllib as urllib
import traceback
import certifi

home_path = os.path.expanduser('~')
cache_path = os.path.join(home_path, '.dding')
file_name = cache_path + '/config.json'

def http_post_data(url,data):
    try:
        # headers = {'Content-Type': 'application/json'}
        # req = urllib.request.Request(url=url, headers=headers, data=json.dumps(data).encode())
        # response = urllib.request.urlopen(req,cafile=certifi.where())
        # res = response.read()
        # print(res.decode("utf8"))
        
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url=url, headers=headers, data=json.dumps(data).encode())
        # 创建 SSL 上下文，指定 CA 证书
        context = ssl.create_default_context(cafile=certifi.where())
        response = urllib.request.urlopen(req, context=context)
        res = response.read()
        print(res.decode("utf8"))
    except Exception as e:
        traceback.print_exc()
        print(e)

def http_post(url, msgtype, title, content):
    """
    http posts
    :param url:
    :param content:
    :return:
    """
    try:
        headers = {'Content-Type': 'application/json'}
        if msgtype == 'text':
            data = {"msgtype": msgtype, "text": {"content": content}}
        else:
            data = {
                "msgtype": msgtype,
                "markdown": {
                    "title": title,
                    "text": content.replace('\\n', '\n')
                },
                "at": {
                    "isAtAll": False
                }
            }
        req = urllib.request.Request(url=url, headers=headers, data=json.dumps(data).encode())
        response = urllib.request.urlopen(req,cafile=certifi.where())
        res = response.read()
        print(res.decode("utf8"))
    except Exception as e:
        traceback.print_exc()
        print(e)


def init():
    """
    初始化
    :return:
    """
    lst = []
    print("help url: https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq")
    token = six.moves.input("input token:")
    secret = six.moves.input("input secret:")
    if token == "" or secret == "":
        print("token or secret empty!! please check")
        sys.exit(1)
    else:
        if len(token) > 65:
            token = token[-64:]
        lst.append({
            'group': 'default',
            'token': token,
            'secret': secret
        })

    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
    save_config(lst)
    return read_config()


def read_config():
    return json.load(codecs.open(file_name, 'r', 'utf-8'))


def save_config(content):
    return json.dump(content, codecs.open(file_name, 'w', 'utf-8'), sort_keys=True, indent=4, separators=(',', ':'))


def check_config():
    dic = {}
    if not os.path.exists(file_name):
        lst = init()
    else:
        lst = read_config()
    for item in lst:
        platform = item.get('platform', 'dding')  # 默认为钉钉
        group = item['group']
        
        # 创建二级字典结构: dic[platform][group]
        if platform not in dic:
            dic[platform] = {}
        dic[platform][group] = item
    
    return dic

def notify_feishu(group='default',title='', content='', msgtype='markdown'):
    try:
        dic = check_config()
        
        # 检查飞书配置是否存在
        if 'feishu' not in dic or group not in dic['feishu']:
            print(f"飞书配置未找到，group: {group}")
            print("请检查配置文件中是否有正确的飞书配置")
            return
            
        config = dic['feishu'][group]
        token = config['token']
        secret = config['secret']
        print("-" * 60)
        print('platform:\tFeishu')
        print('group:\t%s' % (group))
        print('token:\t%s' % (token))
        print('secret:\t%s' % (secret))
        print("-" * 60)

        # accesstoken_url = 'https://oapi.dingtalk.com/robot/send?access_token='
        accesstolen_url= 'https://open.feishu.cn/open-apis/bot/v2/hook/'
        timestamp=round(time.time())
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        url = '%s%s' %(accesstolen_url,token)

        data={
                "timestamp": timestamp,
                "sign": sign,
                "msg_type": "text",
                "content": {
                        "text": "request example"
                }
        }
        http_post_data(url,data)
    except Exception as e:
        traceback.print_exc()
        print(e)

# def notify_dding(group='default', content='',type='text'):
def notify_dding(group='default', title='', content='', msgtype='markdown'):
    try:
        dic = check_config()
        
        # 检查钉钉配置是否存在
        if 'dding' not in dic or group not in dic['dding']:
            print(f"钉钉配置未找到，group: {group}")
            print("请检查配置文件中是否有正确的钉钉配置")
            return
            
        config = dic['dding'][group]
        token = config['token']
        secret = config['secret']
        print("-" * 60)
        print('group:\t%s' % (group))
        print('token:\t%s' % (token))
        print('secret:\t%s' % (secret))
        print("-" * 60)
        accesstoken_url = 'https://oapi.dingtalk.com/robot/send?access_token='
        timestamp = int(round(time.time() * 1000))
        secret_enc = secret.encode()
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode()
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = '%s%s&timestamp=%s&sign=%s' % (accesstoken_url, token, timestamp, sign)
        http_post(url, msgtype, title, content)
    except Exception as e:
        traceback.print_exc()
        print(e)

def notify_dding_token_secret(token,secret,title='',content='',msgtype='markdown'):
    try:
        dic = check_config()
        accesstoken_url = 'https://oapi.dingtalk.com/robot/send?access_token='
        timestamp = int(round(time.time() * 1000))
        secret_enc = secret.encode()
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode()
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = '%s%s&timestamp=%s&sign=%s' % (accesstoken_url, token, timestamp, sign)
        http_post(url, msgtype, title, content)
    except Exception as e:
        traceback.print_exc()
        print(e)

def notify_feishu_token_secret(token,secret,title='',content='',msgtype='markdown'):
    try:
        dic = check_config()
        accesstoken_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/'
        timestamp = int(round(time.time() * 1000))

    except Exception as e:
        traceback.print_exc()
        print(e)
