# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Spider1Item(scrapy.Item):
    #工作名称
    job_name = scrapy.Field()
    #薪资
    salary = scrapy.Field()
    #职位状态
    job_status = scrapy.Field()
    #工作地点
    work_address = scrapy.Field()
    # 工作地点在高德地图上的经度
    gd_longitude = scrapy.Field()
    # 工作地点在高德地图上的纬度
    gd_latitude = scrapy.Field()
    #工作年限
    work_years = scrapy.Field()
    #学历要求
    degree = scrapy.Field()
    # 工作描述
    job_desc = scrapy.Field()
    #招聘人
    recruiter = scrapy.Field()
    #招聘人职位
    recruiter_position = scrapy.Field()
    #招聘公司
    company_name = scrapy.Field()
    #招聘公司别名
    company_short_name = scrapy.Field()
    #公司logo
    company_logo = scrapy.Field()
    #公司福利
    company_welfare = scrapy.Field()
    #行业
    industry = scrapy.Field()
    #公司规模
    company_size = scrapy.Field()
    #融资阶段
    financing_phase = scrapy.Field()
    #公司官网
    company_website = scrapy.Field()
    #公司介绍
    company_intro = scrapy.Field()
    #成立时间
    founded_date = scrapy.Field()
    #企业类型
    business_type = scrapy.Field()
    #经营状态
    business_status = scrapy.Field()
    #注册地址
    registration_address = scrapy.Field()
    #注册资金
    registered_capital = scrapy.Field()
    #经营范围
    business_scope = scrapy.Field()
    #法人代表
    legal_representative = scrapy.Field()
