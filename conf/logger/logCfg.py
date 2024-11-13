import os,sys,logging
import datetime
def setupLogger(task):


    if "win32" in sys.platform or "win64" in sys.platform:
        logPath="c:/portunid/task/log"
    else:
        logPath="/Users/admin/portunid/log"

    if not os.path.isdir(logPath):
        os.makedirs(logPath)

    fileName = logPath+"/"+task+datetime.datetime.now().strftime('%Y%m%d')+".log"

    print("logging basic config:"+fileName)
    logging.basicConfig(filename=fileName, level=logging.DEBUG, format='[%(filename)s:%(lineno)d][%(asctime)s][%(levelname)s] %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.info("系统开始启动")