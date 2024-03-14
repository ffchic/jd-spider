import os
import re
import time
import json
import random
import codecs
import requests
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, comment_url, product_list=None,finish_list=None ,download_path="download/", proxy_file=None):

        self.comment_url = comment_url

        self.proxy_pool = None if not proxy_file else \
            [line.strip() for line in open(proxy_file,'r').readlines()]

        self.REQUEST_HEADER = {
            "Cookie":"shshshfp=24670528370b016eb37cacadd64cb534; shshshfpa=1c9d3201-b6f3-0e8a-1b47-e3b8f1037e16-1680933557; shshshfpx=1c9d3201-b6f3-0e8a-1b47-e3b8f1037e16-1680933557; joyya=1705330053.0.6.0yb4taj; __jdu=1705330053829963086395; wlfstk_smdl=vv5uj97stjokh1yq0cr6qsfprljgun4p; __jdv=95931165|direct|-|none|-|1710425584935; _pst=jd_41d80db23f448; logintype=wx; unick=Suffer-x1; pin=jd_41d80db23f448; npin=jd_41d80db23f448; thor=2BCAE5D481724A06FCB86BAC61D72D8E7CC0690A9C1C93CDBC9C21DEEAD027AE2A147915AB02970AB58301A2CA12C550C3F024DC3288B3B64A3535E0CED9C13E0AEEE36F61DDC74EBB8C79BB0AD4E90ABE04FAD78F5F9E765C74FB4048B4896E4B457B0D6D1F285B64C744F1F340C8D10E16540FC555F858D8C7D0FEC5B2AA434A8761F3DA3706BE7B6028A97CDBA9F4516D0397D200469E2B051889B99D31C8; flash=2_Y-vhED9OYBf8od6vWsvzUPJqoLouFQkQavJF0E4PrHeSjswq0OXKYARWYL30fzNSPgcYlT-l60Eo9ZmQNm-H5zqPytD5mw-NcGxV1nJ3Yij*; _tp=ZWuUEiNZ%2FElhLY3OF%2BkNrbz8AC5etjCAcIgaOV9j9iE%3D; pinId=NfUb5jjwv3B7-MDyGwqXB7V9-x-f3wj7; ipLoc-djd=1-2901-0-0; __jda=29846306.1705330053829963086395.1705330054.1706538576.1710425585.3; __jdc=29846306; jsavif=1; jsavif=1; areaId=1; avif=1; xapieid=jdd03YJKTW2LSZF2AH3FJ5OTGVXILJTNAOA3UQN5WDLHLKKYAJQVSJCWU3ASH57TFXTP2WH4UVL7Z2A7OOAVSVSV6MXW2JYAAAAMOHVHVSBQAAAAADYYASIAMFQS4NIX; __jdb=29846306.6.1705330053829963086395|3.1710425585; 3AB9D23F7A4B3CSS=jdd03YJKTW2LSZF2AH3FJ5OTGVXILJTNAOA3UQN5WDLHLKKYAJQVSJCWU3ASH57TFXTP2WH4UVL7Z2A7OOAVSVSV6MXW2JYAAAAMOHVNOIHIAAAAACDBOY6EHHOUWBQX; _gia_d=1; shshshfpb=BApXe1HFSPutAa5wRRLTgPqmOis9Kxc_MB8LSMnhr9xJ1Mjl-uIO2; 3AB9D23F7A4B3C9B=YJKTW2LSZF2AH3FJ5OTGVXILJTNAOA3UQN5WDLHLKKYAJQVSJCWU3ASH57TFXTP2WH4UVL7Z2A7OOAVSVSV6MXW2JY",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        # 加载商品id
        if not product_list:
            self.crawl_product_list()
            with codecs.open("products.json",'r',encoding='utf-8') as f:
                print(">>>",f.read())
        else:
            self.products = json.load(open(product_list,'r',encoding='utf-8'))

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
            soup = BeautifulSoup(web_source.content.decode("utf8"), 'lxml')
            # 拿到所有手机品牌的链接
            _temp = soup.find_all(name="ul",attrs={"class":"J_valueList v-fixed"})
            all_brands = _temp[0].find_all(name="a")
            for i,url_object in enumerate(all_brands[:2]):
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
                    product_dict = {}
                    for product in products:
                        name = product.find_all(name="em")[-1].text
                        code = product.attrs['data-sku']
                        product_dict[code] = name
                    with codecs.open("products.json", 'w', encoding='utf-8') as f:
                        json.dump(product_dict, f, ensure_ascii=False)
                # 休眠 防止被检测到
                time.sleep(random.randint(8,20))

            print("[INFO] crawl product list ...")

    def crawl_once(self,code,name,idx,cnt):
        tgt_url = self.comment_url.format(code)
        web_source = requests.get(tgt_url, headers=self.REQUEST_HEADER)

        print("[{}/{} | STATUS CODE:[{}]]start crawl {}".format(idx,cnt,web_source.status_code,name))
        if web_source.status_code != 200:

            print("[ERROR] Status Code ERROR, start chrome for cookies ...")

        else:
            soup = BeautifulSoup(web_source.content.decode("gbk"), 'lxml')
            if soup.find(name="p"):
                self.save_data(soup.find(name="p").text,name)
            else:
                print("[warn] cannot find json comments ...")

            time.sleep(random.randint(8,20))

    def save_data(self,json_text,name):
        saved_path = os.path.join(self.download_path,name)
        save_file = os.path.join(saved_path,"{}.txt".format(int(time.time())))
        res = []
        if not os.path.exists(saved_path):
            os.mkdir(saved_path)
        try:
            json_comments = re.findall(r"[(](.*)[)]",json_text)[0]
            comments_dict = json.loads(json_comments)
            for comment in comments_dict['comments']:
                res.append(comment['content'])
            with open(save_file,"w",encoding="utf-8") as f:
                f.write("\n\n".join(res))
        except:
            print("[error ]re cannot match json comments ..")

    def run(self):
        product_count = len(self.products.keys()) - len(self.finish_list)
        idx = 1
        for key,name in self.products.items():
            if key in self.finish_list:continue

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
                          "productId={}&score=0&sortType=5&page=2&pageSize=10&isShadowSku=0&rid=0&fold=1"

    # 未获取product id
    spider = Spider(product_comment_url)

    # 已经拿到product id文件后
    # spider = Spider(product_comment_url,"products.json","finish.txt")

    spider.run()