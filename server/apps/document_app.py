import logging
from fastapi import APIRouter, Depends, File, UploadFile

from PdBaseKits.RedisLoader import RedisCntType
from conf.logger.logQueue import logQueue
from conf.logger.logType import LogType
from PdBaseKits.redis.RedisUtil import redisUtil
from PdBaseKits.token.tokenUtil import authenticate, decodeAccessToken
from server.db.service.DocmentService import DocumentService

from server.schema.TriggerType import TriggerType
from server.schema.schema import (
    TriggerImagineIn,
    TriggerResponse,
    TriggerOcrIn, TriggerOcrResponse,
)

router = APIRouter()

@router.post("/imagine", response_model=TriggerResponse)
async def imagine(body: TriggerImagineIn, token: str = Depends(authenticate)):
    ##v2.0
    midService = DocumentService()
    code, msg, len = midService.imageingTask(body)
    if code != 200:
        return {"code": code, "message": msg}
    logQueue.push("完成了imagine任务!", LogType.info)
    return {"triggerId": msg, "triggerType": TriggerType.generate.value, "waitLen": len}




### Author : dean Date: 20240919
### 本接口实现文件上传
@router.post("/uploader/")
async def create_upload_file(file: UploadFile = File(...), source: str = ""):
    logging.info("收到上传文件[" + file.filename + "]")


    fileName = DocumentService().uploadTask(file, file.filename)
    if fileName == None:
        return {"code":500,"msg":"上传文件失败"}
    return {"code":200, "filename": fileName}



@router.post("/ocrPoem", response_model=TriggerOcrResponse)
async def imagine(body: TriggerOcrIn, token: str = Depends(authenticate)):
    print(decodeAccessToken(token))
    logQueue.push("收到诗词解析任务请求！", LogType.info)

    ##v2.0
    midService = DocumentService()
    poem, poemParse = midService.parsePoemTask(body.fileName)
    logging.info(poem)
    logging.info(poemParse)
    if poemParse == None:
        return {"code": 500, "message": "解析失败"}

    logQueue.push("完成了["+str(poemParse.bookName)+"]解析!", LogType.info)
    return {"poem": poem, "parse": poemParse.parse, "prompt": poemParse.prompt}




@router.post("/test", response_model="")
async def test(body, token: str = Depends(authenticate)):
    redisUtil.incrKey(RedisCntType.POEM_PARSE_TOTALS)