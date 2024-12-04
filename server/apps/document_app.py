import asyncio
import logging
from typing import Optional
import time
from fastapi import APIRouter, Depends, File, UploadFile, Response
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import StreamingResponse

from PdBaseKits.RedisLoader import RedisCntType
from PdBaseKits.db.dbModels import InformationModel
from PdBaseKits.tools.CommonTools import nonceId
from conf.logger.logQueue import logQueue
from conf.logger.logType import LogType
from PdBaseKits.redis.RedisUtil import redisUtil
from PdBaseKits.token.tokenUtil import authenticate, decodeAccessToken
from server.db.service.DocmentService import DocumentService

from server.schema.TriggerType import TriggerType
from server.schema.schema import (
    User,
    TriggerDetailOut,
    TriggerInformationListIn,
    TriggerInformationIn,
    TriggerImagineIn,
    TriggerResponse,
    TriggerOcrIn,
    TriggerListOut,
    TriggerOcrResponse, userInfo, TriggerUploadResponse,
)

router = APIRouter()



##路径参数
@router.get("/information/{id}", response_model=TriggerDetailOut)
async def information(id:str,  user: userInfo = Depends(authenticate)):
    ##v2.0
    logging.info("information id["+str(id)+"]")



    logging.info("information detail ["+id+"]")

    query = DocumentService().queryInfoDetail(id)
    print(query)
    return {"message":"succ","code":200,"data": query}


@router.get("/information", response_model=TriggerListOut)
async def information(  author: str, classify: Optional[str], pageNum: int, pageSize: int,  user: userInfo = Depends(authenticate)):
    ##v2.0

    classify = classify
    logging.info("classify ["+classify+"], pageNum ["+str(pageNum)+"]")

    query = DocumentService().queryInfoList(classify, (pageNum-1) * pageSize, pageSize)
    print(query)
    return {"message":"succ","code":200,"data": query}



@router.post("/information", response_model=TriggerResponse)
async def information(body: TriggerInformationIn,  user: userInfo = Depends(authenticate)):
    ##v2.0
    logging.info("information id["+str(body.id)+"]")
    if body.id:

        logging.info("更新information任务 id ["+str(body.id)+"], author ["+body.author+"]")

        query = InformationModel.update(author=body.author, title=body.title, classify=body.classify, content=body.content,
                                level=body.level, state=body.state, tags=body.tags).where(InformationModel.id == body.id)
        cnt = query.execute()
        logQueue.push("完成了更新information任务["+str(cnt)+"]!", LogType.info)

    else:
        logging.info("新建information任务 id ["+str(body.id)+"], author ["+body.author+"]")

        info = InformationModel(author=body.author, title=body.title, classify=body.classify, content=body.content,
                                level=body.level, state=body.state, tags=body.tags)

        info.save()

        logQueue.push("完成了新建information任务!", LogType.info)

    return {"triggerId": "msg", "triggerType": TriggerType.generate.value, "waitLen": 1}



@router.post("/imagine", response_model=TriggerResponse)
async def imagine(body: TriggerImagineIn,  user: userInfo = Depends(authenticate)):
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
async def imagine(body: TriggerOcrIn,  user: userInfo = Depends(authenticate)):

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


###pip install fastapi-limiter
##@router.post("/test", response_model="",dependencies=[Depends(RateLimiter(times=5, seconds=1))])
@router.put("/test/{id}", response_model=str)
async def test(id :int, user: userInfo = Depends(authenticate)):
    logging.info("recive put id ["+str(id)+"]")
    redisUtil.incrKey(RedisCntType.POEM_PARSE_TOTALS)
    poemCnt = redisUtil.getStr(RedisCntType.POEM_PARSE_TOTALS)
    logQueue.push(str(poemCnt)+"test!", LogType.info)
    return "succ"


## event stream
###pip install fastapi-limiter
##@router.post("/test", response_model="",dependencies=[Depends(RateLimiter(times=5, seconds=1))])
@router.get("/chatEvent", response_model=TriggerUploadResponse)
async def chatEvent(user:str, pwd:str, userI: userInfo = Depends(authenticate)):
    logging.info("test event recive user ["+str(user)+"], pwd ["+str(pwd)+"]")
    # for n in DocumentService().testEventStream():
    #     print(n)

    # g= DocumentService().testEventStream()
    # resp = StreamingResponse(g, mimetype="text/event-stream")
    # resp.headers.add_header("Cache-control", "no-cache")
    # resp.headers.add_header("Connection", "keep-alive")
    # resp.headers.add_header("X-Accel-Buffering", "no")
    # resp.headers.add_header("Content-Type", "text/event-stream; charset=utf-8")
    #
    # return resp
    #
    #
    #
    g = DocumentService().event_generator()
    return StreamingResponse(g, media_type="text/event-stream")
