import __init__
import logging
from GUI.loader import setupWindow
from PdBaseKits.RedisLoader import initRedis
from PdBaseKits.db.dbModels import initDbModels


# ========  Config   ========


version = "1.4"


# ========  End Config   ========




if __name__ == '__main__':


    """初始化系统表结构"""
    initDbModels()
    logging.info("完成DB初始化")

    """初始化redis"""
    initRedis()
    logging.info("完成Redis加载")


    """初始化窗口"""
    setupWindow()
    logging.info("完成界面加载")




