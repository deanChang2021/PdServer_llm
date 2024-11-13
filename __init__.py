from conf.ini.Initial import initialSysConfig
from conf.logger.logCfg import setupLogger
import logging



"""初始化系统参数"""
initialSysConfig()


setupLogger("pdServer")
logging.info("开始初始化系统配置文件……")
