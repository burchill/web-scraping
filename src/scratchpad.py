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
# m = load_obj(MAIN_PATH+"single")
# 
# for k,v in m.items():
#     print("-------=========--------")
#     print(k)
#     print(v)
# 
# print(m["categories"])
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
# metadata_saver = save_progress(MAIN_PATH+"first", save_progress.identity, save_after_n=2)
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


manga_ids = list(set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))) 

print("AAAAAAAAAA")
c=0
c2=0
d={}
good_keys = []
bad_keys = []

weirdos =['11183', '110397', '118812', '7157', '24764', '50747', '1410', '2665', '54215', '56551', '32119', '4825', '72251', '53683', '129630', '138217', '78113', '117791', '12578', '53507', '43769', '3078', '106021', '7056', '41430', '4470', '614', '8126', '11039', '59594', '107106', '136952', '14738', '2490', '103185', '107192', '6346', '115705', '119794', '118714', '95411', '2458', '1146', '118350', '112872', '68982', '6341', '80386', '19859', '118260', '3916', '3264', '5680', '122677', '65695', '2775', '52894', '105477', '74055', '116302', '87918', '25799', '23170', '71530', '134878', '1615', '506', '135265', '59514', '65255', '81188', '12183', '63336', '66727', '6710', '32506', '579', '64034', '35129', '565', '103321', '12455', '82976', '112744', '138501', '21264', '77178', '62194', '35896', '18278', '56892', '46482', '104644', '6706', '115298', '125266', '79620', '130855', '58852', '2948', '58308', '66458', '4080', '77484', '128572', '48526', '3385', '45475', '9487', '22393', '121955', '13379', '75351', '80553', '105867', '90216', '59061', '110712', '957', '4116', '29914', '11412', '69007', '64751', '79827', '4821', '38117', '42004', '45530', '1105', '69989', '51824', '105943', '73020', '5867', '95731', '43946', '44806', '47734', '64237', '4697', '93876', '41903', '7610', '7333', '8089', '11789', '142693', '37215', '120692', '15707', '17982', '102398', '34257', '17171', '120605']




with shelve.open(MAIN_PATH + "first") as db:
    print(db)
    print(len(db.items()))
    
    for k, v in db.items():
        c2+=1
        good_keys+=[k]
    
    for i in manga_ids:
        if db.get(i):
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





