import logging
import os


logger = logging.getLogger("logger")
result_path = os.path.join(os.path.dirname(__file__),"..","logs", "test.log")
handler2 = logging.FileHandler(filename=result_path,mode="w")

logger.setLevel(logging.INFO)
handler2.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler2.setFormatter(formatter)
######
handler1 = logging.StreamHandler()
handler1.setLevel(logging.INFO)
handler1.setFormatter(formatter)
logger.addHandler(handler1)
######
logger.addHandler(handler2)
