import pymysql

"""

CREATE TABLE `hot_search` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '热搜记录 ID',
  `article_id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '文章 ID',
  `author_id` INT  COMMENT '作者 ID',
  `author_name` VARCHAR(255)  COMMENT '作者姓名',
  `article_title` text   COMMENT '文章标题',
  `follow_count` INT  COMMENT '关注数量',
  `answer_count` INT  COMMENT '回答数',
  `like_count` INT  COMMENT '点赞数',
  `view_count` INT  COMMENT '浏览量',
  `duration` INT  COMMENT '持续时间',
  `tag_category` text  COMMENT '标签分类（多个）', # 为一个list关联tags表
  `heat` INT  COMMENT '热度',
  `status` TINYINT  DEFAULT 0 COMMENT '状态',
  `date` DATE  COMMENT '日期'
);

CREATE TABLE `tags` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '热搜记录 ID',
  `tag_name` VARCHAR(255)  COMMENT '标签名称',
  `quantity` int,
);
"""


import pymysql

class HotSearch:
    def __init__(self, host, username, password, database, port):
        """
        初始化数据库连接
        """
        self.db = pymysql.connect(host, username, password, database, port, charset='utf8')
        self.cursor = self.db.cursor()

    def __del__(self):
        """
        关闭数据库连接
        """
        self.cursor.close()
        self.db.close()

    def insert(self, author_id, author_name, article_title, follow_count, answer_count, like_count, view_count, duration, tag_category, heat, date):
        """
        插入数据
        """
        sql = """
        INSERT INTO hot_search (author_id, author_name, article_title, follow_count, answer_count, like_count, view_count, duration, tag_category, heat, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (author_id, author_name, article_title, follow_count, answer_count, like_count, view_count, duration, tag_category, heat, date))
        self.db.commit()

    def delete(self, id):
        """
        删除数据
        """
        sql = """
        DELETE FROM hot_search WHERE id = %s
        """
        self.cursor.execute(sql, (id,))
        self.db.commit()

    def update(self, article_id, author_id, author_name, article_title, follow_count, answer_count, like_count, view_count, duration, tag_category, heat, date):
        """
        更新数据
        """
        sql = """
        UPDATE hot_search SET author_id = %s, author_name = %s, article_title = %s, follow_count = %s, answer_count = %s, like_count = %s, view_count = %s, duration = %s, tag_category = %s, heat = %s, date = %s WHERE article_id = %s
        """
        self.cursor.execute(sql, (author_id, author_name, article_title, follow_count, answer_count, like_count, view_count, duration, tag_category, heat, date, article_id))
        self.db.commit()

    def query_one(self, article_id):
        """
        查询单条数据
        """
        sql = """
        SELECT * FROM hot_search WHERE article_id = %s
        """
        self.cursor.execute(sql, (article_id,))
        return self.cursor.fetchone()

    def query_all(self):
        """
        查询所有数据
        """
        sql = """
        SELECT * FROM hot_search
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

