#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sys
import time
import smtplib
import sqlite3
import traceback


def mail(to):
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


if '__main__' == __name__:
    if 2 == len(sys.argv):
        src_db = sqlite3.connect(sys.argv[1])
        src_cursor = src_db.cursor()
        src_cursor.execute("select distinct(mail) from apps")
        rows = src_cursor.fetchall()

        for row in rows:
            try:
                mail(row[0])
                print(row[0])
                time.sleep(10)
            except:
                print(traceback.format_exc())
