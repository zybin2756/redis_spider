# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from redis_spider.items import JobItem,JobItemLoader
from datetime import datetime
from redis_spider.utils.common import get_md5


class RedisjobspiderSpider(RedisCrawlSpider):
    name = 'redisJobSpider'
    allowed_domains = ['www.lagou.com']
    # start_urls = ['https://www.lagou.com/']

    custom_settings = {
        "COOKIES_ENABLED": False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': '_ga=GA1.2.1959704847.1510409980; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1510409981,1510490677,1511357128; user_trace_token=20171111221935-5833c389-c6eb-11e7-8960-525400f775ce; LGUID=20171111221935-5833c92e-c6eb-11e7-8960-525400f775ce; index_location_city=%E5%B9%BF%E5%B7%9E; JSESSIONID=ABAAABAAAIAACBI07E6E73E2CB2CA37CC323D6C00FB3F6C; SEARCH_ID=07d9d0bab5f24578a4dcd5dd4f45791e; LGSID=20171122212522-97928ad6-cf88-11e7-999b-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2FJava%2F; LGRID=20171122214001-a3ace9f8-cf8a-11e7-9e98-525400f775ce; _gid=GA1.2.1998323372.1511357128; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1511358005; X_HTTP_TOKEN=f2aca44c116a2e4ea03860285ddca5a8; _putrc=""; login=false; unick=""; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=4; TG-TRACK-CODE=index_navigation; X_MIDDLE_TOKEN=5c1b9a7f88dcba141a6146610f5f55db; _gat=1',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
    }
    rules = (
        Rule(LinkExtractor(allow=r'.*?gongsi/\d+\.html'), follow=True),
        Rule(LinkExtractor(allow=r'.*?zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'.*?jobs/\d+.html'), callback='parse_job', follow=True),

    )

    def parse_job(self, response):
        outline = response.css(".outline_tag::text").extract()
        if len(outline) == 0:
            itemLoader = JobItemLoader(item=JobItem(), response=response)
            itemLoader.add_css("job_name", ".job-name::attr(title)")
            itemLoader.add_css("company_name", "#job_company dt a img::attr(alt)")
            itemLoader.add_css("min_salary", ".salary::text")
            itemLoader.add_css("max_salary", ".salary::text")
            itemLoader.add_css("publish_time", ".publish_time::text")
            itemLoader.add_value("crawl_time", datetime.now().strftime("%Y/%m/%d"))
            itemLoader.add_css("city", ".work_addr")
            itemLoader.add_css("content", ".content_l.fl")
            itemLoader.add_value("url", response.url)
            itemLoader.add_value("object_id", get_md5(response.url))
            itemLoader.add_css("exp", ".job_request")
            itemLoader.add_css("degree",".job_request")
            itemLoader.add_css("company_type", ".c_feature > li:nth-child(1)")
            item = itemLoader.load_item()
            yield item
