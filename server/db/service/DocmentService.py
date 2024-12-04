import asyncio
import json
import logging
import shutil
import time
from typing import Union, List

from fastapi import UploadFile
from PdBaseKits.NetUtil import  GET, POST
from PdBaseKits.OCR.ocr import OCR
from PdBaseKits.RedisLoader import RedisCntType
from PdBaseKits.db.dbModels import InformationModel
from PdBaseKits.llm.chat import LLM, PoemInfo
from PdBaseKits.redis.RedisUtil import redisUtil
from PdBaseKits.tools.CommonTools import getSaveUploadFilePath, getFileName, nonceId
from PdBaseKits.tools.imageTools import writeImg2Local
from business.demoService import demo
from conf.logger.logQueue import logQueue
from entity.entity import Information
from server import WAIT_SIZE

from server.db.service import MIDJOURNEY_IMG_URL, MIDJOURNEY_IMG_TOKEN, GET_MIDJOURNEY_IMG_URL
from server.handler.handler import unique_id
from server.queue.TaskQueue import taskqueue
from server.schema.TriggerType import TriggerType
from server.schema.schema import TriggerImagineIn


class DocumentService:

    async def event_generator(self):
        i = 10
        for i in range(0,10):
            if i ==9:
                '''这是一个标准格式，不要修改data，否则前端无法解析'''
                ss = json.dumps({"picUrl": nonceId(),"state":"end", "message": "ok", "code": 200})
                data = "event: message\n"+"data:"+ss+"\n\n"
                #data = f'"event": "state":"end","message":"succ","data":{nonceId()}\n'
            else:
                ss = json.dumps({"picUrl": nonceId(), "state": "running", "message": "ok", "code": 200})
                data = "event: message\n"+"data:"+ss+"\n\n"
                #data = f'"event": "state":"running","message":"succ","data":{nonceId()}\n'

            yield data
            await asyncio.sleep(1)

    async def testEventStream(self):
            res_str = "双天至尊真是一部好的电视剧！！！"
            for i in res_str:

                data = f'"event": "message"\n"data":{i}\n'
                yield "data:" + json.dumps({"picUrl": nonceId(), "message": "ok", "code": 200},
                                           ensure_ascii=False) + "\n\n"
                await asyncio.sleep(1)


    def queryInfoDetail(self, id:str):
        '''param: 归属类目'''
        logging.info("queryInfoDetail ["+id+"]")
        query = InformationModel.select().where(InformationModel.id == int(id)).get()

        return { 'id' :query.id ,
                'title' : query.title,
                'author': query.author,
                'classify':query.classify,
                'content': query.content,
                'level' : query.level,
                'state' :query.state,
                'tags' : query.tags ,
                'createDate' : query.createDate.strftime('%Y-%m-%d %H:%M:%S')}

    def queryInfoList(self, c:str, start:int, length:int):
        '''param: 归属类目'''
        logging.info("queryInfoList ["+c+"]")
        query = InformationModel.select().where(InformationModel.classify == c).order_by(-InformationModel.createDate).paginate(int(start), int(length))

        dataList : List[Information] = []
        for pet in query:

            dataList.append({ 'id' :pet.id ,
                            'title' : pet.title,
                            'author': pet.author,
                            'classify':pet.classify,

                            'level' : pet.level,
                            'state' :pet.state,
                            'tags' : pet.tags ,
                            'createDate' : pet.createDate.strftime('%Y-%m-%d %H:%M:%S')})
            logging.info(">>> query author:" + str(pet.author))

        return dataList


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


    def uploadTask(self, file: UploadFile, fileName: str):


        tmpArr = fileName.split(".")
        sysFileName = getFileName(tmpArr[-1]) #随机名字

        try:
            filePath = getSaveUploadFilePath() + sysFileName
            logging.info("filePath ["+filePath+"]")
            with open(filePath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except Exception as e:
            logging.error("upload error:"+str(e))
            return None

        return filePath, sysFileName


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




