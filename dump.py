#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# @author hjweddie@163.com

import sys
import sqlite3

if '__main__' == __name__:
    if 2 == len(sys.argv):
        src_db = sqlite3.connect(sys.argv[1] + ".db")
        src_cursor = src_db.cursor()
        src_cursor.execute("select app_name, developer_name, mail, gp_link from apps")
        rows = src_cursor.fetchall()

        with open(sys.argv[1] + ".csv", "w") as fd:
            total_count = 0

            fd.write('"app_name","developer_name","mail","gp_link"\n')
            for row in rows:
                total_count = total_count + 1

                fd.write('"%s","%s","%s","%s"\n' % (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                ))
            print("total: ", total_count)

    else:
        print("dump.py hk")
