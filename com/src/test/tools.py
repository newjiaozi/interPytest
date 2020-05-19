import os
import re
import jsonpath
import requests
from openpyxl import load_workbook
from com.src.test.logger import logger
from com.src.test.config import Config
from com.src.test.interface import getExpiresMd5
from com.src.test.handleSqlite import updateTmp,getCursor,getTmp
from com.src.test.handleRedis import deleteCommentRedis

conn,cursor = getCursor()

##初始化参数，获取测试用例
## path 0,method 1,data 2,params 3,checkpoints 4,desc 5 ,exec 6,locust 7,store_response 8,
def initParams(excel ="testcase.xlsx"):
    testcase_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","config",excel))
    return testcase_path


## 读取excel获取测试用例,返回数据格式为[[row1],[row2],[row3]]
def getTestData(excel ="testcase.xlsx"):
    case_result = initParams(excel)
    wb = load_workbook(case_result)
    sheet = wb.active
    data_tuple = tuple(sheet.rows)[1:]
    parsedData = parseData(data_tuple)
    return parsedData

##将excel读取出的数据cell获取真正的数据返回格式为[[],[],[]]
def parseData(data_tuple):
    a_list = []
    for i in data_tuple:
        b_list = []
        for j in i:
            b_list.append(j.value)
        if b_list[6]: ##是否执行的列
            if b_list[6].strip().lower() == "yes":
                a_list.append(b_list)
    return a_list

## 根据case数据进行接口请求
def requestAction(params,headerType=""):
    params_dict = parseParams(params,headerType)
    # logger.info(params_dict)
    if params_dict["method"]== "POST":
        resp = requests.request(params_dict["method"],params_dict['url'],data=params_dict['data'],params=params_dict["payload"],cookies=params_dict["cookies"],headers= params_dict["headers"],verify=False)
        # resp = requests.request(params_dict["method"],params_dict['url'],json=params_dict['data'],params=params_dict["payload"],cookies=params_dict["cookies"],headers= params_dict["headers"],verify=False)
    else:
        resp = requests.request(params_dict["method"],params_dict['url'],params=params_dict["payload"],cookies=params_dict["cookies"],headers= params_dict["headers"],verify=False)

    # logger.info(resp.request.url)
    updateTmp(conn, cursor, "response", resp.text)
    updateTmp(conn, cursor, "url", resp.url)
    updateTmp(conn,cursor,"scene",params_dict["desc"])
    if resp.ok:

        resp_json = resp.json()
        if resp_json.get("code",None) == 10005:
            deleteCommentRedis()
            return requestAction(params,headerType)
        store_resp = params_dict["store_resp"]
        check_point = params_dict["checks"]
        if store_resp:
            handleStoreResponse(resp_json,store_resp)
        if check_point:
            return checkResut(resp_json,check_point)
        else:
            return True
    else:
        logger.info(resp.url)
        return False

##解析每一个case，params为一行数据
## 如果对应的value中有格式如下"${getRandomMobileNum}",需要调取getRandomMobileNum方法获取返回值，替换该值；
## 如果对应的value中有格式如下"$session",session的值替换该值。
def parseParams(params,headerType):
    path_url = ""
    host_url =Config("httphost")
    method =""
    headers=handleUSD(Config("headers",headerType=headerType))
    cookies=handleUSD(Config("cookies"))
    data={}
    payload=handleUSD(Config("baseparams"))
    checks={}
    desc="默认描述desc"
    exec="No"
    locust_exec="No"
    store_resp={}
    ##url
    if params[0] : ## url
        url = host_url+params[0].strip()
        path_url = params[0].strip()
        payload.update(getExpiresMd5(path_url))
    ## method
    if params[1]:
        method = params[1].strip()
    ## data
    if params[2]:
        data = eval(params[2].strip())
        data = handleUSD(data)
    ##params payload
    if params[3]:
        payload.update(eval(params[3].strip()))
        payload = handleUSD(payload)
    ##checks
    if params[4]:
        checks = eval(params[4].strip())
    ##description
    if params[5]:
        desc = params[5].strip()
    ##exec
    if params[6]:
        exec = params[6].strip()
    ##locust_exec
    if params[7]:
        locust_exec = params[7].strip()
    ## store_response
    if params[8]:
        store_resp = eval(params[8].strip())
    return {"url":url,"path_url":path_url,"method":method,"headers":headers,"cookies":cookies,"data":data,"payload":payload,"checks":checks,"desc":desc,"exec":exec,"locust_exec":locust_exec,"store_resp":store_resp}

##处理获取全局变量或者执行某个方法
def handleUSD(dict_obj):
    if isinstance(dict_obj,dict):
        for k,v in dict_obj.items():
            if isinstance(v,dict):
                handleUSD(v)
            elif isinstance(v,str) and v.startswith("${") and v.endswith("}"):
                matchObj = re.match(r"^\$\{(.*?)\((.*?)\)\}$",v)
                meth = matchObj.group(1)
                trans_prams = matchObj.group(2)
                if meth and trans_prams:
                    dict_obj[k]=eval(meth)(trans_prams)
                elif meth:
                    dict_obj[k] = eval(meth)()
            elif isinstance(v,str) and v.startswith("$"):
                ini_param = v[1:]
                dict_obj[k] = getTmp(cursor,ini_param)

    ## 处理整体生成请求参数，如果格式json，data，params字段符合格式"${method()}",请求结果替换为整体入参。
    elif isinstance(dict_obj,str) and dict_obj.startswith("${") and dict_obj.endswith("}"):
        matchObj = re.match(r"^\$\{(.*?)\((.*?)\)\}$",dict_obj)
        meth = matchObj.group(1)
        trans_prams = matchObj.group(2)
        if meth and trans_prams:
            dict_obj=eval(meth)(trans_prams)
        elif meth:
            dict_obj = eval(meth)()
    return dict_obj

## 检查有几种，相等(==)，in(结果in预期)，contains(结果contains预期),非空(notNone)，字段存在(exists),isnum(全是数字)，len(判断长度）；
def checkResut(result,checkPoint):
    pass_count = 0
    if isinstance(checkPoint,dict):
        for i,j in checkPoint.items():
            if i.startswith("$"):
                judge = j[0]
                expect = j[1]
                jsonpath_value = jsonpath.jsonpath(result, i)
                if jsonpath_value:
                    if judge == "exists":
                        if jsonpath_value:
                            pass_count+=1
                    elif len(jsonpath_value) == 1:
                        jsonpath_value = jsonpath_value[0]
                    if judge == "==":
                        if jsonpath_value == expect:
                            pass_count+=1
                    elif judge == "notNone":
                        if jsonpath_value != "" and jsonpath_value is not None:
                            pass_count+=1
                    elif judge == "in":
                        if jsonpath_value in expect:
                            pass_count+=1
                    elif judge == "contains":
                        if expect in jsonpath_value:
                            pass_count+=1
                    elif judge == "length":
                        if len(jsonpath_value) == expect:
                            pass_count+=1
                    elif judge == "isdigit":
                        if str(jsonpath_value).isdigit():
                            pass_count+=1
    if len(checkPoint) == pass_count:
        return True
    else:
        logger.error("##"*20)
        logger.error(result)
        logger.error("$$"*20)
        logger.error(checkPoint)
        logger.error("&&"*20)
        logger.error(jsonpath_value)
        return False

##处理需要保存为全局变量的响应
def handleStoreResponse(result,store):
    if isinstance(store,dict):
        for i,j in store.items():
            if i.startswith("$"):
                jsonpath_value = jsonpath.jsonpath(result, i)
                if jsonpath_value:
                    jsonpath_value = jsonpath_value[0]
                    updateTmp(conn,cursor,j,jsonpath_value)
                # logger.info("全局SET：%s 为 %s" % (j,jsonpath_value))

if __name__ == "__main__":
    pass