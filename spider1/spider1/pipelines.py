# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
import time
import os
import uuid
import hashlib
import logging
import traceback
from contextlib import closing
from urllib import urlopen

class Spider1Pipeline(object):
    def __init__(self):
        self.conn = mysql.connector.connect(user='root', password='mysql', host='localhost', port='3306', database='spider_zhipin', use_unicode=True)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        logging.info("........关闭数据库资源........")
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        logo_path = ''
        if item['company_logo']:
            logo_path = self.download_image('images', item['company_logo'], self.get_image_name(item['company_name']))

        try:
            self.cursor.execute("SELECT * FROM company WHERE name = '%s'" % (item['company_name']) + " OR short_name = '%s'" % (item['company_name']))
            company_info = self.cursor.fetchone()
            if company_info and len(company_info) > 0:
                company = company_info[0]
                self.cursor.execute("UPDATE company SET logo = '%s', welfare = '%s', size = '%s', financing_phase = '%s', website = '%s', legal_representative = '%s', business_status = '%s', updated_at = '%s' WHERE id = %s" % (
                    logo_path, item.get('company_welfare'), item.get('company_size'), item.get('financing_phase'), item.get('company_website'), item.get('legal_representative'), item['business_status'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), company)
                )
                self.conn.commit()
            else:
                self.cursor.execute("INSERT INTO company (name, short_name, logo, welfare, industry, size, financing_phase, website, legal_representative, registered_capital, founded_date, \
                 business_type, business_status, intro, registration_address, business_scope, created_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['company_name'], item['company_short_name'],
                   logo_path, item.get('company_welfare', ''), item.get('industry'), item.get('company_size'), item.get('financing_phase'), item.get('company_website', ''), item.get('legal_representative'), item.get('registered_capital'),
                   item['founded_date'], item['business_type'], item['business_status'], item.get('company_intro'), item.get('registration_address'), item.get('business_scope'), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ))
                company = self.cursor.getlastrowid()
                self.conn.commit()

            if company > 0:
                self.cursor.execute("SELECT * FROM jobs WHERE company = %s AND job_name = '%s'" % (company, item['job_name']))
                job_info = self.cursor.fetchone()
                if job_info and len(job_info) > 0:
                    self.cursor.execute("UPDATE jobs SET job_status = '%s', salary = '%s', work_address = '%s', gd_longitude = '%s', gd_latitude = '%s', work_years = '%s', degree = '%s', job_desc = '%s', recruiter = '%s', recruiter_position = '%s', updated_at = '%s' WHERE id = %s" % (
                        item['job_status'], item['salary'], item['work_address'], item.get('gd_longitude', 0), item.get('gd_latitude', 0), item['work_years'], item['degree'], item['job_desc'], item.get('recruiter'), item.get('recruiter_position'), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), job_info[0])
                    )
                    self.conn.commit()
                else:
                    self.cursor.execute("INSERT INTO jobs (company, job_name, job_status, salary, work_address, gd_longitude, gd_latitude, work_years, degree, job_desc, recruiter, recruiter_position, created_at) VALUES(%s, %s, \
                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (company, item['job_name'], item['job_status'], item['salary'], item['work_address'], item.get('gd_longitude', 0), item.get('gd_latitude', 0), item['work_years'],
                        item['degree'], item['job_desc'],item.get('recruiter'), item.get('recruiter_position'), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    ))
                    self.conn.commit()
            else:
                logging.info("公司名称:",item['company_short_name'] + "添加失败")
        except Exception:
            logging.exception(str(traceback.format_exc()))

    def download_image(self, dirName, image_url, default_image_name = ""):
        try:
            if not os.path.exists('../' + dirName):
                os.mkdir('../' + dirName)

            if image_url.find('?') > -1:
                arr = image_url.split('?')
                image_url = arr[0]

            image_arr = image_url.split('.')
            if len(image_arr) > 1:
                extension = image_arr[len(image_arr) - 1]
            else:
                extension = 'png'

            if default_image_name:
                image_name = default_image_name + '.' + extension
            else:
                image_name = str(uuid.uuid1()) + '.' + extension

            image_path = "../" + dirName + "/" + image_name

            with closing(urlopen(image_url)) as result:
                data = result.read()
                with open(image_path, 'wb+') as f:
                    f.write(data)

            return image_name
        except OSError:
            logging.info(dirName + "目录创建失败")
        except:
            logging.info("下载图片" + image_url + "出现错误")

        return

    def get_image_name(self, name):
        h = hashlib.md5()
        h.update(name.encode('utf-8'))
        return h.hexdigest()