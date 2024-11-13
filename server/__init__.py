from conf.ini.Initial import getIni
from server.handler.exceptions import MissRequiredVariableError

WAIT_SIZE = getIni("sys","maxtaskqueuelen")
CONSUR_SIZE = getIni("sys","maxwaitqueuelen")
TASK_TIMEOUT=getIni("sys","tasktimeout")

if not all([WAIT_SIZE,CONSUR_SIZE,TASK_TIMEOUT]):
    raise MissRequiredVariableError("Missing required environment variable: [WAIT_SIZE][CONSUR_SIZE][TASK_TIMEOUT]")
