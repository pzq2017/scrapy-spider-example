# -*- coding: utf-8 -*-
import scrapy
import logging
from spider1.items import Spider1Item

class FindWorkSpider(scrapy.Spider):
    #定义该Spider的名字
    name = 'find_work'
    #定义该Spider允许爬取的域名
    allowed_domains = ['zhipin.com']
    #定义该Spider爬取的首页链接
    start_urls = ['https://www.zhipin.com/c101280100/h_101280100/']
    #定义爬虫对应的管道
    custom_settings = {
        'ITEM_PIPELINES' : {
            'spider1.pipelines.Spider1Pipeline': 300
        }
    }

    #response代表下载器从start_urls中每个URL下载得到的响应
    def parse(self, response):
        for job_primary in response.xpath('//div[@class="job-primary"]'):
            item = Spider1Item()
            info_primary = job_primary.xpath('./div[@class="info-primary"]')

            item['job_name'] = info_primary.xpath('./h3/a/div[@class="job-title"]/text()').extract_first()
            item['salary'] = info_primary.xpath('./h3/a/span[@class="red"]/text()').extract_first()

            work_requirement = info_primary.xpath('./p/text()').extract()
            if work_requirement and len(work_requirement) > 1:
                item['work_years'] = work_requirement[1]
            if work_requirement and len(work_requirement) > 2:
                item['degree'] = work_requirement[2]

            detail_url = 'https://www.zhipin.com' + info_primary.xpath('./h3/a/@href').extract_first()

            company_text = job_primary.xpath('./div[@class="info-company"]/div[@class="company-text"]')
            item['company_short_name'] = company_text.xpath('./h3/a/text()').extract_first()
            company_info = company_text.xpath('./p/text()').extract()
            if company_info and len(company_info) > 0:
                item['industry'] = company_info[0]
            if company_info and len(company_info) == 1:
                item['company_size'] = company_info[1]
            if company_info and len(company_info) > 1:
                item['financing_phase'] = company_info[1]
            if company_info and len(company_info) > 2:
                item['company_size'] = company_info[2]

            info_publish = job_primary.xpath('./div[@class="info-publis"]')
            info_recruiter = info_publish.xpath('./h3/text()').extract()
            if info_recruiter and len(info_recruiter) > 0:
                item['recruiter'] = info_recruiter[0]
            if info_recruiter and len(info_recruiter) > 1:
                item['recruiter_position'] = info_recruiter[1]

            #爬取详情页信息
            logging.info(item['company_short_name'] + detail_url)
            yield scrapy.Request(url = detail_url, callback = self.parse_detail, meta={'data': item}, dont_filter=True)

        #爬取下一页信息
        # next_page_links = response.xpath('//div[@class="page"]/a[@ka="page-next"]/@href').extract()
        # if next_page_links and len(next_page_links) > 0:
        #     yield scrapy.Request(url='https://www.zhipin.com' + next_page_links[0], callback=self.parse)

    def parse_detail(self, response):
        item = response.meta['data']

        item['job_status'] = response.xpath('//div[@class="job-status"]/text()').extract_first()
        if not item['job_status']:
            print response.url
            return

        return
        company_welfare = response.xpath('//div[@class="tag-all job-tags"]/span/text()').extract()

        if len(company_welfare) < 1:
            company_welfare = response.xpath('//div[@class="job-tags"]/span/text()').extract()
        if len(company_welfare) > 0:
            item['company_welfare'] = ','.join(list(set(company_welfare)))

        content = response.xpath('//div[@class="detail-content"]')
        job_desc = content.xpath('./div[@class="job-sec"]/div[@class="text"]/text()').extract()
        item['job_desc'] = ('<br>'.join(job_desc)).strip()

        item['company_name'] = content.xpath('./div[@class="job-sec"]/div[@class="name"]/text()').extract_first()
        if not item['company_name']:
            item['company_name'] = item['company_short_name']

        level_list = content.xpath('./div[@class="job-sec"]/div[@class="level-list"]')
        for level_selector in level_list.xpath('./li'):
            if (level_selector.xpath('./span/text()').extract_first()).strip() == '法人代表：'.decode('utf-8'):
                item['legal_representative'] = level_selector.xpath('./text()').extract_first()
            if (level_selector.xpath('./span/text()').extract_first()).strip() == '注册资金：'.decode('utf-8'):
                item['registered_capital'] = level_selector.xpath('./text()').extract_first()

        item['founded_date'] = level_list.xpath('./li[@class="res-time"]/text()').extract_first()
        item['business_type'] = level_list.xpath('./li[@class="company-type"]/text()').extract_first()
        item['business_status'] = level_list.xpath('./li[@class="manage-state"]/text()').extract_first()

        item['work_address'] = content.xpath('./div[@class="job-sec"]/div[@class="job-location"]/div[@class="location-address"]/text()').extract_first()

        map_link = content.xpath('./div[@class="job-sec"]/div[@class="job-location"]/div[@class="job-location-map js-open-map"]/img/@src').extract_first()
        if map_link:
            map_args = map_link.split(',')
            if len(map_args) == 4:
                item['gd_longitude'] = int(float((map_args[2].split(':'))[1]) * 1000000)
                item['gd_latitude'] = int(float((map_args[3].split('&'))[0]) * 1000000)

        company_info = response.xpath('//div[@class="sider-company"]')
        item['company_logo'] = company_info.xpath('./div/a[@ka="job-detail-company-logo_custompage"]/img/@src').extract_first()

        item['company_website'] = company_info.xpath('./p/i[@class="icon-net"]/../text()').extract_first()

        company_detail_url = content.xpath('./div[@class="job-sec"]/a[@ka="job-cominfo"]/@href').extract_first()
        if company_detail_url:
            company_detail_url = 'https://www.zhipin.com' + company_detail_url
            yield scrapy.Request(url=company_detail_url, callback=self.parse_company_detail, meta={'data':item}, dont_filter=True)
        else:
            yield item


    def parse_company_detail(self, response):
        item = response.meta['data']

        content = response.xpath('//div[@class="detail-content"]')

        item['company_intro'] = content.xpath('./div[@class="job-sec"]/div[@class="text fold-text"]/text()').extract_first()

        business_detail = content.xpath('./div[@class="job-sec company-business"]/div[@class="business-detail"]/ul')
        for li in business_detail.xpath('./li'):
            if (li.xpath('./span/text()').extract_first()).strip() == '注册地址：'.decode('utf-8'):
                item['registration_address'] = li.xpath('./text()').extract_first()
            if (li.xpath('./span/text()').extract_first()).strip() == '经营范围：'.decode('utf-8'):
                item['business_scope'] = li.xpath('./text()').extract_first()

        yield item