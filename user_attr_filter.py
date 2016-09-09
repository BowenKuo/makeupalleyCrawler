import pymysql
import numpy as np

def more():    
    more= input("Try another filter? Y/N: ").upper()
    if more == 'Y':
        get_variables()
        
    elif more =='N':
        print("closing mysql connection")
        conn.close()

def get_rating(t_id, user_attr, attr_filter):
    c.execute("SELECT rating from author INNER JOIN review ON (author.name = review.author) WHERE t_id = %(id)s AND " 
             + user_attr + " = %(attr)s",{'id':t_id,'attr':attr_filter})
    all_ratings = c.fetchall()
    if len(all_ratings) > 0:
        filtered_av_rating = round(np.array(all_ratings).mean(),1)
        print("Number of filtered ratings: ", len(all_ratings))
        print("New average rating: ", filtered_av_rating)
    else:
        print('no reviews fall under your desired filter, please select another filter.')
        more()

def get_comments(t_id, user_attr, attr_filter):
    c.execute("SELECT rating,content from author INNER JOIN review ON (author.name = review.author) WHERE t_id = %(id)s AND " 
                   + user_attr + " = %(attr)s",{'id': t_id, 'attr': attr_filter})
    while True:
        show = input("Press 'c' to show next filtered comment, press 'q' to quit: ").lower()
        if show == 'c':
            if c.fetchone() != None:
                print(c.fetchone())
                c.fetchone()    
            else:
                print("no more comments to show")
                break
        elif show == 'q':   
            break
    

def get_variables():
    t_id = input("Please enter item id number: ")

    print("Please enter user attribute to use as filter. Options are below")
    c.execute("SHOW COLUMNS FROM author")
    columns = c.fetchall()
    attrs =[]
    for col in columns:
        print(col[0])
        attrs.append(col[0])
    
    user_attr = input("Enter attribute to use as filter: ")
    if user_attr in attrs:
        pass
    else:
        print('Please enter a valid attribute to use as filter')
        user_attr = input("Enter attribute to use as filter: ")

        print("Please specify attribute filter. Options are below ")

    filters = str("SELECT DISTINCT " + user_attr + " FROM author")
    c.execute(filters)
    filters = c.fetchall()
    filter_list = []
    for fil in filters:
        print(fil)
        filter_list.append(fil[0])

    attr_filter = input("Please specify attribute filter: ")
    
    if attr_filter in filter_list:
        pass
    else:
        print("Please enter valid filter")
        attr_filter = [input("Please specify attribute filter: ")]
    
    get_rating(t_id, user_attr,attr_filter)
    get_comments(t_id, user_attr,attr_filter)

 
if __name__ == '__main__':
    conn = pymysql.connect(host = "localhost", user = 'user', password = 'password', db = 'makeupalley')
    c= conn.cursor()
    get_variables()
    more()