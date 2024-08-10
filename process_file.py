# coding=UTF-8
import json, time
import os
from pyexpat import model
import requests as rq
from promplate.llm.openai import ChatComplete # 引入GPT
import csv
import ini_db

# 打开GPT数据库


# 填写GPT基本信息
base_url = os.getenv("openai-base-url")
api_key = os.getenv("openai-api-key")
if api_key == None:
    print("[WARN]无法从环境变量 openai-api-key 中读取到 key，将无法使用 AI 功能。")
    ai_function = False
else:
    ai_function = True
    if base_url == None:
        print("[WARN]无法从环境变量 openai-base-url 中读取到 base_url，将直接连接 OpenAI 。")
        complete = ChatComplete(api_key=api_key).bind(model="gpt-4o-mini",max_tokens=250) # 这一行启用是直连OpenAI
    else:
        print("[INFO]成功从环境变量 openai-base-url 中读取到 base_url，当前站点为：",base_url)
        complete = ChatComplete(base_url=base_url,api_key=api_key).bind(model="gpt-4o-mini",max_tokens=250) # 这一行用转发服务器
    # 初始化GPT
print("[INFO]您可将将敏感词以 UTF-8 编码以空格分割写入与程序同目录的 mingan.txt ，无需重启程序，即时生效。\n[INFO] p.s. 此词库仅限于问AI功能。")
with open("mingan.txt","a") as f:
    pass
# 此模块用于处理消息事件
# 收到消息将会从主程序调用
# 模块中的函数处理会阻塞主线程，请勿等待！

# 全局消息额外处理函数
def global_message(original_data:dict):
    # 所有消息都会触发此函数调用
    # original_data 调用返回的消息json中的["data"]转成的dict
    # 详细请参见 https://open.fanbook.mobi/document/manage/doc/#%E9%A2%91%E9%81%93%E6%B6%88%E6%81%AF%E5%88%97%E8%A1%A8
    pass

# 文本消息额外处理函数
def text_message(message_id:str,message_sender_id:str,message_sender_nick:str,message_text_ori:str,message_text_format:str,bot_id,channel_id,api_url,bot_token,headers_json,guild_id):
    #return()
    # message_id 消息唯一长ID
    # message_sender_id 发送者唯一短ID
    # message_sender_nick 发送者外显名
    # message_text_ori 消息原文，@和#未转义
    # message_text_format 转义@和#后的消息
    if message_text_ori.find("${@!"+str(bot_id)+"}") != -1 and ai_function is True:
        # 判断用户是否封了
        if(ini_db.read_black(int(message_sender_id))): return None # 封了就直接返回
        # 许可协议部分
        if message_text_ori == "${@!"+str(bot_id)+"}" + "我同意相关协议" or message_text_ori == "${@!"+str(bot_id)+"}" + " 我同意相关协议":
            ini_db.set_agree(int(message_sender_id),True)
            temp0_json = {} # dict
            temp0_json["chat_id"] = int(channel_id)
            temp0_json["text"] = "已同意协议\n功能已解锁，输出有限长，请不要让模型输出长篇内容。"
            temp0_json["desc"] = "已同意协议"
            response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp0_json))
            return
        # 没同意就返回
        if ini_db.read_agree(int(message_sender_id)) != True:
            temp0_json = {} # dict
            temp0_json["chat_id"] = int(channel_id)
            temp0_json["text"] = "{\"type\":\"richText\",\"title\":\"您的AI功能未启用\",\"document\":\"[{\\\"insert\\\":\\\"您需要阅读并同意以下协议才可使用\\\\n点击阅读协议\\\\n\\\"}]\",\"v2\":\"[{\\\"insert\\\":\\\"您需要阅读并同意以下协议才可使用\\\\n\\\"},{\\\"insert\\\":\\\"点击阅读协议\\\",\\\"attributes\\\":{\\\"link\\\":\\\"https://cn.bing.com/\\\"}},{\\\"insert\\\":\\\"\\\\n\\\"}]\",\"v\":2}"
            temp0_json["desc"] = "拒绝使用"
            temp0_json["unreactive"] = 1 # 不准表态
            temp0_json["parse_mode"] = "Fanbook" # 富文本消息
            response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp0_json))
            return None

        # 判断用户余额够不够，够的话-1
        time_of_chance = ini_db.read_time(int(message_sender_id))
        if time_of_chance > 0:
            time_of_chance -= 1
            ini_db.set_time(int(message_sender_id),time_of_chance)
        else: # 余额不足
            temp0_json = {} # dict
            temp0_json["chat_id"] = int(channel_id)
            temp0_json["text"] = "余额不足"
            temp0_json["desc"] = "余额不足"
            response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp0_json))
            return None
        message_text_ori.replace("${@!"+str(bot_id)+"}","")
        print(message_text_ori)
        ini_db.db_save() # 保存一下数据库，防止程序崩了丢数据
        # 这里是一个敏感词库
        with open("mingan.txt","r",encoding="UTF-8") as f:
            mingan_words = f.read().lower() # 原文和判定全部转小写匹配
        mingan_list = mingan_words.split()
        for i in range(len(mingan_list)):
            if message_text_ori.lower().find(mingan_list[i]) != -1:
               print("[!紧急截断] 发现敏感词：",mingan_list[i]) 
               if not os.path.exists("block_log"):
                    os.makedirs("block_log")
               with open("block_log/" + time.strftime(f"%Y-%m-%d-%H%M%S-{message_sender_id}", time.localtime()) + ".txt","w",encoding="UTF-8") as f:
                    f.write("======截断时间======\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    f.write("\n======截断类型======\n发送敏感词")
                    f.write("\n======发送用户======\n" + message_sender_nick + f"({message_sender_id})")
                    f.write("\n======发送原文======\n" + message_text_ori)
                    f.write("\n======触发词汇======\n" + mingan_list[i])
               return()
        # 敏感词库结束
        try:    
            model_anwser = complete("注意：回答简介明了，不可使用Markdown格式，换行无需双写。以下是问题：\n"+message_text_ori)
        except Exception as e:
            print("[AI请求错误]",str(e))
            model_anwser = "请求错误：" + str(e)
        
        for i in range(len(mingan_list)): # 返回消息敏感词检测
            if model_anwser.lower().find(mingan_list[i]) != -1:
                print("[!紧急截断] 发现敏感词：",mingan_list[i]) 
                print(model_anwser)
                if not os.path.exists("block_log"):
                    os.makedirs("block_log")
                with open("block_log/" + time.strftime(f"%Y-%m-%d-%H%M%S-{message_sender_id}", time.localtime()) + ".txt","w",encoding="UTF-8") as f:
                    f.write("======截断时间======\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    f.write("\n======截断类型======\n返回敏感词")
                    f.write("\n======发送用户======\n" + message_sender_nick + f"({message_sender_id})")
                    f.write("\n======发送原文======\n" + message_text_ori)
                    f.write("\n======返回原文======\n" + model_anwser)
                    f.write("\n======触发词汇======\n" + mingan_list[i])
                model_anwser = "返回含有可疑词汇，不予展现。\n若滥用AI功能将会受到惩罚！"
                break
        
        temp_json1 = {} #dict
        temp_json1["guild_id"] = int(guild_id)
        temp_json1["username"] = [str(message_sender_id)]
        response = rq.post(api_url + f"/api/bot/{bot_token}/searchGuildMemberByName",headers=headers_json,data=json.dumps(temp_json1))
        resp_json = json.loads(response.text)
        with open("gpt_complete.log","a",encoding="UTF-8") as f: # GPT功能使用记录
            f.write("=====")
            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            f.write("=====\n用户" + message_sender_nick + "(" + message_sender_id + ")：\n")
            f.write(message_text_ori)
            f.write("\nGPT：\n")
            f.write(model_anwser)
            f.write("\n")
        if resp_json["ok"] == False: print("请求用户名称失败，返回信息：",response.text); return("Lookup_failed")
        message_sender_id = resp_json["result"][0]["user"]["id"]

        model_anwser = "${@!"+ str(message_sender_id) +"} 剩余余额：" + str(time_of_chance) + " 次\n" + model_anwser # 添加@
        
        time.sleep(1)
        temp_json = {} # dict
        temp_json["chat_id"] = int(channel_id)
        temp_json["text"] = model_anwser
        temp_json["desc"] = "AI智能回复"
        response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp_json))
        if json.loads(response.text)["ok"] == False: print("请求失败，返回信息：",response.text)
    pass

# 图片消息额外处理函数
def pic_message(message_id:str,message_sender_id:str,message_sender_nick:str,pic_url:str):
    # message_id 消息唯一长ID
    # message_sender_id 发送者唯一短ID
    # message_sender_nick 发送者外显名
    # pic_url 图片拉取地址
    pass

# 语音消息额外处理函数
def voi_message(message_id:str,message_sender_id:str,message_sender_nick:str,voi_url:str,voi_sec:int):
    # message_id 消息唯一长ID
    # message_sender_id 发送者唯一短ID
    # message_sender_nick 发送者外显名
    # voi_url 语音拉取地址
    # voi_sec 语音秒数
    pass