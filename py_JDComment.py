import pymysql

"""
CREATE TABLE `jd_comment` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `brand` text COMMENT '品牌',
  `product_name` text COMMENT '商品名称',
  `product_id` bigint(20) unsigned COMMENT '商品ID',
  `content` text COMMENT '评论内容',
  `append_content` int(11) unsigned DEFAULT 0 COMMENT '追评 0 表示未追评，1表示追评价',
  `seller_reply` int(11) unsigned DEFAULT 0 COMMENT '商家回复，0表示未回复，1表示已回复',
  `score` tinyint(4) unsigned COMMENT '评分',
  `is_good` tinyint(4) unsigned DEFAULT 0 COMMENT '是否好评，0表示不是，1表示是',
  `image_count` tinyint(4) unsigned DEFAULT 0 COMMENT '图片数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='京东商品评论表';



# CREATE TABLE `product` (
#   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
#   `product_id` int(11) unsigned COMMENT '商品ID',
#   `sales_volume` int(11) unsigned DEFAULT 0 COMMENT '销售量',
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';
"""

import pymysql
host='localhost'
port=3306
user='root'
password='123456'
database='jd_spider'

class JDComment:
    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

        # 创建游标
        self.cursor = self.conn.cursor()

    def insert_comment(self, data):
        """
        新增评论

        Args:
            product_id: 商品ID
            user_id: 用户ID
            content: 评论内容
            score: 评分
            image_count: 图片数量

        Returns:
            None
        """
        # 批量插入数据
        sql = """
        INSERT INTO `jd_comment` (`brand`, `product_name`, `product_id`,  `content`, `append_content`,  `seller_reply`, `score`, `is_good`, `image_count`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(sql, data)

        # self.cursor.execute(sql, (product_id, user_id, content, score, image_count))
        self.conn.commit()

    def delete_comment(self, id):
        """
        删除评论

        Args:
            id: 评论ID

        Returns:
            None
        """
        sql = """
        DELETE FROM `jd_comment` WHERE `id` = %s
        """
        self.cursor.execute(sql, (id,))
        self.conn.commit()

    def update_comment(self, id, content, score, image_count):
        """
        修改评论

        Args:
            id: 评论ID
            content: 评论内容
            score: 评分
            image_count: 图片数量

        Returns:
            None
        """
        sql = """
        UPDATE `jd_comment` SET `content` = %s, `score` = %s, `image_count` = %s WHERE `id` = %s
        """
        self.cursor.execute(sql, (content, score, image_count, id))
        self.conn.commit()

    def select_all_comments(self):
        """
        查询所有评论

        Args:
            None

        Returns:
            评论列表
        """
        sql = """
        SELECT * FROM `jd_comment`
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def select_comments_by_product_id(self, product_id):
        """
        查询某个商品的评论

        Args:
            product_id: 商品ID

        Returns:
            评论列表
        """
        sql = """
        SELECT * FROM `jd_comment` WHERE `product_id` = %s
        """
        self.cursor.execute(sql, (product_id,))
        return self.cursor.fetchall()

    def select_comments_by_user_id(self, user_id):
        """
        查询某个用户的评论

        Args:
            user_id: 用户ID

        Returns:
            评论列表
        """
        sql = """
        SELECT * FROM `jd_comment` WHERE `user_id` = %s
        """
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def select_good_comments_by_product_id(self, product_id):
        """
        查询某个商品的好评

        Args:
            product_id: 商品ID

        Returns:
            评论列表
        """
        sql = """
        SELECT * FROM `jd_comment` WHERE `product_id` = %s AND `is_good` = 1
        """
        self.cursor.execute(sql, (product_id,))
        return self.cursor.fetchall()

    def select_bad_comments_by_product_id(self, product_id):
        """
        查询某个商品的差评

        Args:
            product_id: 商品ID

        Returns:
            评论列表
        """
        sql = """
        SELECT * FROM `jd_comment` WHERE `product_id` = %s AND `is_bad` = 1
        """
        self.cursor.execute(sql, (product_id,))
        return self.cursor.fetchall()

    def close(self):
        """
        关闭游标和连接"""
        self.cursor.close()
        self.conn.close()



