import pytest
import urllib3

from com.src.test.tools import *
from com.src.test.handleEmail import sendMail

urllib3.disable_warnings()
testdata = getTestData()

ids = [
    "{}->{}->{}->".format(data[0], data[2], data[3]) for data in testdata
]

# @pytest.mark.parametrize("path,method,data,params,checkpoints,desc,exec,locust,store_response",testdata)
# def test_Inter(loginPy,path,method,data,params,checkpoints,desc,exec,locust,store_response):
#     assert requestAction(path,method,data,params,checkpoints,desc,exec,locust,store_response)

@pytest.mark.parametrize("params",testdata,ids=ids)
def test_Inter(loginPy,params):
    assert requestAction(params)

if __name__ == "__main__":
    pytest.main(["-s", "test_interface.py"])
    # sendMail()