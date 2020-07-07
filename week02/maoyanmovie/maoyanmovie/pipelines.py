# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from itemadapter import ItemAdapter


class MaoyanmoviePipeline:
    def process_item(self, item, spider):
        title = item['title']
        genre = ' '.join(item['genre'])
        date = item['date']

        sql = "insert into maoyanmovie values (%s,%s,%s)"

        conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            password = '980419',
            database = 'test',
            charset = 'utf8mb4'
        )
        
         # 获得cursor游标对象
        cur = conn.cursor()
        try:
            print(cur.excute(sql, [title, genre, date]))
            # 关闭游标
            cur.close()
            conn.commit()
        except:
            conn.rollback()
        # 关闭数据库连接
        conn.close()
        
        return item
