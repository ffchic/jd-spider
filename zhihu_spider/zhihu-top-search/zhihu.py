# -*- coding=utf-8 -*-

from datetime import datetime
import json
import os
import re

from lxml import etree
import requests

import log_tools


BASE_URL = 'https://www.zhihu.com'
JSON_DIR = './raw'
ARCHIVE_DIR = './archives'
LOG_DIR = './logs'

logger = log_tools.init_logger(__name__, log_path=LOG_DIR)


def get_top(url):
    ''' 获取网页 HTML 返回字符串

    Args:
        url: str, 网页网址
    Returns:
        HTML 字符串
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.json()




def main():
    try:
        top_url = "/api/v3/feed/topstory/hot-lists/total?limit=100"
        data_json = get_top(BASE_URL + top_url)
        print(data_json)
        print(type(data_json))
        depth_url = BASE_URL + "/question/{}?utm_division=hot_list_page"
        for data in data_json.get("data"):
            target = data.get("target")
            id = target["id"]
            print(id)
            print(target)
            print(type(target))

    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == '__main__':
    main()
