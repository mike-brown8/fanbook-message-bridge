# coding=UTF-8
import json, time
from pyexpat import model
import requests as rq
from promplate.llm.openai import ChatComplete # 引入GPT

# 初始化GPT
#complete = ChatComplete(base_url="",api_key="【这里填key!!!】").bind(model="gpt-4o-mini") # 这一行启用可以用转发服务器
complete = ChatComplete(api_key="【这里填key!!!】").bind(model="gpt-4o-mini") # 这一行启用是直连OpenAI

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
def text_message(message_id:str,message_sender_id:str,message_sender_nick:str,message_text_ori:str,message_text_format:str,bot_id,channel_id,api_url,bot_token,headers_json):
    #return()
    # message_id 消息唯一长ID
    # message_sender_id 发送者唯一短ID
    # message_sender_nick 发送者外显名
    # message_text_ori 消息原文，@和#未转义
    # message_text_format 转义@和#后的消息
    if message_text_ori.find("${@!"+str(bot_id)+"}") != -1:
        message_text_ori.replace("${@!"+str(bot_id)+"}","")
        temp0_json = {} # dict
        temp0_json["chat_id"] = int(channel_id)
        temp0_json["text"] = "收到请求 正在处理"
        temp0_json["desc"] = "收到请求 正在处理"
        response = rq.post(api_url + f"/api/bot/{bot_token}/sendMessage",headers=headers_json,data=json.dumps(temp0_json))
        if json.loads(response.text)["ok"] == False: print("请求失败，返回信息：",response.text)
        print(message_text_ori)
        # 这里是一个敏感词库
        mingan_words = """敏感词库(以下所有词汇一旦出现原文就会被紧急截断)
        1 2 3 4 5
        6 7 8 9 0
        """
        mingan_list = mingan_words.split()
        for i in range(len(mingan_list)):
            if message_text_ori.find(mingan_list[i]) != -1:
               print("[!紧急截断] 发现敏感词：",mingan_list[i]) 
               return()
        # 敏感词库结束
        try:    
            model_anwser = complete(message_text_ori)
        except Exception as e:
            print("[AI请求错误]",str(e))
            model_anwser = "请求错误：" + str(e)
        
        for i in range(len(mingan_list)): # 返回消息敏感词检测
            if message_text_ori.find(mingan_list[i]) != -1:
                print("[!紧急截断] 发现敏感词：",mingan_list[i]) 
                print(model_anwser)
                model_anwser = "返回含有可疑词汇，不予展现。"
            return()
        
        time.sleep(1)
        temp_json = {} # dict
        temp_json["chat_id"] = int(channel_id)
        temp_json["text"] = model_anwser
        temp_json["desc"] = model_anwser
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