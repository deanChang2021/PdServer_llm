import logging
from datetime import timedelta
from fastapi import APIRouter

from PdBaseKits.token.tokenUtil import createAccessToken, ACCESS_TOKEN_EXPIRE_MINUTES
from server.db.service.SysService import SysService
from server.schema.schema import (
    User, UserLoginResponse, )

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse)
async def login(body: User):
    midService = SysService()

    logging.info("login [" + body.user + "],[" + body.pwd + "]]")

    userInfo = midService.login(body.user, body.pwd)
    if userInfo:
        accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        accessToken = createAccessToken(data={"userName": body.user, 'id': 12}, expires_delta=accessTokenExpires)
        return {"user": userInfo.username, "id": userInfo.id, 'token': accessToken, 'nickname': userInfo.nickname, 'headUrl': 'i.png'}
    else:
        return {"code":500}



