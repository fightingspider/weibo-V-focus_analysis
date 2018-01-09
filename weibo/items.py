# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    focus_by = scrapy.Field()  # 该微博主的粉丝粉丝
    name = scrapy.Field() #微博主名字
    url = scrapy.Field()  #微博主url
    fans_num = scrapy.Field() #粉丝数量，100万以上为大V，也是本次研究对象

class FailUrlItem(scrapy.Item):
    fail_url = scrapy.Field() #记录请求失败的url




