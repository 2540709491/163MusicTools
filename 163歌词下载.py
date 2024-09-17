import json, os,  requests,sys
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import USLT
from mutagen.mp4 import MP4
import langid
import pycountry
is_downLrcToFile=False#是否将歌词下载到本地

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
def lau2_to_lau3(name):
    #把lang_id获取到的2位国家简称转为3位国家简称
    # 获取所有语言的列表
    languages = pycountry.languages
    # 根据两个字母的代码找到对应的语言对象
    try:
        return languages.lookup(name).alpha_3
    except:
        #如果获取不到则默认英语
        return "eng"


def getSongName(path):
    '''
    获取歌曲名称
    :param path:输入歌曲路径 
    :return: 无
    '''
    #判断歌曲类型并读取歌曲名,作者名
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
    if name=="":
        #如果没有ID3信息,则选择文件名作为歌曲名
        name=os.path.splitext(os.path.basename(path))[0]
    return f"{name} {ac[0]}"
def setSongLRC_IN(path,lyrics):
    """
    设置歌曲内嵌字幕
    :param path:输入歌曲路径 
    :param lyrics: 输入歌词
    :return: 无
    """
    #判断歌曲类型并添加歌词信息
    if isFlac(path):
        audio=FLAC(path)
        audio['Lyrics']=lyrics
        audio.pprint()
        audio.save()
        print(f"[LRC][FLAC]歌词已内嵌:{path}")
    elif isM4a(path):
        audio=MP4(path)
        audio["\xa9lyr"]=lyrics
        audio.pprint()
        audio.save()
        print(f"[LRC][M4A]歌词已内嵌:{path}")
    else:
        audio=MP3(path)
        language=lau2_to_lau3(langid.classify(lyrics)[0])
        audio['USLT']=USLT(encodings=3,lang=language,desc="Lyrics",text=lyrics)
        audio.pprint()
        audio.save()
        print(f"[LRC][MP3]歌词已内嵌:{path}")
    pass
def setSongLRC(path):
    """
    设置歌曲歌词
    :param path:输入歌曲本地路径 
    :return: 无
    """
    name=getSongName(path)
    try:
        #搜索歌曲信息
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
            #找出相关度最高的,获取歌词
            LRCresult=json.loads(requests.get(url=LRCapi.replace("{songid}",finid)).text)['lyric']
        except Exception as e:
            LRCresult=""
        filepath,filename=os.path.split(path)
        songname,fileendname=os.path.splitext(filename)
        with open(f"{filepath}\\{songname}.lrc",mode="w",encoding="utf-8") as f:
            #默认内嵌字幕
            setSongLRC_IN(path,LRCresult)
            if LRCresult != "":
                #判断获取的字幕内容是否为空
                if is_downLrcToFile:
                    #如果用户一开始选择了下载歌词到本地,则创建同名歌词文件
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
versionCall="""=========================>歌曲歌词补充1.5<=========================
bilibili:杂牌土豆粉,QQ:2540709491,开源仓库:https://github.com/2540709491/163UCtoFLAC,软件QQ交流群:590074502
BILIBILI主页:https://space.bilibili.com/487041556
作者声明:开源软件,禁止倒卖,仅供学习交流,请在下载后的120年内删除.
功能:1.单文件补充歌词,打开exe文件2.多文件补充歌词,多个歌曲文件拖入软件打开
"""
# ---常量结束---

argv=sys.argv[1:]
if(input("是否将歌词下载到本地(否则将歌词内嵌到歌曲文件中,是则在内嵌歌词的基础上保存一份同名歌词文件)\n请输入,不输入则为否(Y/n):\n")) == 'Y':
    is_downLrcToFile=True
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


