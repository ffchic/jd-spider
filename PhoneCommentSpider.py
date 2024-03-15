import os
import re
import time
import json
import random
import codecs
import requests
from bs4 import BeautifulSoup
from py_JDComment import JDComment


brand_thre = {}
product_thre = {}
error_num = 0

def random_dic(dicts):
    dict_key_ls = list(dicts.keys())
    random.shuffle(dict_key_ls)
    new_dic = {}
    for key in dict_key_ls:
        new_dic[key] = dicts.get(key)
    return new_dic

class Spider:
    def __init__(self, comment_url, product_list=None,brand_list=None, finish_list=None ,download_path="download/", proxy_file=None):

        self.comment_url = comment_url

        self.proxy_pool = None if not proxy_file else \
            [line.strip() for line in open(proxy_file,'r').readlines()]

        self.REQUEST_HEADER = {
            "Cookie":"wlfstk_smdl=hqhwukb2a12ltdi8l7ysuo37e382oby6; __jdv=95931165|direct|-|none|-|1710515781563; __jdu=17105157815621457862545; _pst=jd_41d80db23f448; logintype=wx; unick=Suffer-x1; pin=jd_41d80db23f448; npin=jd_41d80db23f448; thor=2BCAE5D481724A06FCB86BAC61D72D8E7CC0690A9C1C93CDBC9C21DEEAD027AE745F96FE4E32B8E2A0AAA6C333C0FB1B7C2337E586C6F52B96A6206C303CDA0977D7E7C952975B4E72FBB23FF55C6CDE400EF2B296D762616032F018864ED021F2BE846901C3F4A8AB0E32D1ADB41170B46346A60E9C78B212B9B30FE56E49557EF2DD332A5B56AB6BEE98F0AFFA013AFD798807B94A8C6F7D1ADDF746743046; flash=2_fouGCeKL57nt7FmB0Omd13M7bdMm-MgiEle2aQYMBq32npEAG3X-fh7PTPxtI2xDjuttMAulwyBdBZ3fPmLLjwp38vAdiV8_HhA93GSpWoj*; _tp=ZWuUEiNZ%2FElhLY3OF%2BkNrbz8AC5etjCAcIgaOV9j9iE%3D; pinId=NfUb5jjwv3B7-MDyGwqXB7V9-x-f3wj7; ipLoc-djd=1-2800-0-0; __jda=29846306.17105157815621457862545.1710515782.1710515782.1710515782.1; __jdc=29846306; jsavif=1; jsavif=1; shshshfpa=96641626-b302-2ce7-126e-cbd53c089ea1-1710515813; shshshfpx=96641626-b302-2ce7-126e-cbd53c089ea1-1710515813; 3AB9D23F7A4B3CSS=jdd03ZLO3XPAALRWLT3Z6INJAVEMQI7GFAT5YAFMPM7O7KC4RP3DOKWZSMSBK36RROLG6CN3L4R5AFXZFBXU6VTU3WCX5GAAAAAMOIKX757QAAAAACOZC5KUTO3Z7P4X; _gia_d=1; xapieid=jdd03ZLO3XPAALRWLT3Z6INJAVEMQI7GFAT5YAFMPM7O7KC4RP3DOKWZSMSBK36RROLG6CN3L4R5AFXZFBXU6VTU3WCX5GAAAAAMOIKX757QAAAAACOZC5KUTO3Z7P4X; areaId=1; __jdb=29846306.6.17105157815621457862545|1.1710515782; shshshfpb=BApXeY8G4QetAkrg2QUXCU6CnoqKHzi97BlIQXzxo9xJ1MsBd6YO2; 3AB9D23F7A4B3C9B=ZLO3XPAALRWLT3Z6INJAVEMQI7GFAT5YAFMPM7O7KC4RP3DOKWZSMSBK36RROLG6CN3L4R5AFXZFBXU6VTU3WCX5GA",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        # 加载商品id
        if not product_list:
            self.crawl_product_list()
        else:
            self.products = json.load(open(product_list,'r',encoding='utf-8'))
            # self.products = random_dic(self.products)
            self.brand = json.load(open(brand_list,'r',encoding='utf-8'))

        # 加载已完成的列表
        self.finish_list = set()
        if finish_list:
            self.finish_list = set([line.strip() for line in open(finish_list,'r').readlines()])

        # 评论保存路径
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        self.download_path = download_path

    # 先爬取对应品牌的产品的id号，然后直接通过id号请求对应的接口拿到评论数据
    # 为了偷懒，这里没有处理同一个品牌的产品翻页的问题，只选择了同一个品牌第一页的产品来提取评论信息。
    def crawl_product_list(self):
        print(" crawl product list ...")
        product_list_url = "https://list.jd.com/list.html?cat=9987%2C653%2C655&cid3=655&cid2=653"
        web_source = requests.get(product_list_url, headers=self.REQUEST_HEADER)
        if web_source.status_code != 200:
            print("[ERROR] Status Code ERROR ...")
        else:
            product_dict = {}
            brand_dict = {}
            soup = BeautifulSoup(web_source.content.decode("utf8"), 'lxml')
            # 拿到所有手机品牌的链接
            _temp = soup.find_all(name="ul",attrs={"class":"J_valueList v-fixed"})
            all_brands = _temp[0].find_all(name="a")
            for i,url_object in enumerate(all_brands):
                title = url_object.attrs['title']
                print("[INFO {}/{}] get product id for brand [{}]".format(i,len(all_brands),url_object.attrs['title']))
                brand_url = "https://list.jd.com" + url_object.attrs['href']
                # 请求品牌对应的产品列表
                brand_products_source = requests.get(brand_url,headers=self.REQUEST_HEADER)
                if brand_products_source.status_code != 200:
                    print("[ERROR] Status Code ERROR ...")
                else:
                    products_soup = BeautifulSoup(brand_products_source.content.decode("utf8"), 'lxml')
                    # 处理第一页的30条数据，拿到id号和title名称
                    products = products_soup.find_all(name="li",attrs={"class":"gl-item"})
                    for product in products:
                        name = product.find_all(name="em")[-1].text
                        code = product.attrs['data-sku']
                        product_dict[code] = name
                        brand_dict[code] = title
                # 休眠 防止被检测到
                time.sleep(random.randint(8,20))
            with codecs.open("products.json", 'w', encoding='utf-8') as f:
                json.dump(product_dict, f, ensure_ascii=False)
            with codecs.open("brand_dict.json", 'w', encoding='utf-8') as f:
                json.dump(brand_dict, f, ensure_ascii=False)
            print("[INFO] crawl product list ...")

    def crawl_once(self,code,name,idx,cnt):
        tgt_url = self.comment_url.format(code,1)
        web_source = requests.get(tgt_url, headers=self.REQUEST_HEADER)
        json_text = web_source.content.decode("UTF-8")
        json_comments = re.findall(r"[(](.*)[)]", json_text)[0]
        comments_dict = json.loads(json_comments)
        maxPage = comments_dict.get("maxPage", 1)

        print("[{}/{} | STATUS CODE:[{}]]start crawl {}".format(idx,cnt,web_source.status_code,name))
        if web_source.status_code != 200:
            print("[ERROR] Status Code ERROR, start chrome for cookies ...")

        else:
            for page in range(1, maxPage+1):
                if product_thre.get(code,0) > 20000:
                    print("商品：",code,"  数量：", product_thre.get(code,0), "达到上限")
                    break
                tgt_url = self.comment_url.format(code, page)
                web_source = requests.get(tgt_url, headers=self.REQUEST_HEADER)

                print("     [{}/{} | STATUS CODE:[{}]]start crawl {}".format(page, maxPage+1, web_source.status_code, name))


                if web_source.status_code != 200:
                    print("[ERROR] Status Code ERROR, start chrome for cookies ...")
                soup = BeautifulSoup(web_source.content.decode("UTF-8"), 'lxml')
                if soup.find(name="p"):
                    self.save_data(soup.find(name="p").text, name, code)
                else:
                    print("[warn] cannot find json comments ...")

                time.sleep(random.randint(1,3))


    def save_data(self,json_text,name,code):
        global error_num
        # try:
        json_comments = re.findall(r"[(](.*)[)]",json_text)[0]
        comments_dict = json.loads(json_comments)
        data = []
        for comment in comments_dict['comments']:
            # 商家回复：replies  #追评价：afterUserComment -> content  # 图片： images len()
            brand = self.brand[code]
            product_id = int(code)
            content = comment.get("content")
            append_content = 1 if comment.get("afterUserComment",{}).get("content", False) else 0
            seller_reply = 1 if comment.get("replies",False) else 0
            score = comment.get("score", 5)
            is_good = 1 if score >= 3 else 0
            image_count = len(comment.get("images", []))
            d = (brand, name, product_id, content, append_content, seller_reply, score, is_good, image_count,)
            data.append(d)
        JDComment().insert_comment(data)
        product_thre[code] = product_thre.get(code, 0) + len(data)
        brand_thre[self.brand[code]] = brand_thre.get(self.brand[code], 0) + len(data)

        # except:
        #     time.sleep(20)
        #     error_num+=1
        #     if error_num >= 300:
        #         raise ValueError("报错，可能ip被封")
        #     print("[error ]re cannot match json comments ..")

    def run(self):
        product_count = len(self.products.keys()) - len(self.finish_list)
        idx = 1
        for key,name in self.products.items():
            if key in self.finish_list:continue
            if brand_thre.get(self.brand[key],0) > 200000:
                print("品牌：", self.brand[key], "数量：", brand_thre.get(self.brand[key]), "达到上限")
                continue
            name = re.sub(r"[-()\"\n\t\\#/@;:<>{}`+=~|.!?,]", "", name)
            self.crawl_once(key,name,idx,product_count)

            idx += 1

            with open("finish.txt","a+") as f:
                f.write(key+"\n")


        print("spider run over ... ")
"""
1. 批量获取某个品类的product id
2. 保存数据库
3. 写一个web服务
  3.1 数据分析
  
  好评率
  差评率
  追加率

  品牌
  
  销售量/评价率

  关键词搜索
  
  评价带图片率
"""
if __name__ == '__main__':
    # page为评论页数
    product_comment_url = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&" \
                          "productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1"

    # 未获取product id
    # spider = Spider(product_comment_url)

    # 已经拿到product id文件后
    spider = Spider(product_comment_url,"products.json", "brand_dict.json", "finish.txt")

    spider.run()