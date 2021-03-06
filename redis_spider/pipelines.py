# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class RedisSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )

        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):

        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        # return item

    def handle_error(self, failure, item, spider):
        print(failure)
        print("insert error %s" %(item["url"]))

    def do_insert(self,cursor,item):
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,params)


class esPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item