# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from threading import Thread
import urllib2
import time
from datetime import datetime
import random
import requests
import re
import sys 
import MySQLdb 
import sys
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')


delim = '\t'
one_page_tid_gap = 31
class_dict = dict()
# db = MySQLdb.connect('localhost', 'root', ****, 'makeupalley')


def process(row):
    global db, class_dict
    
    cursor = db.cursor()

    # take 'f(' and ');' away
    row = row[2:]
    row = row[:-3]
    
    # split row string by comma
    col_list = row.strip().split(',')

    # REPLY CLASS
    reply_class = int(col_list[0])

    # QUESTION ID
    question_id = int(col_list[1])

    # REPLY ID
    reply_id = int(col_list[2])

    class_dict[reply_class] = reply_id

    # TITLE
    title = ','.join(col_list[3:-5])[1:-1].decode('latin-1').encode("utf-8")
    title = title + ' '

    # CONTENT
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'ASPSESSIONIDSQTBQDDQ=IGEIFPIBHPKPMBIFAAPKOANH; cuq=%7B35601117%2D8B51%2D4E22%2D876C%2D2103B9CF211E%7D; crm=%FE23%3A9732b%FEuspglzmmjx; cs=%FENQ%2134%3B12%3B32%21721301404%FE2%FEnpd%2FmjbnhA311239zmmjx%FEuspglzmmjx%FE94%3A8973; __utma=77819144.2116043615.1459350963.1459350963.1459353409.2; __utmb=77819144.35.9.1459355756786; __utmc=77819144; __utmz=77819144.1459350963.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'Host': 'www.makeupalley.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
    }
    request = urllib2.Request(
        url = 'http://www.makeupalley.com/rss/j.aspx?m='+str(reply_id),
        headers = headers,
    )
    content_res = urllib2.urlopen(request).read()
    soup = BeautifulSoup(content_res, 'lxml')
    content_not_parse = soup.get_text()
    # content = ' '.join(content_not_parse.split('(|(')[5:]).replace("'", "''").encode('utf8').decode('unicode_escape')
    content = ' '.join(content_not_parse.split('(|(')[5:]).replace("'", "''").encode('utf8')
    content = content + ' '

    # AUTHOR
    author = col_list[-5][1:-1]

    try:
        post_time = datetime.strptime(col_list[-4], "'%m/%d/%Y %I:%M%p'").strftime('%Y-%m-%d %H:%M:%S')
    except:
        post_time = datetime.strptime(col_list[-4], "'%m/%d/%Y'").strftime('%Y-%m-%d %H:%M:%S')


    # write in question file
    if reply_class == 0:
        sql = """
            INSERT INTO message(q_id, r_id, subtitle, content, author, time)
            VALUES(%d, %d, '%s', '%s', '%s', '%s')""" % (question_id, reply_id, title, content, author, post_time)
        print 'Question :\t' + str(question_id)
    # write in reply file
    else:
        sql = """
            INSERT INTO message(q_id, r_id, reply_to, subtitle, content, author, time)
            VALUES(%d, %d, %d, '%s', '%s', '%s', '%s')""" % (question_id, reply_id, class_dict[reply_class-1], title, content, author, post_time)
        print ' ->Reply :\t\t' + str(reply_id)



    try:
        cursor.execute(sql)
        db.commit()
    except:
        print '\t [ERR]'
        print sql
        db.rollback()

def seconds_to_clock(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return " %d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print '[Usage] python program.py start_title_id end_title_id '
    else:
        end_tid = int(sys.argv[2])
        start_tid = int(sys.argv[1])
        total_gap = start_tid - end_tid

        start_time = time.time()

        while start_tid >= end_tid:
            current_time = time.time()
            base_url = 'http://www.makeupalley.com/board/j.asp?bid=1&tid=' + str(start_tid)
            print '[BEGIN]  ' + base_url + '\t[EXE TIME]:' + seconds_to_clock(current_time - start_time)
            print '[PROGRESS] ------ ' + str((1-(float(start_tid-end_tid)/total_gap))*100) + '%'


            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
                'Host': 'www.makeupalley.com',
                'Referer': base_url,
                'Upgrade-Insecure-Requests': '1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                'Connection': 'keep-alive',
                'Cookie' : 'ASPSESSIONIDSQTBQDDQ=IGEIFPIBHPKPMBIFAAPKOANH; cuq=%7B35601117%2D8B51%2D4E22%2D876C%2D2103B9CF211E%7D; __utmt=1; crm=%FE23%3A9732b%FEuspglzmmjx; cs=%FENQ%2134%3B12%3B32%21721301404%FE2%FEnpd%2FmjbnhA311239zmmjx%FEuspglzmmjx%FE94%3A8973; __utma=77819144.2116043615.1459350963.1459350963.1459353409.2; __utmb=77819144.10.9.1459354236482; __utmc=77819144; __utmz=77819144.1459350963.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            }

            request = urllib2.Request(
                url = base_url,
                headers = headers,
            )

            res = urllib2.urlopen(request).read()


            rows = re.findall(r'f\([0-9],.*\.*', res)
            all_this_round = len(rows)
            count = 1
            for row in rows:
                print 'PROGRESS : ' + str(count) + '/' + str(all_this_round)
                process(row)
                time.sleep(0.1)
                count += 1
            
            time.sleep(3)

            start_tid -= one_page_tid_gap

        db.close()
        print '--- FINISHED ALL ---'
        
