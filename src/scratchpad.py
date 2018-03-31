'''
Created on Mar 26, 2018

@author: zburchill
'''
from bs4 import BeautifulSoup
import manga_updates

'''
TO-DO: 
    - add threading locks!!!!!!!!!!!!
'''

from basic_functions import *
from manga_updates import *

import json




define_global_variables()


# test_url = "/Users/zburchill/Desktop/test_scraped_page.html"
# 
# with open(test_url,"r", encoding="utf-16") as f:
#     s = f.read()
#     soup = BeautifulSoup(s)
# # soup = soupify("https://www.mangaupdates.com/series.html?id=2171")
# m = metadata_task(soup)[-1]
# print(m)

MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
# save_obj(m, MAIN_PATH+"single")
m = load_obj(MAIN_PATH+"single")

for k,v in m.items():
    print("-------=========--------")
    print(k)
    print(v)

print(m["categories"])
# print(m["id"])












def save_a(tupes):
    return((tupes[0],tupes[1]))



# save_a = save_progress("/Users/zburchill/Desktop/delete", save_progress.identity, 100)
# save_a(("XX","OO"))
# save_a(("XX","OO"))
# # save_a("b","c")
# print(save_a.data)
# print(list(save_a._shelf.items()))



MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
metadata_saver = save_progress(MAIN_PATH+"first", save_progress.identity, save_after_n=2)
# print(save_a.data)
# print(list(metadata_saver._shelf.items()))
# 
# "2171,29394,74847,95303,95498,18592,105656,15478"
# 


# test_saver = save_progress(MAIN_PATH+"test", save_progress.identity, save_after_n=2)
# for i in range(0,20):
#     k = str(i)
#     test_saver((k, m))
# 
# test_saver.close()


    

print("AAAAAAAAAA")
with shelve.open(MAIN_PATH + "first") as db:
    print(db)
#     print(list(db.keys()))
    print(list(db.items()))
    for k, v in db.items():
        print("-----------")
        print(k)
        print(v)





