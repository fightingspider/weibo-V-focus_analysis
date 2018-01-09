# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from weibo.items import WeiboItem,FailUrlItem

class WeiboPipeline(object):
    def open_spider(self,spider):
        self.client = pymongo.MongoClient('127.0.0.1',27017)
        self.weibo = self.client['weibo']['focus']
        self.fail = self.client['weibo']['fail']

    def process_item(self, item, spider):
        if isinstance(item,WeiboItem):
            data = {
                'name':item['name'],
                'url':item['url'],
                'focus_by':item['focus_by'],
                'fans_num':item['fans_num']
            }
            self.weibo.insert_one(data)
            return item
        else:
            data = {'fail_url':item['fail_url']}
            self.fail.insert_one(data)
            return item

    def close_spider(self,spider):
        pass
