import os
import time
while 1:
    a = os.system("python PhoneCommentSpider.py")
    # print(">>>>",a)
    # break
    # product_comment_url = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&" \
    #                       "productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1"
    #
    # # 未获取product id
    # # spider = Spider(product_comment_url)
    #
    # # 已经拿到product id文件后
    # spider = Spider(product_comment_url,"products.json", "brand_dict.json", "finish.txt")
    #

    # spider.run()
    time.sleep(60)