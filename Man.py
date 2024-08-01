import json
from datetime import datetime
import mutagen.id3
from mutagen.flac import FLAC,Picture
import re
import requests
flac_path = (input("请输入uc缓存文件路径:"))
#获取ID
match=re.search(r'\d+',flac_path)
song_id="";
if match:
    song_id=match.group(0)
#访问歌曲内容
url=f"https://music.163.com/song?id={song_id}"

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
response = requests.get(url, headers=headers)
html_content=""
#获取歌曲信息
if response.status_code == 200:
    # 请求成功，打印页面内容
    html_content=response.text
else:
    print(f"Failed to retrieve content, status code: {response.status_code}")
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
print(response.text)

if match:
    json_content = match.group(1)  # 这是匹配到的JSON字符串
    print(json_content)
    data=json.loads(json_content)

    title=data.get("title")
    descripton=data.get("description")
    image=requests.get(data.get("images")[0]).content
    date=data.get('pubDate')
    date=datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').year
    ac=re.search(r'由 (.*?) 演唱', descripton).group(1)
else:
    print("No JSON content found in the script tag.")
#解密uc文件
with open(flac_path, "rb") as f:
    # 读取文件内容
    c = f.read()

# 将读取的内容转换为字节数组
arr = bytearray(c)

# 对字节数组中的每个元素进行异或操作，异或的值是163
for i in range(len(arr)):
    arr[i] ^= 163

# 将处理后的字节数组写入新的文件，文件名在原文件名后添加".mp3"
with open(f"{title}_{ac}.flac", "wb") as f:
    f.write(bytes(arr))
    flac_path = f"{title}_{ac}.flac"

# 打印完成信息
print('ok')

audio = FLAC(flac_path)
audio["artist"]=ac
audio["title"]=title
audio["date"]=str(date)
audio['album']=title
audio.pprint()
print(audio.tags)
#更改歌曲封面
p=Picture()
p.data=image
p.type=mutagen.id3.PictureType.COVER_FRONT
p.mime=u"jpg"
p.width=130
p.height=130
p.depth=32
# 构造PICTURE块并添加到元数据中
audio.add_picture(p)
# 保存文件
audio.save()

print(f"封面和虚构的元数据信息已添加到 {flac_path}")

