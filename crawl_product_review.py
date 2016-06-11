from bs4 import BeautifulSoup as bs
from threading import Thread
import urllib
import urllib2
import time
import json
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

""" database setting 
"""
# db = MySQLdb.connect('localhost', 'root', ****, 'makeupalley')
db.set_character_set('utf8')

""" get page's comments 
"""
def get_comments(inner_HTML, tid):

    global db

    """ bs4 inner_HTML
    """
    soup = bs(inner_HTML, 'lxml')

    """ find all comments
    """
    comments = soup.findAll("div", {"class": "comments"})

    for comment in comments:

        cursor = db.cursor()

        """ id
        """
        comment_id = int(comment.findAll("div", {"class": "comment-content"})[0].p['id'][1:])

        """ rating
        """
        rating = int(comment.findAll("div", {"class": "lipies"})[0].span['class'][0].split('-')[1])

        """ author name
        """
        author_name = comment.findAll("span", {"itemprop": "name"})[0].text.replace("'", "''").encode('utf8')
        check_author_in_db_SQL = """
            SELECT *
            FROM author
            WHERE name = '%s'
        """ %(author_name)
        cursor.execute(check_author_in_db_SQL)
        check_author_result = cursor.fetchall()
        if check_author_result:
            pass
        else:
            """ get author page content ( joinedTime, location ) and check author is available
            """
            headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'ASPSESSIONIDSQTBQDDQ=IGEIFPIBHPKPMBIFAAPKOANH; cuq=%7B35601117%2D8B51%2D4E22%2D876C%2D2103B9CF211E%7D; __gads=ID=070c169d0e80d5a5:T=1459389925:S=ALNI_MYI7m2o1ByRKSVYaMqidwP39W1OGQ; ASPSESSIONIDQSTDTBDQ=GOIJBKFCBILKKMKOEKNPBINB; ASPSESSIONIDQWTDTBDQ=NDAEGMFCAFCBJOKMEKBPOABD; ASPSESSIONIDSQSBTACR=KLHJBGCDPMAACAONIKHIGNAM; ASPSESSIONIDSUSBTACR=LLJODGCDOOAHLKCJAEFNMJFO; ASPSESSIONIDQQRDQDDR=JDFELDPDINKDGCMMGNEMALED; ASPSESSIONIDQURDQDDR=NNFELDPDLNJBELDGAOGOMHJE; ASPSESSIONIDQQSAQDCQ=OFAHFPODNFGKMGKNKJJPNIOL; ASPSESSIONIDQUSAQDCQ=LKHCGPODGNNEGNBFDLCCPCCJ; ASPSESSIONIDSQRAQDDQ=HEALGNBDHDCLKBKMDINPEDLP; ASPSESSIONIDSURAQDDQ=HCGNCACDEPOBIKDPJCKACCCP; ASPSESSIONIDQWRBRDCQ=BAOKJLODOMGMPMBONPDPAPFF; ASPSESSIONIDSWTDTACQ=EKHNOILAOODCBJOBPCPGDKGP; crm=%FE23%3A9732b%FEuspglzmmjx; cs=%FENB%2185%3B24%3B3%21721308205%FE2%FEnpd%2FmjbnhA311239zmmjx%FEuspglzmmjx%FE94%3A8973; ASPSESSIONIDQUTDQDDR=LCDLFBIBIEOMIPHCMJFHMAGK; __utma=77819144.2116043615.1459350963.1460867791.1460881480.40; __utmb=77819144.3.9.1460881485138; __utmc=77819144; __utmz=77819144.1460817681.35.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
                'Host':'www.makeupalley.com',
                'Referer':'https://www.makeupalley.com/board/j.asp?bid=1&tid=4121437',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
            }
            request = urllib2.Request(
                url = 'https://www.makeupalley.com/p_'+author_name,
                headers = headers,
            )

            author_page_HTML = urllib2.urlopen(request).read()
            author_soup = bs(author_page_HTML, 'lxml')
            author_details = author_soup.findAll("div", {"class": "details"})
            if author_details:
                joinedTime = author_details[0].p.text.split(': ')[1]
                joinedTime = datetime.strptime(joinedTime, "%m/%d/%Y").strftime('%Y-%m-%d')
                location = author_details[0].findAll("p", {"class": "custom-margin-bottom"})[0].text.split(': ')[1]
                status = 1
            else:
                joinedTime = ''
                location = ''
                status = 0


            """ get author data in json
            """
            author_json_url = 'https://www.makeupalley.com/account/profileJson.asp'
            values = {'u': author_name}
            data = urllib.urlencode(values)
            req = urllib2.Request(author_json_url, data)
            response = urllib2.urlopen(req)
            the_page = response.read()
            author_json = json.loads(the_page)

            ageRange = author_json['ageRange']
            eyeColor = author_json['eyeColor']
            skinType = author_json['skinType']
            skinTone = author_json['skinTone']
            skinUndertone = author_json['skinUndertone']
            hairColor = author_json['hairColor']
            hairTexture = author_json['hairTexture']
            hairType = author_json['hairType']

            """ make insert SQL of author
            """
            insert_author_data_SQL = """
                INSERT INTO author(name, ageRange, eyeColor, hairColor, hairTexture, hairType, skinTone, skinType, skinUndertone, joinedTime, location, status)
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)
            """ %(author_name, ageRange, eyeColor, hairColor, hairTexture, hairType, skinTone, skinType, skinUndertone, joinedTime, location, status)

            try:
                cursor.execute(insert_author_data_SQL)
                db.commit()
            except MySQLdb.Error, e:
                try:
                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                except IndexError:
                    print "MySQL Error: %s" % str(e)
                print '\t [ERR - review]'
                print insert_author_data_SQL
                db.rollback()

            

        """ published datetime
        """
        published_datetime = comment.findAll("time", {"itemprop": "datePublished"})[0].text
        try:
            published_datetime_formatted = datetime.strptime(published_datetime, "%m/%d/%Y %I:%M:%S %p").strftime('%Y-%m-%d %H:%M:%S')
        except:
            published_datetime_formatted = datetime.strptime(published_datetime, "%m/%d/%Y").strftime('%Y-%m-%d %H:%M:%S')

        """ comment content
        """
        comment_content = comment.findAll("div", {"class": "comment-content"})[0].p.text.lstrip().rstrip().replace("'", "''").encode('utf8')+' '
        
        """ positive number of comment and
            negative number of comment
        """
        comment_option = comment.findAll("div", {"class": "comment-options"})[0]
        is_helpful_text = comment_option.findAll("div", {"class": "thumbs"})[0].text
        comment_positive_num = 0
        comment_negative_num = 0
        if is_helpful_text == ' Is this review helpful? YesNo ':
            pass
        else:
            comment_positive_num = int(is_helpful_text.split(' ')[1])
            comment_all_num = int(is_helpful_text.split(' ')[4])
            comment_negative_num = comment_all_num - comment_positive_num

        """ SQL: insert comment via product
        """
        comment_SQL = """
            INSERT review(t_id, r_id, author, rate, content, time, positive_num, negative_num)
            VALUES (%d, %d, '%s', %d, '%s', '%s', %d, %d)
        """ %(tid, comment_id, author_name, rating, comment_content, published_datetime_formatted, comment_positive_num, comment_negative_num)
        
        try:
            cursor.execute(comment_SQL)
            db.commit()
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
            print '\t [ERR - review]'
            print comment_SQL
            db.rollback()





def process(base_url, tid):

    global db

    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':'cuq=%7B5EC6DC19%2D2804%2D47B9%2D9A55%2D3CF44F51D1DE%7D; __utmt=1; __utma=77819144.579216116.1461223295.1461223295.1461223295.1; __utmb=77819144.1.10.1461223295; __utmc=77819144; __utmz=77819144.1461223295.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __gads=ID=798dce59d66d2990:T=1461223296:S=ALNI_Mbhspa8QSoDXruAUEfl_-PgwGgzQw; ASPSESSIONIDQUTDRCCQ=HNGBNFODGDMJDLKBBGKNOGBE',
        'Host':'www.makeupalley.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
    }

    print 'test'

    proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    request = urllib2.Request(
        url = base_url,
        headers = headers,
    )

    inner_HTML = urllib2.urlopen(request).read()

    print 'shit'
    print inner_HTML
    print 'nope'

    if inner_HTML == '':
        pass
    else:

        try:

            cursor = db.cursor()

            """ bs4 inner_HTML
            """ 
            soup = bs(inner_HTML, 'lxml')


            """ product name
            """ 
            product_name = soup.findAll("div", {"id": "ProductName"})[0].text.replace("'", "''").encode('utf8')

            
            """ ingredients
            """ 
            ingredients = soup.findAll("span", {"id": "hold-ingredients"})[0].text.lstrip().rstrip().replace("'", "''").encode('utf8')+' '


            """ category
            """ 
            category = soup.findAll("a", {"class": "track_BreadCrumbs_Category"})[0].span.text.replace("'", "''").encode('utf8')


            """ brand
            """ 
            brand = soup.findAll("a", {"class": "track_BreadCrumbs_Brand"})[0].span.text.replace("'", "''").encode('utf8')



            """ get aggregate item
            """ 
            item_aggregate = soup.findAll("div", {"itemprop": "aggregateRating"})
            if item_aggregate:
                item_aggregate_p_list = item_aggregate[0].findAll("p")
                """ rating by members
                """
                rating = item_aggregate[0].h3.text

                """ number of reviews
                """ 
                reviews_num = int(item_aggregate_p_list[0].span.text)

                """ percent of who would repurchase
                """ 
                repurchase = item_aggregate_p_list[1].text.split("%")[0]

                """ package quality
                """ 
                package_quality = re.search('[0-9]\.[0-9]', item_aggregate_p_list[2].text).group(0)

            else:
                reviews_num = 0
                repurchase = ''
                package_quality = ''


            """ SQL : insert product data
            """
            product_SQL = """
                INSERT INTO product(t_id, name, category, brand, ingredients, rate, reviews_num, repurchase, package_quality)
                VALUES (%d, '%s', '%s', '%s', '%s', %s, %d, '%s', '%s')
            """ %(tid, product_name, category, brand, ingredients, rating, reviews_num, repurchase, package_quality)


            try:
                cursor.execute(product_SQL)
                db.commit()
            except MySQLdb.Error, e:
                try:
                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                except IndexError:
                    print "MySQL Error: %s" % str(e)
                print '\t [ERR - product]'
                print product_SQL
                db.rollback()
            

            if item_aggregate:
                """ run first page
                """ 
                get_comments(inner_HTML, tid)

                """ run next page until none
                """ 
                page_count = 2
                next_page_content = 'first_time'
                while(next_page_content != ''):
                    base_url_list = base_url.split('/')
                    base_url_list.insert(5, 'page='+str(page_count))
                    next_page_url = '/'.join(base_url_list)

                    """ request next page
                    """ 
                    request = urllib2.Request(
                        url = next_page_url,
                        headers = headers,
                    )

                    """ get next page content
                    """ 
                    next_page_content = urllib2.urlopen(request).read()
                    get_comments(next_page_content, tid)

                    #time.sleep(0.1)
                    page_count += 1


        except:
            pass
        

        

        # # take 'f(' and ');' away
        # row = row[2:]
        # row = row[:-3]
        
        # # split row string by comma
        # col_list = row.strip().split(',')

        # # REPLY CLASS
        # reply_class = int(col_list[0])

        # # QUESTION ID
        # question_id = int(col_list[1])

        # # REPLY ID
        # reply_id = int(col_list[2])

        # class_dict[reply_class] = reply_id

        # # TITLE
        # title = ','.join(col_list[3:-5])[1:-1].decode('latin-1').encode("utf-8")
        # title = title + ' '

        # # CONTENT
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #     'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        #     'Cache-Control': 'max-age=0',
        #     'Connection': 'keep-alive',
        #     'Cookie': 'ASPSESSIONIDSQTBQDDQ=IGEIFPIBHPKPMBIFAAPKOANH; cuq=%7B35601117%2D8B51%2D4E22%2D876C%2D2103B9CF211E%7D; crm=%FE23%3A9732b%FEuspglzmmjx; cs=%FENQ%2134%3B12%3B32%21721301404%FE2%FEnpd%2FmjbnhA311239zmmjx%FEuspglzmmjx%FE94%3A8973; __utma=77819144.2116043615.1459350963.1459350963.1459353409.2; __utmb=77819144.35.9.1459355756786; __utmc=77819144; __utmz=77819144.1459350963.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        #     'Host': 'www.makeupalley.com',
        #     'Upgrade-Insecure-Requests': '1',
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
        # }
        # request = urllib2.Request(
        #     url = 'http://www.makeupalley.com/rss/j.aspx?m='+str(reply_id),
        #     headers = headers,
        # )
        # content_res = urllib2.urlopen(request).read()
        # soup = BeautifulSoup(content_res, 'lxml')
        # content_not_parse = soup.get_text()
        # # content = ' '.join(content_not_parse.split('(|(')[5:]).replace("'", "''").encode('utf8').decode('unicode_escape')
        # content = ' '.join(content_not_parse.split('(|(')[5:]).replace("'", "''").encode('utf8')
        # content = content + ' '

        # # AUTHOR
        # author = col_list[-5][1:-1]

        # try:
        #     post_time = datetime.strptime(col_list[-4], "'%m/%d/%Y %I:%M%p'").strftime('%Y-%m-%d %H:%M:%S')
        # except:
        #     post_time = datetime.strptime(col_list[-4], "'%m/%d/%Y'").strftime('%Y-%m-%d %H:%M:%S')


        # # write in question file
        # if reply_class == 0:
        #     sql = """
        #         INSERT INTO message(q_id, r_id, subtitle, content, author, time)
        #         VALUES(%d, %d, '%s', '%s', '%s', '%s')""" % (question_id, reply_id, title, content, author, post_time)
        #     print 'Question :\t' + str(question_id)
        # # write in reply file
        # else:
        #     sql = """
        #         INSERT INTO message(q_id, r_id, reply_to, subtitle, content, author, time)
        #         VALUES(%d, %d, %d, '%s', '%s', '%s', '%s')""" % (question_id, reply_id, class_dict[reply_class-1], title, content, author, post_time)
        #     print ' ->Reply :\t\t' + str(reply_id)



        # try:
        #     cursor.execute(sql)
        #     db.commit()
        # except:
        #     print '\t [ERR]'
        #     print sql
        #     db.rollback()

def seconds_to_clock(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return " %d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print '[Usage] python program.py start_item_id end_item_id '
    else:
        end_tid = int(sys.argv[2])
        start_tid = int(sys.argv[1])
        now_tid = start_tid
        total_gap = end_tid - start_tid + 1
        start_time = time.time()

        while now_tid <= end_tid:

            current_time = time.time()
            base_url = 'https://www.makeupalley.com/product/showreview.asp/ItemId=' + str(now_tid)

            print '[BEGIN]  ' + base_url + '\t[EXE TIME]:' + seconds_to_clock(current_time - start_time)
            print '[PROGRESS] ------ ' + str((float(now_tid-start_tid+1)/total_gap)*100) + '%'

            process(base_url, now_tid)

            now_tid += 1

        db.close()
        print '--- FINISHED ALL ---'
        
