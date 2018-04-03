'''
Created on Mar 26, 2018

@author: zburchill
'''
from bs4 import BeautifulSoup


'''
TO-DO: 
    - add threading locks!!!!!!!!!!!!
'''

from basic_functions import *
from manga_updates import *

import json




define_global_variables()












def break_strings_by_line(soup_obj):
    big_l = []
    temp_l = []
    for child in soup_obj.children:
        if child.name == "br":
            if temp_l:
                big_l+="".join(temp_l)
                temp_l = []
        else:
            if get_string(child): temp_l += [ get_string(child) ]
    if temp_l: big_l+="".join(temp_l)
    return(big_l)


test_url = "/Users/zburchill/Desktop/test_scraped_page.html"
 
with open(test_url,"r", encoding="utf-16") as f:
    s = f.read()
    soup = BeautifulSoup(s)
# soup = soupify("https://www.mangaupdates.com/series.html?id=32093")
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


