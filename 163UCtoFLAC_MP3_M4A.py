import json, os, re, requests, mutagen.id3, sys
from datetime import datetime
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, APIC
from mutagen.mp4 import MP4, MP4Cover

# 获取ID
def getSongIdByStr(filename):
    """
    通过文件名获取SongID
    :param filename:文件名,"xxxx.uc 
    :return: 返回网易云歌曲ID
    """
    match = re.search(r'\d+', filename)
    if match:
        return match.group(0)
    else:
        return ""
def getSongInfo(path):
    """
    获取歌曲信息,返回SongInfo
    :param path:媒体文件路径 
    :return: 返回字典{"title":标题,"description":介绍,"image":图片二进制数据,"date":年份,"ac":作者}
    """
    print("开始获取歌曲信息")
    url = f"https://music.163.com/song?id={getSongIdByStr(path)}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"获取详细信息失败(item)! {response.status_code}")
        return 
    # 设置歌曲信息
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
    if match:
        json_content = match.group(1)  # 这是匹配到的JSON字符串
        print(f"歌曲原始信息{json_content}")
        try:
            data = json.loads(json_content)
            # 读取歌曲信息
            title = data.get("title")
            description = data.get("description")
            image = requests.get(f"{data.get("images")[0]}?param=256y256").content
            date = data.get('pubDate')
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').year
            ac = re.search(r'由 (.*?) 演唱', description).group(1)
            return {"title":title,"description":description,"image":image,"date":date,"ac":ac}
            
        except Exception as e:
            print(f"写入歌曲信息失败(item)!{e}")
            title = None
            description = None
            image = None
            date = None
            ac = None
            return {"title":title,"description":description,"image":image,"date":date,"ac":ac}


        
    else:
        print("ERROR!没有发现歌曲信息")
        title = None
        description = None
        image = None
        date = None
        ac = None
        return {"title":title,"description":description,"image":image,"date":date,"ac":ac}
def changeCover(img, au):
    """
    更改FLAC封面
    :param img:传入图片数据二进制
    :param au: FLAC格式数据,audio
    :return: 返回FLAC格式数据,audio
    """
    # 更改歌曲封面
    p = Picture()
    p.data = img
    p.type = mutagen.id3.PictureType.COVER_FRONT
    p.mime = u"jpg"
    p.width = 130
    p.height = 130
    p.depth = 32
    # 构造PICTURE块并添加到元数据中
    au.add_picture(p)
    return au
def decry(path,songInfo):
    """
    解密网易云音乐媒体文件
    :param path:媒体文件路径 
    :param songInfo: 参上getSongInfo
    :return: 返回解密后文件路径,自动命名
    """
    # 解密uc文件
    with open(path, "rb") as f:
        # 读取文件内容
        c = f.read()
    # 将读取的内容转换为字节数组
    arr = bytearray(c)
    # 对字节数组中的每个元素进行异或操作，异或的值是163
    for i in range(len(arr)):
        arr[i] ^= 163
    filename=f"{os.path.dirname(path)}\\{re.sub(r'[<>:"/\\|?*]', '', songInfo["title"])}_{re.sub(r'[<>:"/\\|?*]', '', songInfo["ac"])}"
    #判断格式是FLAC还是mp3
    if arr[:4] == b"fLaC":
        # 将处理后的字节数组写入新的文件，文件名在原文件名后添加".flac"
        with open(f"{filename}.flac", "wb") as f:
            f.write(bytes(arr))
            return f"{filename}.flac"
    elif arr[:20].find(b'ftyp') !=-1  or arr[:20].find(b'M4A') !=-1:
        # 将处理后的字节数组写入新的文件，文件名在原文件名后添加".m4a"
        with open(f"{filename}.m4a", "wb") as f:
            f.write(bytes(arr))
            return f"{filename}.m4a"
    else:
        # 将处理后的字节数组写入新的文件，文件名在原文件名后添加".mp3"
        with open(f"{filename}.mp3", "wb") as f:
            f.write(bytes(arr))
            return f"{filename}.mp3"
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
def setSongInfoFLAC(path,songInfo):
    """
    设置FLAC文件信息
    :param path: 媒体文件路径
    :param songInfo: 参上getSongInfo
    :return: 无返回
    """
    audio = FLAC(path)
    # 设置歌曲信息
    audio["artist"] = songInfo["ac"]
    audio["title"] = songInfo["title"]
    audio["date"] = str(songInfo["date"])
    audio['album'] = songInfo["title"]
    audio.pprint()
    print(audio.tags)
    audio = changeCover(songInfo["image"], audio)
    # 保存文件
    audio.save()
    print(f"[FLAC]封面和元数据信息已添加到 {path}")
def setSongInfoMP3(path, songInfo):
    """
    设置MP3文件信息
    :param path: 媒体文件路径
    :param songInfo: 参上getSongInfo
    :return: 无返回
    """
    # 打开MP3文件
    audio = MP3(path, ID3=ID3)
    # 设置歌曲信息
    audio.tags.add(ID3)
    audio.tags["TIT2"] = TIT2(encoding=3, text=songInfo["title"])  # 标题
    audio.tags["TPE1"] = TPE1(encoding=3, text=songInfo["ac"])    # 艺术家
    audio.tags["TALB"] = TALB(encoding=3, text=songInfo.get("album", ""))  # 专辑
    audio.tags["TYER"] = TYER(encoding=3, text=str(songInfo["date"]))  # 年份
    audio.tags["APIC"] = APIC(encoding=3, mime=u"image/jpeg", type=3, desc=u"Cover", data=songInfo["image"])  # 封面

    # 保存文件
    audio.save()
    print(f"[MP3] 元数据信息已添加到 {path}")
def addCoverForM4A(filename, cover):
    """
    为M4A文件添加封面
    :param filename:媒体文件路径 
    :param cover: 二进制封面数据
    :return: 无返回
    """
    audio = MP4(filename)
    data = cover
    covr = []
    if data.startswith(b'\x89PNG'):
        covr.append(MP4Cover(data, MP4Cover.FORMAT_PNG))
    else:
        covr.append(MP4Cover(data, MP4Cover.FORMAT_JPEG))
    audio['covr'] = covr
    audio.save()
def setSongInfoM4A(path, songInfo):
    """
    设置M4A文件信息
    :param path: 媒体文件路径
    :param songInfo: 参上getSongInfo
    :return: 无返回
    """
    # 打开M4A文件
    audio = MP4(path)
    # 检查是否已经有APIC帧，如果有则删除
    for key in audio.keys():
        if key.startswith("covr") or key == 'APIC':
            del audio[key]
    # 设置歌曲信息
    audio["\xa9nam"] = songInfo["title"]
    audio["\xa9ART"] = songInfo["ac"]
    audio["\xa9alb"] = songInfo.get("album", "")
    audio["\xa9day"] = str(songInfo["date"])
    audio.pprint()
    audio.save()  # 保存时指定ID3版本
    
    # 添加封面
    addCoverForM4A(path,songInfo["image"])

    
    # 保存文件
    
    print(f"[M4A] 元数据信息已添加到 {path}")
def smartSetSongInfo(path,songInfo):
    """
    判断文件类型选用合适方法设置文件信息
    :param path: 文件路径
    :param songInfo: 参上getSongInfo
    :return:无返回 
    """
    print("解密uc文件中......")
    path = decry(path,songInfo)
    if isFlac(path):
        setSongInfoFLAC(path,songInfo)
    elif isM4a(path):
        setSongInfoM4A(path,songInfo)
    else:
        setSongInfoMP3(path,songInfo)
# --------------------------------------主进程------------------------------------------
# ---常量---
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=0, i",
    "referer": "https://music.163.com/",
    "sec-ch-ua": "^\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\"Windows^\"",
    "sec-fetch-dest": "iframe",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
}
# ---常量结束---
argv=sys.argv[1:]
if len(argv) > 0:
    for item in argv:
        smartSetSongInfo(item,getSongInfo(item))
    print("所有任务均已完成!")
    print("""===================================>网易云音乐缓存解密V2.1<===================================
作者信息:①UC文件解密:在吾爱论坛和B站上都看过,个人推测B站,链接:https://www.bilibili.com/video/BV19g4y1y78b
②还原音乐元数据信息,批量解密:
bilibili:杂牌土豆粉,QQ:2540709491,开源仓库:https://github.com/2540709491/163UCtoFLAC,软件QQ交流群:590074502
BILIBILI主页:https://space.bilibili.com/487041556
③项目引用库:json,os,re,requests,mutagen
作者声明:开源软件,禁止倒卖,仅供学习交流,请在下载后的120年内删除.
功能:1.单文件解密,直接打开本EXE文件,2.多文件解密,多个uc缓存拖入软件打开
""")
    os.system("pause")
else:
    print("""===================================>网易云音乐缓存解密V2.1<===================================
作者信息:①UC文件解密:在吾爱论坛和B站上都看过,个人推测B站,链接:https://www.bilibili.com/video/BV19g4y1y78b
②还原音乐元数据信息,批量解密:
bilibili:杂牌土豆粉,QQ:2540709491,开源仓库:https://github.com/2540709491/163UCtoFLAC,软件QQ交流群:590074502
BILIBILI主页:https://space.bilibili.com/487041556
③项目引用库:json,os,re,requests,mutagen
作者声明:开源软件,禁止倒卖,仅供学习交流,请在下载后的120年内删除.
功能:1.单文件解密,直接打开本EXE文件,2.多文件解密,多个uc缓存拖入软件打开
""")
    flac_path = (input("请输入uc缓存文件路径:\n").strip('"'))
    smartSetSongInfo(flac_path,getSongInfo(flac_path))
    os.system("pause")
