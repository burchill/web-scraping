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

import json, shelve



define_global_variables()


test_url = "/Users/zburchill/Desktop/test_scraped_page.html"

with open(test_url,"r", encoding="utf-16") as f:
    s = f.read()
    soup = BeautifulSoup(s)
    
# soup = soupify("https://www.mangaupdates.com/series.html?id=17")
m = metadata_task(soup)[-1]
print(m["authors"])

j = json.dumps(m)
j2 = json.loads(j)
# print(j2["original_pub"][1])
 
# for cat, l in m.items():
#     if isinstance(l, list):
#         for e in l:
#             if "<!--" in e:
#                 print("-----------")
#                 print(cat)
#                 print(e)
#     

print(m["categories"])












def save_a(tupes):
    return((tupes[0],tupes[1]))



class save_progress(object):
    def __init__(self, filename, f, save_after_n, *args, **kwargs):
        self._f = f
        self._save_after = save_after_n
        self._shelf = shelve.open(filename)
        self.filename = filename
        
        # Not affected by args:
        self._writing_lock = threading.Lock()
        self._data_lock = threading.Lock() # don't need it
        self._n = 0
        self.data = {}
        
    def __call__(self, *args, **kwargs):
        # If it needs to sync/save
        if self._n == self._save_after:
            self.sync_dict()
            self._n = 0
        with self._data_lock:
            print(self._f(*args, **kwargs))
            k, v = self._f(*args, **kwargs)
            self.data[k] = v
        self._n += 1
            
    def sync_dict(self):
        with self._writing_lock:
            with self._data_lock:
                # Sync shelf
                self.shelve_dict(self.data)
                self._shelf.sync()
                # Empty out dict
                del self.data
                self.data = {}
        
    def shelve_dict(self, d):
        for k, v in d.items():
            self._shelf[k] = v
        
    def close(self):
        self.sync_dict()
        self._shelf.close()
    
    @staticmethod
    def identity(e):
        """ for functions that already output a key value tuple """
        return(e)


save_a = save_progress("/Users/zburchill/Desktop/delete", save_progress.identity, 100)
save_a(("XX","OO"))
save_a(("XX","OO"))
# save_a("b","c")
print(save_a.data)
print(list(save_a._shelf.items()))









