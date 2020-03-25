#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

from selenium import webdriver
from bs4 import BeautifulSoup

import sys
import time
import json
import redis
import sqlite3
import traceback

BASE_URL = "https://play.google.com"


class GooglePlayCrawler(object):
    def __init__(self, gl=''):
        self.gl = gl
        db_name = "apps.db"
        # if len(gl) > 0:
        # db_name = "%s.db" % gl

        # self.sql = sqlite3.connect('apps.db')
        self.sql = sqlite3.connect(db_name)
        self.redis = redis.Redis(host='localhost', port=6379)

    def close(self):
        self.sql.close()
        self.redis.close()

    def get_driver(self):
        # 初始化chrome driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        # disable image loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        # chrome_options.add_argument('--proxy-server=socks5://hk.vpn.umlife.net:18500')

        return webdriver.Chrome(chrome_options=chrome_options)

    def get(self, url, scroll=True):
        content = ""

        try:
            driver = self.get_driver()

            driver.get(url)
            SCROLL_PAUSE_TIME = 5

            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True and scroll:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            content = driver.page_source.encode('utf-8')

        except:
            print(traceback.format_exc())

        driver.close()

        return content

    def get_more_links(self):
        content = self.get(BASE_URL + "/store/apps?gl=" + self.gl)
        soup = BeautifulSoup(content, "html.parser")

        # 第一个链接是新应用
        more_links = soup.select("a.id-track-click")

        return more_links

    def get_app_info(self, app_div):
        app = {}
        try:
            app_link = app_div.select("c-wiz > div > div > div > div > div > a")[0]
            href = app_link.attrs.get("href")
            target = BASE_URL + href
            print("app_target: ", target)

            # 获取app名称和developer名称
            names = app_div.select("c-wiz > div > div > div:nth-child(2) > div > div > div > div > div > div")
            app_name = names[0].select("a > div:nth-child(1)")[0].text
            developer_name = names[1].select("a > div:nth-child(1)")[0].text

            # 看数据库里面有没记录
            cursor = self.sql.cursor()
            query = 'select * from apps where app_name = "%s" and developer_name = "%s"' % (app_name, developer_name)
            rows = cursor.execute(query)
            for row in rows:
                print("record exists. app_name: %s, developer_name: %s" % (app_name, developer_name))
                return None

            self.app_count = self.app_count + 1
            content = self.get(target, scroll=False)
            if len(content) < 1:
                return app        

            soup = BeautifulSoup(content, "html.parser")
            # 先找到开发者信息的span, 然后再找邮箱地址
            developer_span = soup.select("body > div > div:nth-child(6) > c-wiz > div > div > div > div > div > c-wiz:nth-last-child(1) > div:nth-child(1) > div:nth-child(2) > div > div:nth-last-child(1) > span > div > span")
            if 0 == len(developer_span):
                developer_span = soup.select("body > div > div:nth-child(6) > c-wiz > div > div > div > div > div > c-wiz:nth-last-child(2) > div:nth-child(1) > div:nth-child(2) > div > div:nth-last-child(1) > span > div > span")

            mail = ""
            links = developer_span[0].select("div > a")

            for link in links:
                if "@" in link.text:
                    mail = link.text

            print("num: " + str(self.app_count))
            print("gp link: " + target)
            print("app name: " + app_name)
            print("developer: " + developer_name)
            print("mail address: " + mail)
            print ("------------")

            app = {
                "app_name": app_name,
                "gp_link": target,
                "developer_name": developer_name,
                "mail": mail,
            }

            self.redis.lpush("crayon", json.dumps(app))

        except:
            print(traceback.format_exc())

        return app

    def run(self):
        type_count = 0
        self.app_count = 0

        more_links = self.get_more_links()
        type_count = len(more_links)
        for more_link in more_links:
            href = more_link.attrs.get("href")
            target = BASE_URL + href
            print("type target: ", target)

            content = self.get(target)
            if len(content) < 1:
                continue
            soup = BeautifulSoup(content, "html.parser")
            app_divs = soup.select("body > div > div > c-wiz > div > c-wiz > div > c-wiz > c-wiz > c-wiz > div > div > div > c-wiz > div")

            for app_div in app_divs:
                try:
                    self.get_app_info(app_div)
                except:
                    print(traceback.format_exc())

        print("type count: ", type_count)
        print("app count: ", self.app_count)


if '__main__' == __name__:
    gl = ""
    if 2 == len(sys.argv):
        gl = sys.argv[1]

    crawler = GooglePlayCrawler(gl)
    try:
        crawler.run()
        # crawler.save()
    except:
        print(traceback.format_exc())
    crawler.close()
