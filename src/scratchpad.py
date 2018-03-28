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



test_url = "/Users/zburchill/Desktop/test_scraped_page.html"

with open(test_url,"r", encoding="utf-16") as f:
    s = f.read()
    soup = BeautifulSoup(s)

    

    





