
import pymysql

"""

CREATE TABLE `hot_search` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '热搜记录 ID',
  `article_id` INT NOT NULL COMMENT '文章 ID',
  `article_title` TEXT NOT NULL COMMENT '文章 标题',
  `create_time` int  COMMENT '创建时间',
  `hot_search_time` INT   COMMENT '上热搜时间',
  `duration` INT  COMMENT '持续时间',
  `tag_category` TEXT  COMMENT '标签（列表）对应tags表的id，用,分割',
  `heat_max` BIGINT COMMENT '最高热度',
  `heat_min` BIGINT COMMENT '最低热度',
  `heat_avg` BIGINT COMMENT '平均热度=heat_sum/version',
  `heat_sum` BIGINT COMMENT '总计热度',
  `answer_count` BIGINT  COMMENT '回答数量',
  `follow_count` BIGINT COMMENT '关注数',
  `view_count` BIGINT  COMMENT '浏览量',
  `dates` VARCHAR(100) NOT NULL COMMENT '日期',
  `version` INT COMMENT '爬取次数'
);

CREATE TABLE `tags` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '标签 ID',
  `tag_name` VARCHAR(255)  COMMENT '标签名称',
  `quantity` int
);
"""

import pymysql

host='localhost'
port=3306
user='root'
password='123456'
database='jd_spider'


class HotSearch:
    def __init__(self):
        """
        初始化数据库连接
        """
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        self.cursor = self.conn.cursor()

    def __del__(self):
        """
        关闭数据库连接
        """
        self.cursor.close()
        self.conn.close()

    def insert_batch(self, data_list):
        """
        批量插入数据
        """
        sql = """
        INSERT INTO hot_search (article_id, article_title, create_time, hot_search_time, duration, tag_category, heat_max, heat_min, heat_avg, heat_sum, answer_count, follow_count, view_count, dates, version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def delete(self, article_id):
        """
        根据文章 ID 删除数据
        """
        sql = """
        DELETE FROM hot_search WHERE article_id = %s
        """
        self.cursor.execute(sql, (article_id,))
        self.conn.commit()

    def update(self, article_id, duration, heat_max, heat_min, heat_avg, heat_sum, answer_count, follow_count, view_count, datetime_str, version):
        """
        根据文章 ID 修改数据
        """
        sql = """
        UPDATE hot_search SET duration = %s, heat_max = %s, heat_min = %s, heat_avg = %s, heat_sum = %s, answer_count = %s, follow_count = %s, view_count = %s, version = %s, dates = %s WHERE article_id = %s
        """
        self.cursor.execute(sql, (duration, heat_max, heat_min, heat_avg, heat_sum, answer_count, follow_count, view_count, version, datetime_str, article_id))
        self.conn.commit()

    def query_by_article_id(self, article_id):
        """
        根据文章 ID 查询数据
        """
        sql = """
        SELECT * FROM hot_search WHERE article_id = %s
        """
        self.cursor.execute(sql, (article_id,))
        return self.cursor.fetchone()


class Tags:
    def __init__(self):
        """
        初始化数据库连接
        """
        self.db = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset='utf8')
        self.cursor = self.db.cursor()

    def __del__(self):
        """
        关闭数据库连接
        """
        self.cursor.close()
        self.db.close()

    def insert(self, tag_name, quantity):
        """
        插入数据
        """
        sql = """
        INSERT INTO tags (tag_name, quantity)
        VALUES (%s, %s)
        """
        self.cursor.execute(sql, (tag_name, quantity))
        self.db.commit()

    def delete(self, tag_id):
        """
        根据标签 ID 删除数据
        """
        sql = """
        DELETE FROM tags WHERE id = %s
        """
        self.cursor.execute(sql, (tag_id,))
        self.db.commit()

    def update(self, tag_id, quantity):
        """
        根据标签 ID 修改数据
        """
        sql = """
        UPDATE tags SET quantity = %s WHERE id = %s
        """
        self.cursor.execute(sql, (quantity, tag_id))
        self.db.commit()

    def query_all(self):
        """
        查询所有数据
        """
        sql = """
        SELECT * FROM tags
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def query_by_id(self, tag_name):
        """
        根据标签 ID 查询数据
        """
        sql = """
        SELECT * FROM tags WHERE tag_name = %s
        """
        self.cursor.execute(sql, (tag_name,))
        return self.cursor.fetchone()
