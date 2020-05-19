import redis
from com.src.test.logger import logger


def connectRedis():
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    return r

def setString(r,key,value):
    try:
        res = r.set(key,value)
        logger.info("setString成功 %s：%s" % (key,value))
        return res
    except Exception:
        logger.exception("setString发生异常 %s:%s" % (key,value))

def getString(r,key):
    try:
        res = r.get(key)
        logger.info("getString成功 %s" % key)
        return res
    except Exception:
        logger.exception("getString发生异常 %s" % key)

def setHash(r,name,key,value):
    try:
        res = r.hset(name,key,value)
        # logger.info("setHash成功 %s：%s：%s" % (name,key,value))
        return res
    except Exception:
        logger.exception("setHash发生异常 %s：%s：%s" % (name,key,value))

def getHash(r,name,key):
    try:
        res = r.hget(name,key)
        logger.info("getHash成功 %s：%s" % (name,key))
        return res
    except Exception:
        logger.exception("getHash发生异常 %s：%s" % (name,key))

def setListL(r,name,*values):
    try:
        res = r.lpush(name,*values)
        logger.info("setList成功 %s" % name)
        return res
    except Exception:
        logger.exception("setList发生异常 %s" % name)

def setListR(r,name,*values):
    try:
        res = r.rpush(name,*values)
        logger.info("setList成功 %s" % name)
        return res
    except Exception:
        logger.exception("setList发生异常 %s" % name)


def getList(r,name,key):
    try:
        res = r.hget(name,key)
        logger.info("getHash成功 %s：%s" % (name,key))
        return res
    except Exception:
        logger.exception("getHash发生异常 %s：%s" % (name,key))

def deleteCommentRedis():
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    pattern = "comment_frequency_*_*"
    k = r.keys(pattern=pattern)
    if k:
        r.delete(*k)
        logger.info("redis删除成功 %s" % k)
    else:
        logger.info("没有匹配到需要删除的redis")

def setCommentCount(r,viewerType,titleNo,episodeNo,imageNo=[],count=0):
    if viewerType == "CUT":
        for i in imageNo:
            setHash(r,"image_comment_count","%s-%s-%s" % (titleNo,episodeNo,i),count)
            setHash(r,"image_comment_reply_count","%s-%s-%s" % (titleNo,episodeNo,i),count)
    setHash(r,"episode_comment_count","%s-%s" % (titleNo,episodeNo),count)
    setHash(r,"episode_comment_reply_count","%s-%s" % (titleNo,episodeNo),count)


def setLikeItCount(r,titleNo,episodeNo,count=0):
    setHash(r,"title_like_count","%s" % titleNo,count)
    setHash(r,"episode_like_count","%s-%s" % (titleNo,episodeNo),count)




def deleteCommentLimitRedis(r):
    pattern = "comment_frequency_*_*"
    k = r.keys(pattern=pattern)
    if k:
        r.delete(*k)
        # logger.info("redis删除成功 %s" % k)
    else:
        logger.info("没有匹配到需要删除的redis")



if __name__ == "__main__":
    r = connectRedis()
    ###cut
    imageTitleNo = 1467
    imageEpisodeNo = 1
    imageNo = 1
    ##cut
    # setHash(r,"image_comment_count","%s-%s-%s" % (imageTitleNo,imageEpisodeNo,imageNo),"0")
    # setHash(r,"image_comment_reply_count","%s-%s-%s" % (imageTitleNo,imageEpisodeNo,imageNo),"0")
    # setHash(r,"episode_comment_count","%s-%s" % (imageTitleNo,imageEpisodeNo),"0")
    # setHash(r,"episode_comment_reply_count","%s-%s" % (imageTitleNo,imageEpisodeNo),"0")
    # setLikeItCount(r,imageTitleNo,imageEpisodeNo,count=1000)
    # setLikeItCount(r,423,1,count=1000)
    deleteCommentLimitRedis(r)