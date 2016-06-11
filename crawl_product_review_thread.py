from bs4 import BeautifulSoup as bs
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

        time.sleep(0.1)
        
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

        # time.sleep(1)




def process(base_url, tid):

    global db

    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':'ASPSESSIONIDSQTBQDDQ=IGEIFPIBHPKPMBIFAAPKOANH; cuq=%7B35601117%2D8B51%2D4E22%2D876C%2D2103B9CF211E%7D; __gads=ID=070c169d0e80d5a5:T=1459389925:S=ALNI_MYI7m2o1ByRKSVYaMqidwP39W1OGQ; ASPSESSIONIDQSTDTBDQ=GOIJBKFCBILKKMKOEKNPBINB; ASPSESSIONIDQWTDTBDQ=NDAEGMFCAFCBJOKMEKBPOABD; ASPSESSIONIDSQSBTACR=KLHJBGCDPMAACAONIKHIGNAM; ASPSESSIONIDSUSBTACR=LLJODGCDOOAHLKCJAEFNMJFO; ASPSESSIONIDQQRDQDDR=JDFELDPDINKDGCMMGNEMALED; ASPSESSIONIDQURDQDDR=NNFELDPDLNJBELDGAOGOMHJE; ASPSESSIONIDQQSAQDCQ=OFAHFPODNFGKMGKNKJJPNIOL; ASPSESSIONIDQUSAQDCQ=LKHCGPODGNNEGNBFDLCCPCCJ; crm=%FE23%3A9732b%FEuspglzmmjx; cs=%FENB%2191%3B16%3B12%21721304205%FE2%FEnpd%2FmjbnhA311239zmmjx%FEuspglzmmjx%FE94%3A8973; ASPSESSIONIDSQRAQDDQ=HEALGNBDHDCLKBKMDINPEDLP; __utma=77819144.2116043615.1459350963.1460192402.1460559027.18; __utmb=77819144.11.10.1460559027; __utmc=77819144; __utmz=77819144.1459350963.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ASPSESSIONIDSURAQDDQ=BEPLGNBDADCJMGMMBFGJPCEK',
        'Host':'www.makeupalley.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    }

    request = urllib2.Request(
        url = base_url,
        headers = headers,
    )

    inner_HTML = urllib2.urlopen(request).read()

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
                INSERT INTO product(t_id, name, category, brand, ingredients, reviews_num, repurchase, package_quality)
                VALUES (%d, '%s', '%s', '%s', '%s', %d, '%s', '%s')
            """ %(tid, product_name, category, brand, ingredients, reviews_num, repurchase, package_quality)

            time.sleep(0.1)

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


                    page_count += 1


        except:
            pass



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

        threads = []

        while now_tid <= end_tid:

            current_time = time.time()
            base_url = 'https://www.makeupalley.com/product/showreview.asp/ItemId=' + str(now_tid)

            new_t = Thread(target=process, args=(base_url, now_tid, ))
            new_t.start()
            threads.append(new_t)

            # process(base_url, now_tid)

            if now_tid%5 == 0:

                print '[BEGIN]  ' + base_url + '\t[EXE TIME]:' + seconds_to_clock(current_time - start_time)
                print '[PROGRESS] ------ ' + str((float(now_tid-start_tid+1)/total_gap)*100) + '%'

                for t in threads:
                    t.join()

                time.sleep(3)

            time.sleep(0.1)
            now_tid += 1

        db.close()
        print '--- FINISHED ALL ---'
        
