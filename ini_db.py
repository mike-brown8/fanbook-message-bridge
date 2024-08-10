from configparser import ConfigParser
import os

print("Loaded ini_db.py")

conf = ConfigParser()
conf.read("database.ini",encoding="UTF-8")
default_gpt_time = 0

def db_save():
    with open("database.ini","w",encoding="UTF-8") as f:
        conf.write(f)
    return None

def read_black(sid:int):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
        conf.set(str(sid),"gpt-black",str(False))
    if conf.has_option(str(sid),"gpt-black") == False:
        conf.set(str(sid),"gpt-black",str(False))
    return(conf.getboolean(str(sid),"gpt-black"))

def set_black(sid:int,boolean_value:bool):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
    conf.set(str(sid),"gpt-black",str(boolean_value))
    return None

def read_time(sid:int):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
        conf.set(str(sid),"gpt-time",str(default_gpt_time))
    if conf.has_option(str(sid),"gpt-time") == False:
        conf.set(str(sid),"gpt-time",str(default_gpt_time))
    return(conf.getint(str(sid),"gpt-time"))

def set_time(sid:int,time:int):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
    conf.set(str(sid),"gpt-time",str(time))
    return None

def read_agree(sid:int):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
        conf.set(str(sid),"gpt-agree",str(False))
    if conf.has_option(str(sid),"gpt-agree") == False:
        conf.set(str(sid),"gpt-agree",str(False))
    return(conf.getboolean(str(sid),"gpt-agree"))

def set_agree(sid:int,boolean_value:bool):
    if conf.has_section(str(sid)) == False:
        conf.add_section(str(sid))
    conf.set(str(sid),"gpt-agree",str(boolean_value))
    return None