# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
from redis_spider.models.es_item import es_JobType

class JobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def get_city(addr):
    addr = addr.strip("\n").strip(" ").strip("-").split("-")[0].strip(" ")
    return addr


def get_publish_time(value):
    if ":" in value:
        return datetime.datetime.now().strftime("%Y/%m/%d")

    match_obj = re.match(r"(\d+)天前.*",value)
    if match_obj:
        return (datetime.datetime.now() + datetime.timedelta(days=-int(match_obj.group(1)))).strftime("%Y/%m/%d")

    match_obj = re.match(r"(\d+)-(\d+)-(\d+).*", value)
    if match_obj:
        return "/".join([match_obj.group(1), match_obj.group(2), match_obj.group(3)])


def get_max_salary(value):
    match_obj = re.match(r"(\d+)[kK]-(\d+)[kK]", value)
    if match_obj:
        return match_obj.group(2)


def get_min_salary(value):
    match_obj = re.match(r"(\d+)[kK]-(\d+)[kK]", value)
    if match_obj:
        return match_obj.group(1)


def get_degree(value):
    if "大专" in value:
        return "大专"
    elif "本科" in value:
        return "本科"
    elif "硕士" in value:
        return "硕士"
    elif "博士" in value:
        return "博士"
    return "不限"


def get_exp(value):
    if "应届毕业生" in value:
        return "应届毕业生"

    pattern = r".*?经验((\d+-\d+)|(\d+))年.*"
    match_obj = re.match(pattern, value, re.DOTALL)
    if match_obj:
        return match_obj.group(1)

    return "不限"


def get_type(value):
    return value.strip("\n").strip(" ").split("\n")[0]

from elasticsearch_dsl.connections import connections
es = connections.create_connection(hosts=['localhost'])


def gen_suggestion(index, word_tuple):
    user_set = set()
    suggestions = []
    for word,weight in word_tuple:
        if word:
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter":["lowercase"]}, body=word)
            analyzed_word = set([r["token"] for r in words["tokens"] if len(r['token'])>1])
            new_work = analyzed_word - user_set
        else:
            new_work = set()
        if new_work:
            suggestions.append({"input":list(new_work),"weight":weight})

    return suggestions

# CREATE TABLE `job` (
#   `id` int(11) NOT NULL,
#   `object_id` char(32) NOT NULL,
#   `job_name` varchar(100) NOT NULL,
#   `company_name` varchar(40) NOT NULL,
#   `min_salary` int(11) NOT NULL,
#   `max_salary` int(11) NOT NULL,
#   `publish_time` date NOT NULL,
#   `crawl_time` date NOT NULL,
#   `city` varchar(32) NOT NULL,
#   `content` text NOT NULL,
#   `url` varchar(200) NOT NULL,
#   `exp` varchar(10) NOT NULL,
#   `degree` varchar(10) NOT NULL,
#   `company_type` varchar(30) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
#
# ALTER TABLE `job`
#   ADD PRIMARY KEY (`id`),
#   ADD UNIQUE KEY `object_id` (`object_id`);
#
# ALTER TABLE `job`
#   MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

class JobItem(scrapy.Item):
    job_name = scrapy.Field()
    min_salary = scrapy.Field(input_processor=MapCompose(get_min_salary))
    max_salary = scrapy.Field(input_processor=MapCompose(get_max_salary))
    url = scrapy.Field()
    object_id = scrapy.Field()
    city = scrapy.Field(input_processor=MapCompose(remove_tags, get_city))
    company_name = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(get_publish_time))
    crawl_time = scrapy.Field()
    exp = scrapy.Field(input_processor=MapCompose(remove_tags, get_exp))
    degree = scrapy.Field(input_processor=MapCompose(remove_tags, get_degree))
    company_type = scrapy.Field(input_processor=MapCompose(remove_tags,get_type))

    def get_insert_sql(self):
        sql = """
            INSERT INTO `job`(`object_id`, `job_name`, `company_name`, `min_salary`, `max_salary`, `publish_time`, `crawl_time`, `city`, `content`, `url`
            , `exp`, `degree`, `company_type`)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE crawl_time=VALUES(crawl_time),publish_time=VALUES(publish_time)
        """

        params = (self['object_id'], self['job_name'], self['company_name'],
                  self['min_salary'], self['max_salary'], self['publish_time'],
                  self['crawl_time'], self['city'], self['content'],
                  self['url'], self['exp'], self['degree'],
                  self['company_type'])

        return sql, params

    def save_to_es(self):
        item = es_JobType()
        item.job_name = self['job_name']
        item.meta.id = self['object_id']
        item.company_name = self['company_name']
        item.min_salary = self['min_salary']
        item.max_salary = self['max_salary']
        item.publish_time = self['publish_time']
        item.crawl_time = self['crawl_time']
        item.city = self['city']
        item.content = remove_tags(self['content'])
        item.url = self['url']
        item.exp = self['exp']
        item.degree = self['degree']
        item.company_type = self['company_type']

        item.suggest = gen_suggestion(index="lagou", word_tuple=((item.job_name,10),(item.company_type,8)))
        item.save()