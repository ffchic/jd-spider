# -*- coding=utf-8 -*-

import time
import random
import requests

from lxml import etree
from bs4 import BeautifulSoup
from py_sql import HotSearch,Tags



BASE_URL = 'https://www.zhihu.com'


class Spider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
        }

    def get_top(self,url):
        ''' 获取网页 HTML 返回字符串

        Args:
            url: str, 网页网址
        Returns:
            HTML 字符串
        '''

        response = requests.get(url, headers=self.headers)
        return response.json()

    def details_page(self,url):
        response = requests.get(url, headers=self.headers)

        soup = BeautifulSoup(response.content.decode("utf8"), 'lxml')
        dic_lxml = soup.find(name="div",attrs={"class":"QuestionHeader-topics"})
        label_list = dic_lxml.find_all(name="div",attrs={"class":"css-1gomreu"})
        tag_category = []
        for i in label_list:
            tag_category.append(i.text)
        num_lxml = soup.find_all(name="div",attrs={"class":"NumberBoard-itemInner"})
        follow_count, view_count = num_lxml
        follow_count = follow_count.find(name="strong").text
        follow_count = follow_count.replace(",", "")
        view_count = view_count.find(name="strong").text
        view_count = view_count.replace(",", "")
        print("    [INFO] Get hot search details [{}-{}]".format( follow_count, view_count))
        return tag_category, follow_count, view_count

    def save(self, article_id, article_title, create_time, hot_search_time, tag_category, heat, answer, follow_count, view_count):
        # 获取当前时间戳
        timestamp = time.time()
        # 将时间戳转换为日期时间
        datetime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        sql = HotSearch()
        sql_data = sql.query_by_article_id(article_id)
        # 之前不存在热榜的话题
        if not sql_data:
            sql_tag = Tags()
            tag_id_list = []
            print("    [INFO] Save label data [{}]".format(tag_category))
            for tag_name in tag_category:
                tag_data = sql_tag.query_by_id(tag_name)
                if tag_data:
                    tag_id = tag_data[0]
                    quantity = tag_data[2]+1
                    sql_tag.update(tag_id, quantity)
                else:
                    sql_tag.insert(tag_name, 1)
                    tag_data = sql_tag.query_by_id(tag_name)
                tag_id_list.append(tag_data[0])
            print("    [INFO] Save article data [{}]".format(article_title))
            tag_id_str = ",".join([str(i) for i in tag_id_list])
            data_list = [(article_id, article_title, create_time, hot_search_time, 1, tag_id_str, heat, heat, heat, heat, answer, follow_count, view_count, datetime_str, 1)]
            sql.insert_batch(data_list)
        #已经存在热榜的话题，还未下去
        else:
            print("    [INFO] Save article data [{}]".format(article_title))
            heat_max = sql_data[7]
            heat_min = sql_data[8]
            heat_sum = sql_data[9]
            if heat > heat_max:
                heat_max = heat
            elif heat < heat_min:
                heat_min = heat
            heat_sum += heat
            version = sql_data[-1]
            version += 1
            heat_avg = heat_sum/version
            duration = sql_data[5] + 1
            sql.update(article_id, duration, heat_max, heat_min, heat_avg, heat_sum, answer, follow_count, view_count, datetime_str, version)


def main():
    try:
        top_url = "/api/v3/feed/topstory/hot-lists/total?limit=100"
        print(" crawl Hot search list ...")

        spider = Spider()
        data_json = spider.get_top(BASE_URL + top_url)
        new = int(time.time())
        for i,data in enumerate(data_json.get("data")):
            target = data.get("target")
            print("[INFO {}/{}] Get hot search information [{}]".format(i, len(data_json.get("data")), target.get("title")))
            id = target["id"]
            depth_url = BASE_URL + "/question/{}?utm_division=hot_list_page"
            depth_url = depth_url.format(id)
            tag_category, follow_count, view_count = spider.details_page(depth_url)
            article_title = target.get("title")
            create_time = target.get("created")
            heat = data.get("detail_text")
            heat = int(heat.replace("热度","").replace(" ","").replace("万","")) * 10000
            answer = target.get("answer_count")
            spider.save(id,article_title, create_time, new, tag_category, heat, answer, follow_count, view_count)
            time.sleep(random.randint(8,20))


    except Exception as e:
        raise e


if __name__ == '__main__':
    main()
