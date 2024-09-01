#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import binascii
import json
import random
import string
from urllib import parse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import requests

# 从a-z,A-Z,0-9中随机获取16位字符
def get_random():
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return random_str

# AES加密要求加密的文本长度必须是16的倍数
def len_change(text):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    return text.encode("utf-8")

# 使用cryptography库实现AES加密
def aes_encrypt(plaintext, key):
    iv = b'0102030405060708'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = len_change(plaintext)
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode()

# js中的 b 函数，调用两次 AES 加密
def b(text, str):
    first_data = aes_encrypt(text, '0CoJUm6Qyw8W8jud'.encode())
    second_data = aes_encrypt(first_data, str.encode())
    return second_data

# 这就是那个巨坑的 c 函数
def c(text):
    e = '010001'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    text = text[::-1]
    result = pow(int(binascii.hexlify(text.encode()), 16), int(e, 16), int(f, 16))
    return format(result, 'x').zfill(131)

# 获取最终的参数 params 和 encSecKey 的方法
def get_final_param(text, str):
    params = b(text, str)
    encSecKey = c(str)
    return {'params': params, 'encSecKey': encSecKey}

# 通过参数获取搜索歌曲的列表
def get_music_list(params, encSecKey):
    url = "https://music.163.com/weapi/cloudsearch/get/web"
    payload = f'params={parse.quote(params)}&encSecKey={parse.quote(encSecKey)}'
    headers = {
        'authority': 'music.163.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://music.163.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://music.163.com/search',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.text

# 通过歌曲的id获取播放链接
def get_reply(params, encSecKey):
    url = "https://music.163.com/weapi/song/enhance/player/url/v1"
    payload = f'params={parse.quote(params)}&encSecKey={parse.quote(encSecKey)}'
    headers = {
        # 同上，省略重复的headers定义
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.text

if __name__ == '__main__':
    song_name = input('请输入歌曲名称，按回车键搜索：')
    d = {
        "hlpretag": "<span class=\"s-fc7\">",
        "hlposttag": "</span>",
        "s": song_name,
        "type": "1",
        "offset": "0",
        "total": "true",
        "limit": "30",
        "csrf_token": ""
    }
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])

    print('搜索结果如下：')
    if song_list:
        song_list = json.loads(song_list)['result']['songs']
        for i, item in enumerate(song_list):
            item = json.dumps(item)
            print(f"{i}: {json.loads(item)['name']}")
            d = {
                "ids": f"[{json.loads(item)['id']}]",
                "level": "standard",
                "encodeType": "",
                "csrf_token": ""
            }
            d = json.dumps(d)
            param = get_final_param(d, random_param)
            song_info = get_reply(param['params'], param['encSecKey'])
            if song_info:
                song_url = json.loads(song_info)['data'][0]['url']
                print(song_url)
            else:
                print("该首歌曲解析失败，可能是因为歌曲格式问题")
    else:
        print("很抱歉，未能搜索到相关歌曲信息")