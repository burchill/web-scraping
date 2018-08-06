'''
Created on Mar 26, 2018

@author: zburchill
'''


"""

Structure for the watch:
- Relationship of groups
- Group of hands (obj)
    - Relationship of hands in group
    - Lock (obj)
        - Queue (obj)
            - Variables
                v the Request currently being used
                v the Request in stand-by
            - Request(s)
                - Variables
                    v the app making the request
                    v the function requesting
                    v description / "function" of the function requesting
                    v (?) possible secondary description/information about purpose 
                    v priority of the request
                    v amount of time request will likely take to complete / a general time property of completion
                    v decay property of Request
        - Public functions:
            f get info about queue
            
    - Hand (obj)
        - Variables
            i min speed
            i max speed
            i some property the watch people want to use to control behavior
            v speed
            v position
        - 


        
    




WATCH side:
needs to 


What the APP needs to know about the WATCH INHERENTLY:
need to modify behavior depending on the INHERENT properties of the watch:
  * The number of hands
  * the relatedness of the hands (ie, minute/second and chronometer? or two equal hands? etc)
  * the recommended min and max speeds of the watch hands
  

 


A system where connecting apps ask which HANDS they should use, 
    given some sort of description of what the intended function is
    






"""



import pickle

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)    
    


MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"

valid_ids = load_obj(MAIN_PATH+"all_series_ids")
print(len(valid_ids))

with open(MAIN_PATH+"everything_log", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
print(len(lines))
for e in lines[1907:1910]:
    print(len(e))
    print(e[0:2])
good_lines = [e for e in lines if len(e) > 4 and e[0:2] == "('"]
print(len(good_lines))
# print(good_lines)











# from bs4 import BeautifulSoup
# import requests
# from basic_functions import clean_find_all, join_urls
# 
# # Hacking Josh's website
# payload = {"password": "camera"}
# jsite = "http://iamjoshualee.com/"
# url_formatter="http://iamjoshualee.com/api/auth/visitor/site?crumb={0}"
# 
# with requests.Session() as s:
#     first_get = s.get(jsite)
#     soup = BeautifulSoup(first_get.text)
#     print(soup.title)
#     crumb = s.cookies.get_dict()["crumb"]
#     
#     first_post = s.post(url_formatter.format(crumb), 
#                 json = payload,
#                 cookies = s.cookies.get_dict(),
#                 headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#                            "Content-Type": "application/json",
#                            "Accept": "*/*",
#                            "Accept-Encoding": "gzip, deflate",
#                            "Accept-Language": "en-US,en;q=0.9"})
#     
#     print(first_post)
#     print(first_post.headers)
#     print(first_post.status_code)
#     print(first_post.cookies)
#     password_cookie_dict = requests.utils.dict_from_cookiejar(first_post.cookies)
#     
#     second_get = s.get(join_urls(jsite,"people/"))
#     soup = BeautifulSoup(second_get.text)
#     pages = clean_find_all(soup, ['li',{'class': 'gallery-collection'}])
#     print(pages)
#     links = [join_urls(jsite,e.a["href"]) for e in pages]
#     print(links)
#     
#     page = links[0]
#     all_the_images = clean_find_all(soup,['img',{'class': 'load-false'}])
#     print(all_the_images)
#     img_urls = [e["src"] for e in all_the_images]
#     print(img_urls)
#     print(soup)
#     
#     
    
#     
#     
#     second_get = s.get('http://iamjoshualee.com/people')
#     soup = BeautifulSoup(second_get.text)
#     print(soup.title)
#     print(s.cookies.get_dict())
#     
#     good_cookies = s.cookies.get_dict()
    
#     https://static1.squarespace.com/static/55394a48e4b05abbe6ec9ff0/55394adae4b0d3a13ada9694/553950b5e4b0885052e04c1e/1429819578956/DSC_0081.jpg
#     https://static1.squarespace.com/static/55394a48e4b05abbe6ec9ff0/55394adae4b0d3a13ada9694/553950b5e4b0885052e04c1e/1429819578956/DSC_0081.jpg?format=3000w
    
    



# s = requests.Session()
# 
# r = s.get('http://httpbin.org/cookies', cookies={'from-my': 'browser'})
# print(r.text)
# 
# with requests.Session() as s:
#     payload = {"password": "camera"}
#     r = s.get('http://iamjoshualee.com/')
#     soup = BeautifulSoup(r.text)
#     print(soup.title)
#     crumb = s.cookies.get_dict()["crumb"]
#     
#     
#     
#     prepared_post = requests.Request('POST', url_formatter.format(crumb), data = payload)
# #     prepare_post = 
# #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
# #                             "Content-Type": "application/json",
# #     prepared_post.prepare_
# #     print(s.prepare_request(prepared_post).headers)
#     
#     r2 = s.post(url_formatter.format(crumb), 
#                 json=payload,
#                 headers = {# "Host": "iamjoshualee.com",
# #                             #"Connection": "keep-alive",
# # #                             "Content-Length": "21",
# #                             #"Origin": "http://iamjoshualee.com",
# #                             "X-Requested-With": "XMLHttpRequest",
#                             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#                             "Content-Type": "application/json",
#                             "Accept": "*/*",
# #                             "Referer": "http://iamjoshualee.com/",
#                             "Accept-Encoding": "gzip, deflate",
#                             "Accept-Language": "en-US,en;q=0.9"},
#                 cookies=s.cookies.get_dict())
#     soup = BeautifulSoup(r2.text)
#     print(r2.text)
#     print(r2)
#     print(r2.headers)
#     cc = r2.cookies
#     print(cc)
#     print(requests.utils.dict_from_cookiejar(cc))
# #     print(cc.dict_from_cookiejar())
#     print(r2.status_code)
#     print(soup.title)
#     the_req = r2.request
#     print(the_req)
#     print("AAAAAAAA")
# 
#     
#     r3 = s.get('http://iamjoshualee.com/')
#     soup = BeautifulSoup(r3.text)
#     print(soup.title)
#     print(s.cookies.get_dict())
#     
#     
#     "http://iamjoshualee.com/api/auth/visitor/site?crumb"




'''
from basic_functions import *
from manga_updates import *

import json




define_global_variables()





print(len(list(set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))) ))
assert 1==2





test_url = "/Users/zburchill/Desktop/test_scraped_page.html"
 
with open(test_url,"r", encoding="utf-16") as f:
    s = f.read()
    soup = BeautifulSoup(s)
soup = soupify("https://www.mangaupdates.com/series.html?id=17")
# soup = soupify("https://www.mangaupdates.com/series.html?id=51560")
m = metadata_task(soup)
print(m["related_series"])
print(m["authors"])
print(m["status"])
assert 1==2

MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
# save_obj(m, MAIN_PATH+"single")
# m = load_obj(MAIN_PATH+"single")
# 
# for k,v in m.items():
#     print("-------=========--------")
#     print(k)
#     print(v)
# 
# print(m["categories"])
# print(m["id"])












import shelve 
from basic_functions import *
from manga_updates import *
MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
manga_ids = list(set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))) 

c = c2 = 0
good_keys = []
bad_keys = []

db = shelve.open(MAIN_PATH + "first")
for k in db.keys():
    c2+=1
    good_keys+=[k]
 
for j in set(manga_ids):
    if j in db.keys():
        c+=1
        bad_keys+=[j]
    
print("With `db.keys(): {0}, with verifying from the list: {1}".format(c2, c))    
    
odd_men_out = list( set(bad_keys).difference( set(good_keys) ) )
list_of_keys = list(db.keys())
bad_key = odd_men_out[0]

print(bad_key)
print(bad_key in db.keys())
print(bad_key in db)
print(db[bad_key])
print(bad_key in list(db.keys()))
db.close()








with shelve.open(MAIN_PATH + "first_3") as db:
    for kaka in db.keys():
        c2+=1
        good_keys+=[kaka]
     
    for i in set(manga_ids):
        if i in db.keys():
            c+=1
            bad_keys+=[i]


# 
# 
manga_ids = list(set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))) 
 
print("AAAAAAAAAA")
c=0
c2=0
d={}
good_keys = []
bad_keys = []
 
weirdos =['11183', '110397', '118812', '7157', '24764', '50747', '1410', '2665', '54215', '56551', '32119', '4825', '72251', '53683', '129630', '138217', '78113', '117791', '12578', '53507', '43769', '3078', '106021', '7056', '41430', '4470', '614', '8126', '11039', '59594', '107106', '136952', '14738', '2490', '103185', '107192', '6346', '115705', '119794', '118714', '95411', '2458', '1146', '118350', '112872', '68982', '6341', '80386', '19859', '118260', '3916', '3264', '5680', '122677', '65695', '2775', '52894', '105477', '74055', '116302', '87918', '25799', '23170', '71530', '134878', '1615', '506', '135265', '59514', '65255', '81188', '12183', '63336', '66727', '6710', '32506', '579', '64034', '35129', '565', '103321', '12455', '82976', '112744', '138501', '21264', '77178', '62194', '35896', '18278', '56892', '46482', '104644', '6706', '115298', '125266', '79620', '130855', '58852', '2948', '58308', '66458', '4080', '77484', '128572', '48526', '3385', '45475', '9487', '22393', '121955', '13379', '75351', '80553', '105867', '90216', '59061', '110712', '957', '4116', '29914', '11412', '69007', '64751', '79827', '4821', '38117', '42004', '45530', '1105', '69989', '51824', '105943', '73020', '5867', '95731', '43946', '44806', '47734', '64237', '4697', '93876', '41903', '7610', '7333', '8089', '11789', '142693', '37215', '120692', '15707', '17982', '102398', '34257', '17171', '120605']
 
 
with shelve.open(MAIN_PATH + "first_3") as db:
    for kaka in db.keys():
        c2+=1
        good_keys+=[kaka]
     
    for i in set(manga_ids):
        if i in db.keys():
            c+=1
            bad_keys+=[i]
    
    odd_men_out = list(set(bad_keys).difference(set(good_keys)))
    list_of_keys = list(db.keys())
    



db = shelve.open(MAIN_PATH + "first_3")
for k in db.keys():
    c2+=1
    good_keys+=[k]
 
for j in set(manga_ids):
    if i in db.keys():
        c+=1
        bad_keys+=[j]
    
odd_men_out = list( set(bad_keys).difference( set(good_keys) ) )
list_of_keys = list(db.keys())
bad_key = odd_men_out[0]
print(bad_key)
print(bad_key in db.keys())
print(bad_key in db)
print(bad_key in list(db.keys()))
'''



'''


      
#     for k, v in db.items():
#         c2+=1
#         good_keys+=[k]
#     print(len(db.dict))
#     ks = list(db.keys())
#     for k in ks:
#         c2+=1
    for kaka in db.keys():
        c2+=1
        good_keys+=[kaka]
     
    for i in set(manga_ids):
        if i in db.keys():
#             print(db.get(i))
#             print(i)
            c+=1
            d[i]=db.get(i)
            bad_keys+=[i]
            if i not in db:
                print("XXXXXXXXXXXXXXXXXXXX")
             
    print(len(db.keys()))
print(c)
print(c2)
print(len(d))
 
print(set(good_keys).difference(set(bad_keys)))
print(set(bad_keys).difference(set(good_keys)))
print(len(weirdos))
print(len(set(bad_keys).difference(set(good_keys))))
 
print("11183" in manga_ids)


# for k, v in d.items():
# #     print(v.keys())
#     print("{0}:     {1}".format(v["status"], k))
#     print("S")

#     print(list(db.keys()))
#     print(list(db.items()))
#     for k, v in db.items():
#         print("-----------")
#         print(k)
#         print(v)


#  
# bb = shelve.open(MAIN_PATH + "first_3")
# ks = bb.keys()
#      

'''


