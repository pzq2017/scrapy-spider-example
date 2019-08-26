# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from contextlib import closing
from urllib import urlopen
import random
import json
import time
import mysql.connector


class Spider1SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Spider1DownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomProxyMiddleware(object):
    def __init__(self):
        self.conn = mysql.connector.connect(user='root', password='mysql', host='localhost', port='3306', database='spider_zhipin', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://" + self.get_random_proxy()

    def get_random_proxy(self):
        avaliableIp = ""

        self.cursor.execute("SELECT * FROM proxy_ips WHERE expire_time > %d" % (int(time.time())) + " ORDER BY RAND(), id DESC LIMIT 1")
        proxy_ip = self.cursor.fetchone()
        if not proxy_ip:
            proxy_ip = self.save_proxy_ips()
            if proxy_ip:
                avaliableIp = proxy_ip.get('ip') + ":" + str(proxy_ip.get('port'))
        else:
            avaliableIp = proxy_ip[1] + ":" + str(proxy_ip[2])

        return avaliableIp

    def save_proxy_ips(self):
        avaliableIp = ""
        self.cursor.execute("TRUNCATE proxy_ips;")
        with closing(urlopen('http://api.xedl.321194.com/getip?num=20&type=2&port=1&pack=4217&ts=1&cs=1&lb=1')) as result:
            proxyIpsData = json.loads(result.read())
            proxyIps = proxyIpsData['data']
            for proxyIp in proxyIps:
                if not avaliableIp:
                    avaliableIp = proxyIp

                self.cursor.execute("INSERT INTO proxy_ips (ip, port, created_time, expire_time) VALUES(%s, %s, %s, %s)",
                    (proxyIp.get('ip'), proxyIp.get('port'), self.get_timestamp(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())), self.get_timestamp(proxyIp.get('expire_time')))
                )
                self.conn.commit()

        return avaliableIp

    def spider_opened(self, spider):
        self.cursor.close()
        self.conn.close()

    def get_timestamp(self, datetime):
        timeArray = time.strptime(datetime, '%Y-%m-%d %H:%M:%S')
        return int(time.mktime(timeArray))