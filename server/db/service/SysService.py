import logging
from typing import Union

from PdBaseKits.AES import aesECBDecrypt
from conf.logger.logQueue import logQueue
from conf.logger.logType import LogType

from entity.UserInfo import UserInfo
from server.queue.TaskQueue import taskqueue
from PdBaseKits.db.dbModels import User

class SysService:

    def login(self, username, pwd) -> Union[UserInfo, bool]:
        try:
            pwdDecrypt = aesECBDecrypt(pwd)
            logging.info(">>> pwdDecrypt :" + pwdDecrypt)
            query = User.select().where(User.username == username, User.password == pwdDecrypt).get()

            logging.info(">>> query :"+str(query.username))
        except Exception as e:
            return False

        logQueue.push("Login Succ", LogType.info)
        logging.info("id ["+str(query.id)+"], username ["+query.username+"], nickname ["+query.nickname+"], email ["+query.email+"]")
        return UserInfo(query.id, query.username, query.nickname, query.email)  #user.chkUserInfo(userId, pwdDecrypt)

    def __chkWaitQueue(self, userId: int):
        if taskqueue.findWaitTask(userId):
            return 600
        return 200

    def __chkConsurQueue(self, userId: int):
        if taskqueue.findConsurTask(userId):
            return 601
        return 200
