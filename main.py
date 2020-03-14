#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from bs4 import BeautifulSoup

import time
import smtplib
import traceback

BASE_URL = "https://play.google.com"


class GooglePlayCrawler(object):
    def __init__(self):
        # 初始化chrome driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        # disable image loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument('--proxy-server=socks5://hk.vpn.umlife.net:18500')

        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.apps = {}

    def close(self):
        self.driver.quit()

    def save(self):
        lines = []
        for app_name in self.apps:
            app = self.apps[app_name]
            lines.append('"%s","%s","%s","%s"' % (
                    app["app_name"],
                    app["developer_name"],
                    app["mail"],
                    app["target"]
                )
            )
        content = lines.join("\n")

        with open("result.csv", "w") as fd:
            fd.write(content)

    def mail(self, to):
        msg = MIMEMultipart("alternative")
        with open("template.html") as fd:
            html = MIMEText(fd.read(), 'html')
            msg.attach(html)

        msg['Subject'] = "Believe us：Better Future in Google Play"
        msg['From'] = 'yujingqiong@youmi.net'
        msg['To'] = '596635884@qq.com'
        # msg['To'] = to

        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # s.set_debuglevel(1)
        s.login('postmaster@notify.umlife.com', '7131f971298eef95d785d2156343c183')
        s.send_message(msg)
        s.quit()

    def get(self, url, scroll=True):
        self.driver.get(url)
        SCROLL_PAUSE_TIME = 5

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True and scroll:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # print(new_height)
            if new_height == last_height:
                break
            last_height = new_height

        content = self.driver.page_source.encode('utf-8')
        return content

    def get_more_links(self):
        content = self.get(BASE_URL + "/store/apps")
        soup = BeautifulSoup(content, "html.parser")

        # 第一个链接是新应用
        more_links = soup.select("a.id-track-click")

        return more_links

    def run(self):
        type_count = 0
        app_count = 0
        mails = {}

        more_links = self.get_more_links()
        type_count = len(more_links)
        for more_link in more_links:
            href = more_link.attrs.get("href")
            target = BASE_URL + href
            print("type target: ", target)

            content = self.get(target)
            soup = BeautifulSoup(content, "html.parser")
            app_divs = soup.select("body > div > div > c-wiz > div > c-wiz > div > c-wiz > c-wiz > c-wiz > div > div > div > c-wiz > div")
            for app_div in app_divs:
                app_link = app_div.select("c-wiz > div > div > div > div > div > a")[0]
                href = app_link.attrs.get("href")
                target = BASE_URL + href
                print("app_target: ", target)
                app_count = app_count + 1

                # 获取app名称和developer名称
                names = app_div.select("c-wiz > div > div > div:nth-child(2) > div > div > div > div > div > div")
                app_name = names[0].select("a > div:nth-child(1)")[0].text
                developer_name = names[1].select("a > div:nth-child(1)")[0].text

                content = self.get(target, scroll=False)

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

                #if mail in mails:
                    #continue
                #else:
                    #mails[mail] = 1

                print("num: " + str(app_count))
                print("gp link: " + target)
                print("app name: " + app_name)
                print("developer: " + developer_name)
                print("mail address: " + mail)
                print ("------------")

                self.apps[app_name] = {
                    "gp_link": target,
                    "developer": developer_name,
                    "mail": mail,
                }

                # self.mail(mail)

        print("type count: ", type_count)
        print("app count: ", app_count)
        print("mails: ", len(mails))


if '__main__' == __name__:
    try:
        crawler = GooglePlayCrawler()
        crawler.run()
        crawler.save()
    except:
        print(traceback.format_exc())
    crawler.close()
