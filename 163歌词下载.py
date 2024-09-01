import json, os, re, requests, mutagen.id3, sys
from datetime import datetime
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, APIC
from mutagen.mp4 import MP4, MP4Cover
def isFlac(path):
    """
    判断是否为FLAC文件
    :param path: 媒体文件路径
    :return: 返回布尔值
    """
    with open(path,"rb") as f:
        if f.read(4).startswith(b"fLaC"):
            return True
        else:
            return False
def isM4a(path):
    """
    判断是否为M4A文件类型
    :param path:媒体文件路径 
    :return: 返回bool
    """
    with open(path, 'rb') as file:
        # 读取文件的前20个字节
        header = file.read(20)

    # 检查是否包含'ftyp'或'M4A '的模式
    # 使用bytes的find方法来搜索字节序列
    ftyp_pos = header.find(b'ftyp')
    m4a_pos = header.find(b'M4A ')

    # 如果找到'ftyp'或'M4A '则认为是M4A文件
    return ftyp_pos != -1 or m4a_pos != -1

def getSongName(path):
    if isFlac(path):
        au1=FLAC(path)
        name=au1["title"][0]
        ac=au1["artist"]
    elif isM4a(path):
        au1=MP4(path)
        name=au1["\xa9nam"]
        ac=au1["\xa9ART"]
    else:
        au1=MP3(path)
        name=au1["TIT2"]
        ac=au1["TPE1"]
    return f"{name} {ac[0]}"
def setSongLRC(path):
    name=getSongName(path)
    try:
        result=json.loads(requests.get(url=SCapi.replace("{name}",name)).text)["result"]["songs"]
    except:
        result=""
    if result!="":
        i=1
        for item in result:
            print(f"""{i}. 歌曲ID {item['id']},歌名 {item['name']},主要艺术家 {item['artists'][0]['name']}""")
            i+=1
        #finid=str(result[int(input("请输入最适合的对象序号:\n"))-1]['id'])
        finid=str(result[0]['id'])
        try:
            LRCresult=json.loads(requests.get(url=LRCapi.replace("{songid}",finid)).text)['lyric']
        except Exception as e:
            LRCresult=""
        filepath,filename=os.path.split(path)
        songname,fileendname=os.path.splitext(filename)
        with open(f"{filepath}\\{songname}.lrc",mode="w",encoding="utf-8") as f:
            if LRCresult !="":
                f.write(LRCresult)
                print(f"[LRC]歌词已下载:{filepath}\\{songname}.lrc")
            else:
                print(f"[LRC]此歌曲无歌词!:{name}")
    else:
        print(f"[LRC]此歌曲无歌词或搜不到!:{name}")
    
# --------------------------------------主进程------------------------------------------
# ---常量---
SCapi="https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={name}&type=1&offset=0&total=true&limit=10"
LRCapi="https://music.163.com/api/song/media?id={songid}"
versionCall="""=========================>网易云歌曲补充1.1<=========================
bilibili:杂牌土豆粉,QQ:2540709491,开源仓库:https://github.com/2540709491/163UCtoFLAC,软件QQ交流群:590074502
BILIBILI主页:https://space.bilibili.com/487041556
作者声明:开源软件,禁止倒卖,仅供学习交流,请在下载后的120年内删除.
功能:1.单文件解密,直接打开本EXE文件,2.多文件解密,多个uc缓存拖入软件打开
"""
# ---常量结束---
# songpath=input("请输入歌曲路径:\n").strip('"')
# songpath="H:\\网易云音乐下载\\VipSongsDownload\\黑猫大少爷 - 与众不同.flac"
argv=sys.argv[1:]
if len(argv) > 0:
    for song_path in argv:
        setSongLRC(song_path)
    print("所有任务均已完成!")
    print(versionCall)
    os.system("pause")

else:
    print(versionCall)
    path = (input("请输入歌曲路径:\n").strip('"'))
    setSongLRC(path)
    os.system("pause")


