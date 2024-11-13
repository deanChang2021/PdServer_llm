### author by dean, 202409 , portunid team。
### 本工具用于请求第三方API。
### 方法需要配置第三方API的token。
import json
import logging
import urllib
from urllib.parse import urlencode

import requests

from PdBaseKits import THIRD_API_TOKEN


def POST(body, URL, token=THIRD_API_TOKEN):

    logging.info(f'{URL}')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
               "Content-Type": "application/json", 'Authorization': f'{token}'}
    jsonbody = json.dumps(body, default=lambda o: o.__dict__, sort_keys=True, indent=0)
    jsonstr = str(jsonbody).replace("\n", "").replace("\\", "").replace("\"[", "[").replace("]\"", "]")
    print(f' str 为{jsonstr}')
    #print({'headers': json.dumps(headers)})

    r = urllib.request.Request(URL, data=jsonstr.encode('utf-8'), headers=headers)
    try:
        response = urllib.request.urlopen(r, timeout=6)
        status = response.status
        logging.info(f"上报返回为{response}")
        logging.info(status)
        if status == 200:
            logging.info("上报成功")
            the_page = response.read()
            content = the_page.decode("utf8")
            logging.info(content)
            return content
        else:
            logging.info(f'调用 product-api 异常: {status}')
            logging.info(response.data)

    except Exception as e:
                logging.info(f'调用 product-api 异常')
                logging.info(e)
                return False


def GET(URL, params, token=THIRD_API_TOKEN):

    if params:
        newUrl = f"{URL}?{urlencode(params)}"
    else:
        newUrl = URL

    # print(newUrl)
    logging.info(f'{newUrl}')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
               "Content-Type": "application/json", 'Authorization': f'{token}'}

    try:
        res = requests.get(newUrl, headers=headers)
        return res.text
    except Exception as e:
                logging.info(f'调用 product-api 异常')
                logging.info(e)
                return False

