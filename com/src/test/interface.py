import requests
import time,datetime
import os
import json
import hashlib
import base64
import rsa,binascii
from com.src.test.logger import logger
from com.src.test.config import Config

oslinesep = os.linesep

## 生成expires和md5
def getExpiresMd5(pathstr,skey="the_scret_key"):
    now30 = datetime.datetime.now() + datetime.timedelta(minutes=30)
    utime = str(int(time.mktime(now30.timetuple())))
    msg = utime+" "+pathstr+" "+skey
    m = hashlib.md5()
    m.update(msg.encode(encoding="utf-8"))
    msg_md5 = m.digest()
    msg_md5_base64 = base64.urlsafe_b64encode(msg_md5)
    msg_md5_base64_str = msg_md5_base64.decode("utf-8")
    msg_md5_base64_str = msg_md5_base64_str.replace("=", "")
    return {"md5":msg_md5_base64_str,"expires":utime}

def appRsakeyGet():
    path = "/app/rsakey/get"
    try:
        # logger.info("#"*20)
        # logger.info(Config("httphost"))
        # logger.info("@"*20)
        resp = requests.get(Config("httphost")+path,params=getExpiresMd5(path),headers=Config("headers"))
        resp_json = resp.json()
        evalue = resp_json["message"]["result"]["evalue"]
        keyName = resp_json["message"]["result"]["keyName"]
        nvalue = resp_json["message"]["result"]["nvalue"]
        sessionKey = resp_json["message"]["result"]["sessionKey"]
        return keyName,evalue,nvalue,sessionKey
    except Exception:
        logger.exception("appRsakeyGet出现异常")
        logger.error(resp.url)
        logger.error(resp.text)
        logger.error(resp.headers)
        return False

###加密操作
def rsaEnc(rsa_n,rsa_e,sessionKey,mobile,passwd):
    rsa_e = rsa_e.lower()
    rsa_n = rsa_n.lower()
    key = rsa.PublicKey(int(rsa_e,16),int(rsa_n,16))
    message = chr(len(sessionKey))+sessionKey+chr(len(mobile))+mobile+chr(len(passwd))+passwd
    message = rsa.encrypt(message.encode(),key)
    message = binascii.b2a_hex(message)
    return message.decode()

##登录，"563828","PHONE_VERIFICATION_CODE"，##PHONE_NUMBER
def login(username,passwd,loginType="EMAIL"):
    path="/app/member/id/login"
    ne = appRsakeyGet()
    if ne:
        try:
            # logger.info("%s--%s" % (username,passwd))
            encpw = rsaEnc(ne[2], ne[1], ne[3], mobile=username, passwd=passwd)
            encnm = ne[0]
            plus = {"loginType":loginType,"encnm":encnm,"encpw":encpw,"v":1}
            plus.update(Config("baseparams"))
            resp = requests.post(Config("httphost")+path,headers=Config("headers"),data=plus,params= getExpiresMd5(path))
            resp_json = resp.json()
            neo_ses = resp_json["message"]["result"]["ses"]
            neo_id = resp_json["message"]["result"]["id_no"]
            return neo_ses,neo_id
        except Exception:
            logger.exception("login出现异常")
            logger.error(resp.url)
            logger.error(resp.text)
            logger.error(resp.headers)
            return False
    else:
        return False

##更新页数据
def appHomeCard2(weekday):
    path ="/app/home/card2"
    payload = {"weekday":weekday,"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        ####处理更新页
        # if weekday == "COMPLETE":
        #     resulttmp["titleAndEpisodeList"].sort(key=lambda x: (x["mana"],x["titleNo"]), reverse=True)
        #     result["title"] = resulttmp["titleAndEpisodeList"]
        # else:
        #     resulttmp["titleAndEpisodeList"].sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
        #     result["title"] = resulttmp["titleAndEpisodeList"]
        #     resulttmp["noticeCard"].sort(key=lambda x:int(x["exposurePosition"]))
        #     result["banner"] = resulttmp["noticeCard"]
        return resp_json
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

##home4，发现页数据
def appHome4(weekday="MONDAY",cookies=""):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        # logger.error(resp.url)
        logger.error(resp.text)
        return False

def appHome4Priority(weekday="MONDAY"):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1,"homeDetailDataStatus":"LEAD_UP_DATA"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        # print(resp_json)
        ####处理发现页bigbanner
        resulttmp = resp_json["message"]["result"]
        ###咚漫推荐
        return resulttmp["leadUpLookList"]
    else:
        logger.error(resp.url)
        logger.error(resp.text)

def appHome4DM(weekday="MONDAY"):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1,"homeDetailDataStatus":"RECOMMEND_DATA"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))

    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        # print(resp_json)
        ####处理发现页bigbanner
        resulttmp = resp_json["message"]["result"]
        ###咚漫推荐
        return resulttmp["dongmanRecommendContentList"]
    else:
        print(resp.text)

### list2能够获取作品的所有数据
def appTitleList2():
    path ="/app/title/list2"
    payload = {"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

### 发现页的，排行
def appTitleRanking():
    path ="/app/title/ranking"
    payload = {"v":3,"rankingType":"ALL"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        print(resp.text)

##获取genre 分类数据
def appGenrelist2():
    path ="/app/genreList2"
    payload = {"v":2}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

###返回三个titleName
def everyOneWatching(titleNoList=""):
    path="/app/myComics/everyoneWatching"
    if titleNoList:
        payload = {"respTitleCount":3,"titleNoList":titleNoList,"v":3}
    else:
        payload = {"respTitleCount":3,"v":3}

    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        ranklist = resp.json()
        return ranklist
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def appFavouriteTotalList2(cookies=""):
    path="/app/favorite/totalList2"
    payload= {"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
    if resp.ok:
        titles = resp.json()

        return titles
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def getGenreData(genre="all",status="all",sortby="人气"):
    genreDict = {"恋爱":"LOVE",
                 "少年":"BOY",
                 "古风":"ANCIENTCHINESE",
                 "奇幻":"FANTASY",
                 "搞笑": "COMEDY",
                 "校园": "CAMPUS",
                 "都市": "METROPOLIS",
                 "治愈": "HEALING",
                 "悬疑": "SUSPENSE",
                 "励志": "INSPIRATIONAL",
                 # "影视化":"FILMADAPTATION"
                 }
    statusDict = {"连载":"SERIES","完结":"TERMINATION"}
    path ="/app/title/list2"
    payload = {"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result = []
        resp_json = resp.json()
        # print(resp_json)
        resulttmp = resp_json["message"]["result"]
        titles= resulttmp["titleList"]["titles"]
        genre = genre.strip().lower()
        status = status.strip().lower()
        sortby =  sortby.strip().lower()
        if genre == "all":
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    print("ALL、ALL、人气:%s个" % len(titles))
                    for i in titles:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    print("ALL、ALL、最新:%s个" % len(titles))
                    for i in titles:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        print("ALL、%s、人气:%s个" % (status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x: (x["mana"], x["titleNo"]), reverse=True)
                        result = list(filter(lambda x: x["restTerminationStatus"] == statusDict[status], titles))
                        print("ALL、%s、人气:%s个" % (status, len(result)))
                        for i in result:
                            print(i['title'], i["subGenre"], i['restTerminationStatus'], i["mana"], i["titleNo"],
                                  "%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    print("ALL、%s、最新:%s个" % (status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

        elif genre in genreDict:
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"] ,titles))
                    print("%s、ALL、人气:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["representGenre"],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],titles))
                    print("%s、ALL、最新:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                    print("%s、%s、最新:%s个" % (genre,status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

        elif genre == "影视化":
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["filmAdaptation"],titles))
                    print("%s、ALL、人气:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["filmAdaptation"],titles))
                    print("%s、ALL、最新:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:x["filmAdaptation"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    result = list(filter(lambda x:x["filmAdaptation"],result))
                    print("%s、%s、最新:%s个" % (genre,status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

def appCommentTitleepisodeinfo2(telist):
    path="/app/comment/titleEpisodeInfo2"
    telist2Json = json.dumps(telist)
    payload = {"objectIdsJson":telist2Json}
    payload.update(Config("baseparams"))
    resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"))
    commentTitleEpisodeInfo = resp.json()["message"]["result"]["commentTitleEpisodeInfo"]
    return commentTitleEpisodeInfo

## 获取人气页关注列表
def appMyFavorite2(cookies=""):
    path ="/app/myFavorite2"
    payload = {"v":3,"sortOrder":"UPDATE"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
    if resp.ok:
        return resp.json()
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

## 获取章节点赞数
def v1TitleLikeAndCount(titleEpisodeNos,cookies=""):
    path ="/v1/title/likeAndCount"
    payload = {"titleEpisodeNos":",".join(map(lambda x:str(x),titleEpisodeNos))}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
    if resp.ok:
        data = resp.json()
        return data
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

##获取关注列表
def appFavouriteTotalList2(cookies=""):
    path="/app/favorite/totalList2"
    payload = {"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
    if resp.ok:
        return resp.json()
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

## 获取热词
def appGetHotWordNew():
    path = "/app/getHotWordNew"
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

##获取自定义菜单
def appHomeMenus():
    path = '/app/home/menus'
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##获取自定义菜单detail
def appHomeMenuDetail(menuId):
    path='/app/home/menu/detail'
    payload = {"menuId":menuId}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##自定义菜单的更多操作
def appHomeMenuModuleMore(menuId,moduleId):
    path='/app/home/menu/module/more'
    payload = {"menuId":menuId,"moduleId":moduleId}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)
        return False

##获取章节信息
def appEpisodeInfoV3(titleNo,episodeNo,purchase=0,v=10,cookies=""):
    path='/app/episode/info/v3'
    payload = {"titleNo":titleNo,"episodeNo":episodeNo,"purchase":purchase,"v":v}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)

##章节点赞数
def v1TitleEpisodeLikeCount(titleNo,episodeNos,cookies=0):
    path='/v1/title/%s/episode/likeAndCount' % titleNo
    payload = {"episodeNos":",".join(map(lambda x:str(x),episodeNos))}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)

##获取作品信息
def appTitleInfo2(titleNo):
    path='/app/title/info2'
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)

##底部推荐，或者其他作者，类似推荐的接口
def appTitleRecommend2(titleNo):
    path='/app/title/recommend2'
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##抢先看更多的接口
def appHomeLeaduplook():
    path = "/app/home/leadUpLook"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##咚漫推荐
def appHomeRecommend2():
    path='/app/home/recommend2'
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
       logger.exception(resp.url)

##ppl接口
def appPPLInfo(titleNo,episodeNo,v=5):
    path='/app/ppl/info'
    payload = {"titleNo":titleNo,"episodeNo":episodeNo,"v":v}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##作者信息
def appAuthorInfo2(titleNo):
    path = "/app/author/info2"
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##章节列表接口
def appEpisodeListV3(titleNo,cookies=""):
    path = "/app/episode/list/v3"
    payload = {"titleNo": titleNo, "v": 10}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)
        return False

##隐藏的章节的接口
def appEpisodeListHide(titleNo,cookies=""):
    path = "/app/episode/list/hide"
    payload = {"titleNo": titleNo, "v": 7}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##查询用户信息接口
def appMemeberInfoV2(cookies=""):
    path = "/app/member/info/v2"
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)


##0:12岁以下，1:13～15岁，2:16～18岁，3:19～22岁，4:23～25岁，5:26～35岁，6:36岁以上
##用户画像
def appUserpreferenceNewadd(ancientchinese,boy,campus,comedy,
                            fantasy,filmadaptation,healing,
                            inspirational,love,metropolis,suspense,termination,
                            isNewUser,age,gender,cookies=""):
    path = "/app/userPreference/newAdd"
    if age:
        if ancientchinese or boy or campus or comedy or fantasy or filmadaptation or healing or inspirational or love or metropolis or suspense or termination:
            payload = {"age":age,
                       "ancientChinese":ancientchinese,
                       "boy":boy,
                       "campus":campus,
                       "comedy":comedy,
                       "fantasy":fantasy,
                       "filmAdaptation":filmadaptation,
                       "gender":gender,
                       "healing":healing,
                       "inspirational":inspirational,
                       "love":love,
                       "metropolis":metropolis,
                       "suspense":suspense,
                       "termination":termination,
                       "isNewUser":isNewUser,
                       }
        else:
            payload = {"age":age,
                       "gender": gender,
                       "isNewUser":isNewUser,
                       }
    else:
        if ancientchinese or boy or campus or comedy or fantasy or filmadaptation or healing or inspirational or love or metropolis or suspense or termination:
            payload = {
                       "ancientChinese":ancientchinese,
                       "boy":boy,
                       "campus":campus,
                       "comedy":comedy,
                       "fantasy":fantasy,
                       "filmAdaptation":filmadaptation,
                       "gender":gender,
                       "healing":healing,
                       "inspirational":inspirational,
                       "love":love,
                       "metropolis":metropolis,
                       "suspense":suspense,
                       "termination":termination,
                       "isNewUser":isNewUser,
                       }
        else:
            payload = {
                        "gender": gender,
                        "isNewUser":isNewUser,
                       }
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost")+path, params=payload,headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)

##获取app最新版本
def appClientVersionLatest():
    path = "/app/client/version/latest"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##app是否更新？
def appClientVersion():
    path = "/app/client/version"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##关注的列表
def appFavoriteAdd(titleNo,cookies=""):
    path = "/app/favorite/add"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"titleNo":titleNo})
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##添加关注
def appFavoriteAdd(titleNo,cookies=""):
    path = "/app/favorite/add"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"titleNo":titleNo})
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##全部移除关注
def appFavoriteTotalRemoveAll(cookies):
    path = "/app/favorite/totalRemoveAll"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

##查询配置信息，是否ABtest版本
def testingConfigInfo(version="2.2.4"):
    path = "/testing/configInfo"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"version":version})
    try:
        resp = requests.get("https://qaptsapis.dongmanmanhua.cn" + path, params=payload, headers=Config("headers"))
        result = resp.json()
        return result
    except Exception:
        logger.exception(resp.url)
        return False

##保存昵称个人信息
def saveNickname(nickname,cookies=""):
    path = "/app/member/save"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"birthday":"2018 . 08 . 08","gender":"G","nickname":"✅%s" % nickname })
    if cookies:
        cookies.update(Config("cookies"))
    else:
        cookies = Config("cookies")
    try:
        resp = requests.get(Config("httphost")+ path, params=payload, headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.exception(resp.url)
        return False

if __name__=="__main__":
    pass
    login(Config("mobile"),Config("passwd"),"PHONE_NUMBER")

