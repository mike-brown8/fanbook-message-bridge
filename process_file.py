# coding=UTF-8-BOM
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
def text_message(message_id:str,message_sender_id:str,message_sender_nick:str,message_text_ori:str,message_text_format:str):
    # message_id 消息唯一长ID
    # message_sender_id 发送者唯一短ID
    # message_sender_nick 发送者外显名
    # message_text_ori 消息原文，@和#未转义
    # message_text_format 转义@和#后的消息
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