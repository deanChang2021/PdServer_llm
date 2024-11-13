import json
import logging
import shutil
import time
from typing import Union

from fastapi import UploadFile
from PdBaseKits.NetUtil import  GET, POST
from PdBaseKits.OCR.ocr import OCR
from PdBaseKits.RedisLoader import RedisCntType
from PdBaseKits.llm.chat import LLM, PoemInfo
from PdBaseKits.redis.RedisUtil import redisUtil
from PdBaseKits.tools.CommonTools import getSaveUploadFilePath, getFileName
from PdBaseKits.tools.imageTools import writeImg2Local
from business.demoService import demo
from conf.logger.logQueue import logQueue
from server import WAIT_SIZE

from server.db.service import MIDJOURNEY_IMG_URL, MIDJOURNEY_IMG_TOKEN, GET_MIDJOURNEY_IMG_URL
from server.handler.handler import unique_id
from server.queue.TaskQueue import taskqueue
from server.schema.TriggerType import TriggerType
from server.schema.schema import TriggerImagineIn


class DocumentService:

    def imageingTask(self, body: TriggerImagineIn):
        logQueue.info("recive imagine task")
        redisUtil.incrKey(RedisCntType.POEM_PARSE_TOTALS)
        logging.info("POEM_PARSE_TOTALS:"+str(redisUtil.getStr(RedisCntType.POEM_PARSE_TOTALS)))


        if (taskqueue.currentWaitQueueLen() >= int(WAIT_SIZE)):
            return 603, " task queue is full", WAIT_SIZE

        """生成唯一任务ID"""
        triggerId = str(unique_id())

        taskqueue.put(str(body.userId), demo, triggerId, TriggerType.generate.value)

        return 200, "1231232", "2"


    def uploadTask(self, file: UploadFile, fileName: str) -> Union[str,None]:


        tmpArr = fileName.split(".")
        sysFileName = getFileName(tmpArr[-1])

        try:
            filePath = getSaveUploadFilePath() + sysFileName
            logging.info("filePath ["+filePath+"]")
            with open(filePath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except Exception as e:
            logging.error(str(e))
            return None

        return sysFileName


    def parsePoemTask(self, fileName) -> tuple[str, PoemInfo]:
        filePath = getSaveUploadFilePath() + fileName
        logging.info("filePath:" + filePath)

        """ocr对图片进行识别"""
        poem:str = OCR().ocr(filePath, "chi_sim")

        """QWEN对古诗解析并生成prompt"""
        ret = LLM().chatPoem(poem)

        redisUtil.incrKey(RedisCntType.POEM_PARSE_TOTALS)

        promptList:[] = ret.prompt
        for prompt in promptList:
            """midjourney基于prompt生成图片"""

            with open('d:/test/prompt.txt', mode='a', encoding='utf-8') as f:
                f.write(prompt)
                f.write("\n")

            self.requestMidjourneyImg(prompt)

        logging.info("--- end chat ----")

        return poem, ret


    def requestMidjourneyImg(self, prompt):



        param ={"lang": "en",
                    "params": "   --ar 1:1  --v 6.0 ",
                    "picurl": "",
                    "prompt": prompt
                    }
        res = POST(param, MIDJOURNEY_IMG_URL, MIDJOURNEY_IMG_TOKEN)


        if(type(res) != type({})):
            logging.info("not a dict")
            jsonRes = json.loads(res)


        logging.info(jsonRes["data"]["businessId"])


        logging.info("收到请求的businessId["+jsonRes["data"]["businessId"]+"]")

        while(True):
            params = {"businessId":jsonRes["data"]["businessId"]}
            res = GET(GET_MIDJOURNEY_IMG_URL, params, MIDJOURNEY_IMG_TOKEN)

            if (type(res) != type({})):
                logging.info("not a dict")
                jsonPicRes = json.loads(res)
            logging.info(jsonPicRes)
            logging.info(jsonPicRes["data"]["picurl"])
            if jsonPicRes["data"]["picurl"]:
                logging.info("ok:"+ jsonPicRes["data"]["picurl"])
                writeImg2Local(jsonPicRes["data"]["picurl"], "d:/test",jsonPicRes["data"]["picurl"].split("/")[-1])
                break
            else:
                logging.info("sleep")
                time.sleep(6)

        logging.info("收到图片："+jsonPicRes["data"]["picurl"])




