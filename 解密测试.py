

# 接收命令行参数中的文件名
fname = "F:\\网易云缓存\\Cache\\414586031-128-364d0bf9bbc8184b44cc218c69e11757.uc"

# 打印文件名
print(fname)

# 以二进制读取模式打开文件
with open(fname, "rb") as f:
    # 读取文件内容
    c = f.read()

# 将读取的内容转换为字节数组
arr = bytearray(c)

# 对字节数组中的每个元素进行异或操作，异或的值是163
for i in range(len(arr)):
    arr[i] ^= 163

# 将处理后的字节数组写入新的文件，文件名在原文件名后添加".mp3"
with open(fname + ".mp3", "wb") as f:
    f.write(bytes(arr))

# 打印完成信息
print('ok')