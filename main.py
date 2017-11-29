import os, sys
from scrapy.cmdline import execute

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

execute(['scrapy','crawl','redisJobSpider'])

