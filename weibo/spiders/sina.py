# -*- coding: utf-8 -*-
import scrapy
import re
from lxml import etree
from weibo.items import WeiboItem,FailUrlItem
import logging
from weibo.login import Login


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['www.weibo.com']
    start_urls = ['https://weibo.com/6431467469/follow']

    #模拟登录，获取有效cookie
    def start_requests(self):
        start_url = 'https://weibo.com/6431467469/follow'
        #实例化一个登录器
        loginer = Login()
        #获取cookie
        self.cookie = loginer.AutoLogin()
        #设置请求头
        self.headers ={'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        #设置深度
        depth = 1
        #设置失败次数
        fail_count = 0
        #请求我的关注者页
        return [scrapy.Request(start_url,callback=self.parse,method='GET',headers=self.headers,cookies=self.cookie,dont_filter=True,meta={'depth':depth,'url':start_url,'fail_count':fail_count})]

    #将数据解析成HTML
    def dataToHtml(self,data):
        html_li = re.findall(r'"html":(".*?")}', data)
        html_sum = ''
        for html in html_li:
            html_sum += html
        html_sum = re.sub(r'(\\|\\n|\\r|\\t)', '', html_sum)
        html_etree = etree.HTML(html_sum)
        return html_etree

    #解析我的关注者页，并衍生请求次级关注者页
    def parse(self, response):
        depth = response.meta['depth']
        fail_count = response.meta['fail_count']
        responseUrl = response.url
        requestUrl = response.meta['url']
        #判断请求网页与返回网页的url一致性，不一样则重新请求
        if not str(responseUrl).__eq__(requestUrl):
            #判断失败次数，超过两次放弃
            if fail_count <= 1:
                fail_count += 1
                yield scrapy.Request(requestUrl,callback=self.parse,method='GET',dont_filter=True,meta={'depth':depth,'url':requestUrl,'fail_count':fail_count},headers=self.headers,cookies=self.cookie)
            else:
                #记录请求失败的网页
                item = FailUrlItem()
                item['fail_url'] = requestUrl
                yield item
        else:
            item = WeiboItem()
            data = response.body.decode()
            html_etree = self.dataToHtml(data)
            item['focus_by'] = html_etree.xpath('//h1/text()')[0]
            focus_li = html_etree.xpath('//div[@class="title W_fb W_autocut "]')
            for focus in focus_li:
                item['name'] = focus.xpath('.//a/text()')[0]
                focus_url = focus.xpath('.//a[@class="S_txt1"]/@href')
                item['url'] = 'https://weibo.com' + focus_url[0].split('?')[0]
                item['fans_num'] = 10000000
                url = item['url'] + '/follow?from=page_100306&wvr=6&mod=headfollow'
                yield item
                yield scrapy.Request(url,callback=self.parse_focus_list,method='GET',dont_filter=True,meta={'depth':depth,'url':url,'fail_count':fail_count},headers=self.headers,cookies=self.cookie)

    #解析关注者列表页
    def parse_focus_list(self,response):
        depth = response.meta['depth']
        fail_count = response.meta['fail_count']
        #判断是否被重定向，如果是，重新请求
        responseUrl = response.url
        requestUrl = response.meta['url']
        if not str(responseUrl).__eq__(requestUrl):
            #判断失败次数，超过三次放弃
            if fail_count < 1:
                fail_count += 1
                yield scrapy.Request(requestUrl,callback=self.parse_focus_list,method='GET',dont_filter=True,meta={'depth':depth,'url':requestUrl,'fail_count':fail_count},headers=self.headers,cookies=self.cookie)
            else:
                #记录请求失败的网页url
                item = FailUrlItem()
                item['fail_url'] = requestUrl
                yield item
        else:
            item = WeiboItem()
            data = response.body.decode()
            html_etree = self.dataToHtml(data)
            item['focus_by'] = html_etree.xpath('//h1/text()')[0]
            #获取关注者列表
            focus_list = html_etree.xpath('//li[@class="follow_item S_line2"]')
            for focus in focus_list:
                try:
                    focus_info = focus.xpath('.//dt[@class="mod_pic"]/a')[0]
                    item['name'] = focus_info.xpath('./@title')[0]
                    item['url'] = 'https://weibo.com' + focus_info.xpath('./@href')[0].split('?')[0]
                    item['fans_num'] = int(focus.xpath('.//span[@class="conn_type W_vline S_line1"]//a/text()')[0])
                    yield item
                    dep = depth
                    #判断深度
                    if dep <= 3:
                        dep += 1
                        print(item['url'])
                        url = item['url'] + '/follow?from=page_100306&wvr=6&mod=headfollow'
                        yield scrapy.Request(url,callback=self.parse_focus_list,method='GET',dont_filter=True,meta={'depth':dep,'url':url,'fail_count':fail_count},headers=self.headers,cookies=self.cookie)
                    else:
                        print('不再继续挖掘了')
                except Exception as e:
                    logging.error('解析关注者列表页出错')
            #尝试获取下一页的关注者
            try:
                page_next_url = html_etree.xpath('//a[@class="page next S_txt1 S_line1"]/@href')[0]
                page_next_url = 'https://weibo.com' + page_next_url
                yield scrapy.Request(page_next_url,callback=self.parse_focus_list,method='GET',meta={'depth':depth,'url':page_next_url,'fail_count':fail_count},headers=self.headers,cookies=self.cookie)
            except Exception as e:
                pass









