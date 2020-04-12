#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import json
import time
import redis
import smtplib
import sqlite3
import traceback

import config


def mail(to):
    msg = MIMEMultipart("alternative")
    with open("template.html") as fd:
        html = MIMEText(fd.read(), 'html')
        msg.attach(html)

    msg['Subject'] = config.mail["subject"]
    msg['From'] = config.mail["from"]
    msg['To'] = to

    s = smtplib.SMTP(config.mail["address"], config.mail["port"])
    # s.set_debuglevel(1)
    s.login(config.mail["user"], config.mail["password"])
    s.send_message(msg)
    s.quit()


class GooglePlaySaver(object):
    def __init__(self):
        self.sql = sqlite3.connect("apps.db")
        self.redis = redis.Redis(host='localhost', port=6379)

    def close(self):
        self.sql.close()
        self.redis.close()

    def run(self):
        while True:
            ret = self.redis.brpop('crayon', timeout=10)
            if not ret:
                continue
            app = json.loads(ret[1])

            # 看数据库里面有没记录
            cursor = self.sql.cursor()
            query = 'select * from apps where app_name = "%s" and developer_name = "%s"' % (app["app_name"], app["developer_name"])
            rows = cursor.execute(query)

            exists = False
            for row in rows:
                print("record exists. app_name: %s, developer_name: %s" % (app["app_name"], app["developer_name"]))
                exists = True

            if exists:
                continue

            # 存数据库
            cursor = self.sql.cursor()
            query = 'insert into apps (app_name, developer_name, mail, gp_link, created_at) values ("%s", "%s", "%s", "%s", datetime())' % (app["app_name"], app["developer_name"], app["mail"], app["gp_link"])
            cursor.execute(query)
            self.sql.commit()

            # 发邮件
            mail(app['mail'])
            print(app)
            time.sleep(10)


if '__main__' == __name__:
    try:
        saver = GooglePlaySaver()
        saver.run()
    except:
        print(traceback.format_exc())
