# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
from datetime import datetime


class JobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def get_city(addr):
    addr = addr.strip("\n").strip(" ").split("-")[0].strip(" ")
    return addr


def get_publish_time(value):
    if ":" in value:
        return datetime.now().strftime("%Y/%m/%d")

    match_obj = re.match(r"(\d+)天前.*",value)
    if match_obj:
        return datetime.datetime.now() + datetime.timedelta(days=-match_obj.group(1))

    match_obj = re.match(r"(\d+)-(\d+)-(\d+).*", value)
    if match_obj:
        return "/".join([match_obj.group(1), match_obj.group(2), match_obj.group(3)])


def get_max_salary(value):
    match_obj = re.match(r"(\d+)[kK]-(\d+)[kK]", value)
    if match_obj:
        return match_obj.group(2)


def get_min_salary(value):
    match_obj = re.match(r"(\d+)k-(\d+)k", value)
    if match_obj:
        return match_obj.group(1)


# CREATE TABLE IF NOT EXISTS `job` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
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
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `object_id` (`object_id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
class JobItem(scrapy.Item):
    job_name = scrapy.Field()
    min_salary = scrapy.Field(input_processor=MapCompose(get_min_salary))
    max_salary = scrapy.Field(input_processor=MapCompose(get_max_salary))
    url = scrapy.Field()
    object_id = scrapy.Field()
    city = scrapy.Field(input_processor=MapCompose(remove_tags,get_city))
    company_name = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(get_publish_time))
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        sql = """
            INSERT INTO `job`(`object_id`, `job_name`, `company_name`, `min_salary`, `max_salary`, `publish_time`, `crawl_time`, `city`, `content`, `url`)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE crawl_time=VALUES(crawl_time),publish_time=VALUES(publish_time)
        """
