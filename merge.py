#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

import sys
import sqlite3
import traceback

if '__main__' == __name__:
    gl = ""
    if 3 == len(sys.argv):
        src_db = sqlite3.connect(sys.argv[1])
        dst_db = sqlite3.connect(sys.argv[2])

        src_cursor = src_db.cursor()
        src_cursor.execute("select app_name, developer_name, mail, gp_link from apps")
        rows = src_cursor.fetchall()

        dst_cursor = dst_db.cursor()

        total_count = 0
        new_count = 0
        for row in rows:
            total_count = total_count + 1
            try:
                dst_cursor.execute('insert into apps (app_name, developer_name, mail, gp_link, created_at) values ("%s", "%s", "%s", "%s", datetime())' % (row[0], row[1], row[2], row[3]))
                dst_db.commit()
                new_count = new_count + 1
                print("app_name: " + row[0])
                print("developer_name: " + row[1])
                print("mail: " + row[2])
                print("gp_link: " + row[3])
                print ("------------")
            except:
                if 'UNIQUE constraint failed' not in traceback.format_exc():
                    print(traceback.format_exc())

        print("total: ", total_count)
        print("new: ", new_count)

        src_db.close()
        dst_db.close()

    else:
        print("merge.py from.db to.db")
