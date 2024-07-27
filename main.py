# coding=UTF-8-BOM
import json
import doc_file as doc
import threading
import requests as rq
from requests import RequestException
import datetime
import time
import re
import configparser
import os
import process_file as pf

print("hello? World!")
print("Copyright 2024 © Mike. All Rights Reserved.")

def dev_time_limit(time_limit): # 开发版本时间限制
    if int(time.time()) - time_limit > 0:
        print("超出开发版本使用时间：",time.ctime())
        time.sleep(2)
        quit()
    else:
        print("正在使用开发版本，距离到期还剩",datetime.timedelta(seconds=float(time_limit - int(time.time()))))
        time.sleep(2)

#dev_time_limit(1721923200) # 开发版限时，发布记得注释掉

# 设置机器人信息
# 没有配置文件则创建
if os.path.exists("config.ini") == False:
    with open("config.ini","x",encoding="UTF-8") as f:
        f.write(doc.default_config)
    print("配置文件已创建，请修改后重启程序！"); time.sleep(2); quit()
# 从配置文件读取
config = configparser.ConfigParser() # 定义读取对象
config.read("config.ini", encoding="UTF-8") # 读取配置文件
config_sections = config.sections() # 获取文件分区
if "basic" in config_sections == False: print("不完整配置文件，请删除然后让程序重新创建。"); time.sleep(2); quit()
config_basic_items = config.items("basic") # 读取分区内容
config_basic_items = dict(config_basic_items) # 转为dict
if \
"channel_id" in config_basic_items == False or \
"guild_id" in config_basic_items == False or \
"bot_token" in config_basic_items == False or \
"message_id" in config_basic_items == False:
    print("不完整配置文件，请删除然后让程序重新创建。"); time.sleep(2); quit()

bot_token = config_basic_items["bot_token"]
guild_id = config_basic_items["guild_id"] # 服务器ID
channel_id = config_basic_items["channel_id"] # 频道ID
api_url = "https://a1.fanbook.cn"
message_id = config_basic_items["message_id"] # 读取为0自动使用最近消息
channel_list = {} # 无需填写，首次请求会设置
exit_program = False

# 获取机器人信息
try:
    response = rq.post(api_url + f"/api/bot/{bot_token}/getMe")
except RequestException as e:
    print("发生错误：",e.errno,e.args)
    quit(1)

# 定义JSON变量：data
# 并装载机器人信息
data = json.loads(response.text)

# 确认API是好的
if data["ok"] != True:
    print("API异常：",data)

# 展示机器人信息
print("机器人id：",data["result"]["id"],sep="")
print("机器人名字：",data["result"]["first_name"],sep="")
print("机器人主人ID：",data["result"]["owner_id"],sep="")

# 开始启动处理
print("处理系统正在启动...")
headers = {"Content-Type":"application/x-www-form-urlencoded"}
headers_json = {"Content-Type":"application/json"}

# 长ID搜寻频道用户
def user_lookup(user_long_id):
    global headers_json
    global guild_id
    if user_long_id == "": return("Empty_user_id")
    temp_json = {} #dict
    temp_json["chat_id"] = int(channel_id)
    temp_json["guild_id"] = int(guild_id)
    temp_json["user_id"] = int(user_long_id)
    response = rq.post(api_url + f"/api/bot/{bot_token}/getChatMember",headers=headers_json,data=json.dumps(temp_json))
    resp_json = json.loads(response.text)
    if resp_json["ok"] == False: print("请求用户名称失败，返回信息：",response.text); return("Lookup_failed")
    return(str(resp_json["result"]["user"]["first_name"]) + "(" + str(str(resp_json["result"]["user"]["username"]) + ")"))

# 短ID搜寻服务器用户
def user_lookup_short(user_short_id):
    global headers_json
    global guild_id
    if user_short_id == "": return("Empty_user_id")
    temp_json = {} #dict
    temp_json["guild_id"] = int(guild_id)
    temp_json["username"] = [str(user_short_id)]
    response = rq.post(api_url + f"/api/bot/{bot_token}/searchGuildMemberByName",headers=headers_json,data=json.dumps(temp_json))
    resp_json = json.loads(response.text)
    if resp_json["ok"] == False: print("请求用户名称失败，返回信息：",response.text); return("Lookup_failed")
    return(str(resp_json["result"][0]["user"]["first_name"]) + "(" + str(str(resp_json["result"][0]["user"]["username"]) + ")"))

# 长ID搜寻频道
def channel_lookup(channel_id:str, use_cache=True):
    global headers_json
    global guild_id
    global channel_list
    return_if_fail = False
    if use_cache == False or channel_list == {}: # 若要求不使用缓存或频道列表无缓存，则更新
        time.sleep(1) # 请求有频率限制，做个延迟
        temp_json = {} #dict
        temp_json["guild_id"] = str(guild_id)
        response = rq.post(api_url + f"/api/bot/{bot_token}/channel/list",headers=headers_json,data=json.dumps(temp_json))
        resp_json = json.loads(response.text)
        if resp_json["ok"] == False: print("请求频道列表失败，返回信息：",response.text); return("Lookup_failed")
        channel_list = resp_json
        return_if_fail = True
        if channel_id == "": return("Empty_channel_id")
   # 遍历列表搜寻频道对应 
    for i in range(len(channel_list["result"])):
        if channel_list["result"][i]["channel_id"] == channel_id:
            return(channel_list["result"][i]["name"])
    if return_if_fail != True:
        print("Lookup_NotFound with cache, updating cache.")
        return(channel_lookup(channel_id, False)) # 找不到自动重试无缓存查询
    return("Lookup_NotFound")

# 提及(@)的替换 调用全局mtext[text]
def mention_replace():
    global mtext
    msg_text = str(mtext["text"])
    result = re.findall(r"\$\{@![0-9]+}",msg_text)
    for i in range(len(result)):
        user_id = str(re.findall(r"[0-9]+",result[i])[0])
        user_id_lookup = user_lookup(user_id)
        mtext["text"] = msg_text.replace("${@!" + user_id + "}", "@" + user_id_lookup)

# 频道(#)的替换 调用全局mtext[text]
def channel_replace():
    global mtext
    msg_text = str(mtext["text"])
    result = re.findall(r"\$\{#[0-9]+}",msg_text)
    for i in range(len(result)):
        channel_id = str(re.findall(r"[0-9]+",result[i])[0])
        channel_id_lookup = channel_lookup(channel_id)
        mtext["text"] = msg_text.replace("${#" + channel_id + "}", "#" + channel_id_lookup)

# 定义循环内需要的变量
message_len = 0

# 输入接收函数定义
def InputThread():
    # 引入全局变量
    global doc
    global headers_json
    global channel_id
    global headers
    global exit_program
    # 接收死循环
    chat_mode = False
    while True:
        temp_json = {} # dict
        text_input = input() # 等待输入
        command_end = text_input.find(" ")
        if command_end == -1: command_end = len(text_input)
        command_part = text_input[:command_end]
        # 判定聊天模式
        if chat_mode == True:
            if text_input == "!exit":
                print("退出聊天模式")
                chat_mode = False
                continue
            temp_json["chat_id"] = int(channel_id)
            temp_json["text"] = text_input
            temp_json["desc"] = text_input
            response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp_json))
            if json.loads(response.text)["ok"] == False: print("请求失败，返回信息：",response.text)
            continue
        # 判定命令
        if command_part == "help":
            print(doc.help_text)
        elif command_part == "say": # 发送消息命令
            temp_json["chat_id"] = int(channel_id)
            temp_json["text"] = text_input[command_end + 1:]
            temp_json["desc"] = text_input[command_end + 1:]
            response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp_json))
            if json.loads(response.text)["ok"] == False: print("请求失败，返回信息：",response.text)
        elif command_part == "ulup": # 长ID查用户命令
            print("ulup: 搜寻结果 ",user_lookup(text_input[command_end + 1:]))
        elif command_part == "uslup": # 短ID查用户命令
            print("uslup: 搜寻结果 ",user_lookup_short(text_input[command_end + 1:]))
        elif command_part == "chlup": # 长ID查频道命令
            print("chlup: 搜寻结果 ",channel_lookup(text_input[command_end + 1:]))
        elif command_part == "cmode": # 进入聊天模式命令
            print("已进入聊天模式，输入!exit回到终端模式")
            chat_mode = True
        elif command_part == "114514": # 恶臭命令（整活）
            print("本程序正在恶臭：",doc.t114514)
        elif command_part == "exit": # 退出程序命令
            exit_program = True
            quit()
        else:
            print("未知命令！请使用help查看命令列表。")
# 输入接收线程定义
input_thread = threading.Thread(target=InputThread)
input_thread.daemon = True
# 输入接收线程启动
input_thread.start()

# 死循环
while True:
        
    if message_id == "0":
        response = rq.post(api_url + f"/api/bot/{bot_token}/message/getList",headers=headers,data=f"channel_id={channel_id}")
    else:
        response = rq.post(api_url + f"/api/bot/{bot_token}/message/getList",headers=headers,data=f"channel_id={channel_id}&message_id={message_id}&behavior=after")
    # 装载消息数据
    data = json.loads(response.text)
    message_len = len(data["data"])
    #print(data) #调试用
    # 开始for循环
    for i in range(message_len):
        # 装载消息内容
        mtext = json.loads(data["data"][message_len - i - 1]["content"])
        nickname = str(data["data"][message_len - i - 1]["author"]["nickname"])
        username = str(data["data"][message_len - i - 1]["author"]["username"])
        pf.global_message(data["data"]) # 交给process_file.py处理
        #print(mtext) #调试用
        # 判断消息类型，给予不同输出
        if mtext["type"] == "newJoin": # 新成员通知
            if "code" in mtext:
                print("[新成员 序号:",str(mtext["order"]).rjust(5,"0"),"]邀请码：",mtext["code"].center(10),"|",nickname,f"(#{username})")
            else:
                print("[新成员 序号: ----- ]未使用邀请码","".center(6),"|",nickname,f"(#{username})")
        elif mtext["type"] == "text": # 文本消息
            original_text = mtext["text"]
            mention_replace()
            channel_replace()
            print(f"(#{username})",nickname,"说",mtext["text"])
            pf.text_message(message_id,username,nickname,original_text,mtext["text"]) # 交给process_file.py处理
        elif mtext["type"] == "image": # 图片消息
            print(f"(#{username})",nickname,"发送图片",mtext["url"])
            pf.pic_message(message_id,username,nickname,mtext["url"]) # 交给process_file.py处理
        elif mtext["type"] == "voice": # 语音消息
            print(f"(#{username})",nickname,"发送语音",mtext["second"],"秒",mtext["url"])
            pf.voi_message(message_id,username,nickname,mtext["url"],int(mtext["second"])) # 交给process_file.py处理
        elif mtext["type"] == "114514": # 恶臭消息（整活）
            print(f"(#{username})",nickname,"说",mtext["text"])
        else: # 不在列的消息类型直接输出
            print(f"(#{username})",nickname,f"消息类型未识别：",mtext)
        message_id = data["data"][message_len - i - 1]["message_id"]
    # 如果本次循环有内容，就输出一下最新消息ID
    #if message_len != 0: print(f"本次输出结束ID：{message_id}".rjust(100))
    config.set("basic","message_id",message_id)    
    with open('config.ini', 'w',encoding="UTF-8") as f:
        config.write(f)
    # 循环完毕等待2秒开始下次循环
    if exit_program == True: quit()    
    time.sleep(2)
