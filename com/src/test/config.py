import time
import uuid
from com.src.test.logger import logger
from com.src.test.handleSqlite import updateTmp,getCursor
import configparser
import faker
import os


f = faker.Faker()

def getUUID():
    return "".join(str(uuid.uuid4()).split("-")).upper()

def getIPV4():
    return f.ipv4()

def getConfig(section,option,ini="config.ini"):
    ini_path = os.path.join(os.path.dirname(__file__),"..","config",ini)
    conf = configparser.ConfigParser()
    conf.read(ini_path)
    if conf.has_option(section,option):
        return conf.get(section,option)

def setConfig(section,option,value,ini="session.ini"):
    try:
        conf = configparser.ConfigParser()
        conf.read(ini)
        if conf.has_section(section):
            pass
        else:
            conf.add_section(section)
        conf.set(section,option,value)
    except Exception:
        logger.exception("setConfig错误")
    finally:
        conf.write(open(ini,"r+"))
        time.sleep(5)

def Config(key,section="headers",headerType=""):
    host = getConfig(section,"host")
    httphost = getConfig(section,"httphost")
    phone_uuid = getConfig(section,"phone_uuid")
    mobile = getConfig(section,"mobile")
    passwd = getConfig(section,"passwd")
    email = getConfig(section,"email")
    loginType = getConfig(section,"loginType")
    env = getConfig(section,"env")
    userAgent = getConfig(section,"userAgent")
    if headerType == "json":
        ct =  "application/json; charset=UTF-8"
    else:
        ct = "application/x-www-form-urlencoded; charset=UTF-8"

    config = {"headers":{
                        # "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                         "Content-Type": ct,
                         "HOST":host,
                         "Accept-Language":"zh-CN",
                         "user-agent":userAgent
                         },
              "httphost":httphost,
              "baseparams":{"platform":"APP_IPHONE",
                             "serviceZone":"CHINA",
                             "language":"zh-hans",
                             "locale":"zh_CN",
                             },
              "mobile":mobile,
              "passwd":passwd,
              "email":email,
              "loginType":loginType,
              "cookies":{"uuid":phone_uuid,"neo_ses":"$neo_ses"},
              "env":env,
              "qamysql":{"host":"rm-2ze984p4ljnijqtg1.mysql.rds.aliyuncs.com",
               "port":3306,
               "user":"rmtroot",
               "passwd":"dmdb2050mCn",
               "db":"webtoon",
               },
              }
    if key:
        return config[key]
    else:
        return config

conn,cursor = getCursor()
updateTmp(conn,cursor,"device",getConfig("headers","phone_uuid"))


if __name__ == "__main__":
    pass