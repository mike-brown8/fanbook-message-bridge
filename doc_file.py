# coding=UTF-8

help_text = '''--- HELP DOCUMENT START ---
114514 | 立即开始恶臭
exit   | 退出程序
say    | 向API发送文本信息
cmode  | 进入聊天模式，输入内容直接转发
ulup   | 在当前频道搜索用户(长ID)
uslup  | 在当前频道搜索用户(短ID)
chlup  | 在当前服务器内搜寻频道(长ID)
sblack | 封禁指定用户的GPT权限(短ID) - 分支专属
rblack | 解封指定用户的GPT权限(短ID) - 分支专属
gtime  | 获取指定用户的GPT次数(短ID) - 分支专属
stime  | 设置指定用户的GPT次数(短ID 次数) - 分支专属
--- HELP DOCUMENT END ---'''

t114514 = "1145141919810"

default_config = """[basic]
bot_token = ENTER_BOT_TOKEN
guild_id = ENTER_GUILD_ID
channel_id = ENTER_CHANNEL_ID
message_id = 0
"""