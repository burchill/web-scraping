'''
Created on Mar 26, 2018

@author: zburchill
'''


import time
from selenium import webdriver

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('user-agent={}'.format(user_agent))
driver = webdriver.Chrome('../chromedriver',chrome_options=options)  # Optional argument, if not specified will search path.
driver.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
# driver.get("http://avi.im/stuff/js-or-no-js.html")
# p_element = driver.find_element_by_id(id_='demo')
# print(p_element.text)
print(driver.page_source)
driver.quit()

# driver.get('http://www.google.com/xhtml');
# time.sleep(5) # Let the user actually see something!
# search_box = driver.find_element_by_name('q')
# search_box.send_keys('ChromeDriver')
# search_box.submit()
# time.sleep(5) # Let the user actually see something!
# driver.quit()

# from selenium import webdriver
# driver = webdriver.PhantomJS("/Users/zburchill/Downloads/untitled folder/phantomjs-2.1.1-macosx/bin")
# driver.get("http://avi.im/stuff/js-or-no-js.html")
# p_element = driver.find_element_by_id(id_='intro-text')
# print(p_element.text)

import pickle, csv, os, shutil, json, copy

# class PersistentStack():
#     
#     def __init__(self, filename, flag='c', format='json', *args, **kwargs):
#         self.flag = flag                    # r=readonly, c=create, or n=new
#         self.format = format                # 'csv', 'json', or 'pickle'
#         self.filename = filename
#         if flag != 'n' and os.access(filename, os.R_OK):
#             fileobj = open(filename, 'rb' if format=='pickle' else 'r')
#             with fileobj:
#                 self.load(fileobj)
#         self.stack = list(*args, **kwargs)
#         
#     def sync(self):
#         'Write dict to disk'
#         if self.flag == 'r':
#             return
#         filename = self.filename
#         tempname = filename + '.tmp'
#         fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
#         try:
#             self.dump(fileobj)
#         except Exception:
#             os.remove(tempname)
#             raise
#         finally:
#             fileobj.close()
#         shutil.move(tempname, self.filename)    # atomic commit
# 
#     def close(self):
#         self.sync()
# 
#     def dump(self, fileobj):
#         if self.format == 'csv':
#             csv.writer(fileobj).writerows(self.items())
#         elif self.format == 'json':
#             json.dump(self, fileobj, separators=(',', ':'))
#         elif self.format == 'pickle':
#             pickle.dump(dict(self), fileobj, 2)
#         else:
#             raise NotImplementedError('Unknown format: ' + repr(self.format))
# 
#     def load(self, fileobj):
#         # try formats from most restrictive to least restrictive
#         for loader in (pickle.load, json.load, csv.reader):
#             fileobj.seek(0)
#             try:
#                 return self.update(loader(fileobj))
#             except Exception:
#                 pass
#         raise ValueError('File not in a supported format')
#     
#     def to_list(self):
#         return(copy.deepcopy(self.stack))
#     
#     def take_list(self, l):
#         self.stack = copy.deepcopy(l)
#         


import os, csv, pickle, json, shutil
class PersistentStack(list):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''
    
    def __init__(self, filename, flag='c', format='json', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        self.has_saved = False
        list.__init__(self, *args, **kwds)
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
                
    def sync(self):
        'Write list to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
            self.has_saved = True
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        
    def close(self):
        self.sync()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *exc_info):
        self.close()
        
    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(list(self))
        elif self.format == 'json':
            json.dump(list(self), fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(list(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))
        
    def clear(self):
        for _ in range(len(self)): self.pop()
        
    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                temp = loader(fileobj)
                self.clear()
                return self.extend(temp)
            except Exception:
                pass
        raise ValueError('File not in a supported format')
    
    def to_list(self):
        return(list(self))

    def reset(self):
        if os.access(self.filename, os.R_OK) and (self.flag != 'n' or self.has_saved):
            fileobj = open(self.filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        elif self.flag == "n" and not self.has_saved:
            self.clear()


'''

Just send the weights to the flask app


'''



class WeightLogger(PersistentStack):
    def __init__(self, filename, tag_filename = None, *args, **kwds):
        self.tag_stack = tag_filename
        self.check_counter = 0
        PersistentStack.__init__(self, filename = filename, *args, **kwds)
        
    
    def check_tags(self, count=0):
        if self.check_counter >= count:
           self.check_counter = 0
                
    
    def load_tags(self):
        pass    
    
    def log_weight(self, d):
        if self.tag_stack:
            pass
        self.append(d)
        self.sync()
        
                
    


'''
* utc time 
* reference to tag info
* weights (buffer)
* mean, std, 


'''




"https://hidemyna.me/en/proxy-list/?type=hs&anon=4&start=896"

'''
from basic_functions import soupify

# This is just referencing my own code to load a url and turn it into a soup object
soup = soupify("https://www.nps.gov/mush/index.htm")
# this gets the address tag
x = soup.find("div", {'itemprop': "address"})
# this turns an iterator of all the strings (with extra whitespaces removed) 
#into a list of all the strings
strings = list(x.stripped_strings) 
# this concatenates the list of strings, separating them by a new line
address = "\n".join(strings)
print(address)

soup = soupify("https://www.nps.gov/state/al/index.htm")
parks = soup.find_all("li", {'class':"clearfix"})
park = parks[0]
print(str(park.h2.string))
print(str(park.h3.a.string))
print(str(park.h3.a["href"]))
print(str(park.p.string))
print(park.ul) # use this to get the links
 
def get_strings(tag):
    return(str(tag.string))


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

# assets_file = "/Users/zburchill/Downloads/PDF_STuff/PFD/PFDasset2.txt"
# new_assets_file = "/Users/zburchill/Downloads/PDF_STuff/PFD/PFDasset.txt"
# inner = assets_file+"_old"
# num_cols = 39
# 
# lines = ["|I140009550|,|s|,|N00027694|,|14|,|A|,| |,|S|,|Dreyfus/The Boston Co Sm/Md Cp Gr A|,|Dreyfus The Boston Co Small Mid Cap Growth Fund|,||,||,||,||,||,||,||,||,||,|A |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|I   |,||,,| |,| |,| |,,||,||,| |",
# "|I140009551|,|s|,|N00027694|,|14|,|A|,| |,|S|,|Great-West S&P SmallCap 600 Index Fund I|,|Great-West S&P SmallCap 600 Index Fund I|,||,||,||,||,||,||,||,||,||,|A |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|I   |,||,,| |,| |,| |,,||,||,| |",
# "|I140009552|,|s|,|N00027694|,|14|,|A|,| |,|S|,|PIMCO Total Return A|,|PIMCO Total Return Fund|,||,||,||,||,||,||,||,||,||,|A |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|I   |,||,,| |,| |,| |,,||,||,| |",
# "|I140009553|,|s|,|N00027694|,|14|,|A|,| |,| |,|UMB Bank, n.a.(St. Louis, MO)Type: Checking,|,|UMB Bank Checking|,||,||,||,||,||,||,||,||,||,|D |,,|  |,| |,|x|,| |,| |,| |,| |,|m |,|,|,|I   |,||,,| |,| |,| |,,||,||,| |",
# "|I140009554|,|s|,|N00027694|,|14|,|A|,| |,|S|,|MDY - SPDR S&P MidCap 400 ETF (NYSEArca)Strike price: $270.00 | CallExpires: 06/21/2014|,|SPDR S&P MidCap 400 ETF|,||,||,||,||,||,||,||,||,||,|A |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|III |,||,,| |,| |,| |,,||,||,| |",
# "|I140009555|,|s|,|N00027694|,|14|,|A|,| |,|S|,|SPY - SPDR S&P 500 ETF (NYSEArca)Strike price: $217.00 | CallExpires: 02/20/2015|,|SPDR S&P 500 ETF Trust|,||,||,||,||,||,||,||,||,||,|B |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|I   |,||,,| |,| |,| |,,||,||,| |",
# "|I140009556|,|s|,|N00027694|,|14|,|A|,| |,|S|,|EEM - iShares MSCI Emerging Markets (NYSEArca)Strike price: $46.00 | CallExpires: 10/18/2014|,|iShares MSCI Emerging Markets ETF|,||,||,||,||,||,||,||,||,||,|A |,,|  |,| |,| |,| |,|x|,| |,| |,|f |,|,|,|III |,||,,| |,| |,| |,,||,||,| |"]
# 
# 
# import re 
# with open(assets_file, 'r', encoding="ascii", errors="surrogateescape") as f:
#     s = re.sub(r"(?<!,)(?<!^)(?<!\\)(?<!\n)\|(?!(,|$|\n))", "\\|", f.read())
# 
# with open(new_assets_file, 'w', encoding="ascii", errors="surrogateescape") as f:
#     f.write(s)


# with open("/Users/zburchill/Desktop/delete.txt", "r") as f:
#     lines = f.read().splitlines()
# 
# s = ""
# d = {}
# for k, v in zip(lines[0::2], lines[1::2]):
#     if "sentence_tier" in k:
#         if k.replace("_sentence_tier","") not in d:
#             print(k)
#             print(k.replace("_sentence_tier",""))
#             x=0/0
#         else:
#             d[k.replace("_sentence_tier","")] = {"old": d[k.replace("_sentence_tier","")], "new": v}
#     else:
#         d[k] = v
# for k, v in d.items():
#     if isinstance(v, dict):
#         s += ",".join([k, v["old"], v["new"]])+"\n"
# print(s)
    




# with open(assets_file, 'r', encoding="ascii", errors="surrogateescape") as f:
#     lines = f.read().splitlines()
#     print("XXXXXXXXXXX")
#     bad_lines = {}
#     for j in range(0, len(lines)):
#         line = lines[j]
# #         if line.count("|") != 72:
#         first_quote = True    
#         bad_line = False        
#         i = 0
#         while (i < len(line)):
#             loc = line[i:].find("|")
#             if loc == -1:
#                 break
#             if first_quote:
#                 first_quote = False
#             else:
#                 if i+loc+1 >= len(line):
#                     break
#                 if line[i+loc+1] != ",":
#                     bad_line = True
#                     beginning = line[0:i+loc] + "\\"
#                     line = beginning + line[i+loc:]
#                     i = i + 1
#                 else:
#                     first_quote = True
#                     
#             i = i + loc + 1
#         if bad_line:
#             bad_lines[j] = line
#             
# new_lines = lines
# for k, v in bad_lines.items():
#     new_lines[k] = v
#     
# with open(assets_file+"guh", 'w', encoding="ascii", errors="surrogateescape") as f:
#     f.write("\n".join(new_lines))
# 
# print(len(bad_lines))
                    
# "|adfsa|asfdsa"  
# loc = 0, i = 0, 
# i = 1, loc = 5,     
                        
                    
                    






# from bs4 import BeautifulSoup
# from queue import Queue
# import requests, threading, datetime
# import os.path, re, json
# from warnings import warn
# # My stuff
# from basic_functions import clean_find, clean_find_all, join_urls, load_image, save_image,\
#     soupify
# 
# 
# 
# 
# 
# MAIN_PAGE = "https://efdsearch.senate.gov/search/"
# INTRO_PAGE = "https://efdsearch.senate.gov/search/home/"
# REQUEST_PAGE = "https://efdsearch.senate.gov/search/report/data/" #referer: https://efdsearch.senate.gov/search/
# cooks = {"_ga":"GA1.2.262298844.1536875553", "csrftoken":"sN5WMQgHPXq334JFtj80HkK440yQsYZ2Wmho6AXnXIYNFd0lonzHyUpvLA8FDTaa", "sessionid":"gASVGAAAAAAAAAB9lIwQc2VhcmNoX2FncmVlbWVudJSIcy4:1g8vqr:lMXRgjMZOvx1PE42VEzZMkzm5r4"}
# 
# big_boy={"draw": "1",
# "columns[0][data]": "0",
# "columns[0][name]": "",
# "columns[0][searchable]": "true",
# "columns[0][orderable]": "true",
# "columns[0][search][value]": "",
# "columns[0][search][regex]": "false",
# "columns[1][data]": "1",
# "columns[1][name]": "",
# "columns[1][searchable]": "true",
# "columns[1][orderable]": "true",
# "columns[1][search][value]": "",
# "columns[1][search][regex]": "false",
# "columns[2][data]": "2",
# "columns[2][name]": "",
# "columns[2][searchable]": "true",
# "columns[2][orderable]": "true",
# "columns[2][search][value]": "",
# "columns[2][search][regex]": "false",
# "columns[3][data]": "3",
# "columns[3][name]": "",
# "columns[3][searchable]": "true",
# "columns[3][orderable]": "true",
# "columns[3][search][value]": "",
# "columns[3][search][regex]": "false",
# "columns[4][data]": "4",
# "columns[4][name]": "",
# "columns[4][searchable]": "true",
# "columns[4][orderable]": "true",
# "columns[4][search][value]": "",
# "columns[4][search][regex]": "false",
# "order[0][column]": "1",
# "order[0][dir]": "asc",
# "order[1][column]": "0",
# "order[1][dir]": "asc",
# "start": "0",
# "length": "100",
# "search[value]": "",
# "search[regex]": "false",
# "report_types": "[]",
# "filer_types": "[4]",
# "submitted_start_date": "01/01/2012 00:00:00",
# "submitted_end_date": "",
# "candidate_state": "",
# "senator_state": "",
# "office_id": "",
# "first_name": "",
# "last_name": ""}
# 
# 
# 
# def browse_candidates(cur_sesh, mwtoken, state="", url=REQUEST_PAGE, headers = {"referer": MAIN_PAGE}):
#     
#     
#     
# #     
# #     outer_form = {"first_name": "", 
# #                   "last_name": "", 
# #                   "filer_type": "4", 
# #                   "candidate_state": state, 
# #                   "submitted_start_date": "", 
# #                   "submitted_end_date": "",
# #                   "csrfmiddlewaretoken": mwtoken}
#     
#     response_post = cur_sesh.post(url, data = big_boy, cookies = cur_sesh.cookies.get_dict(),
#                     headers = headers)
#     return(response_post)
#     
#     
# 
# def get_middleware_token(text):
#     soup_obj = BeautifulSoup(text)
#     l = clean_find_all(soup_obj, ['input',{'name': 'csrfmiddlewaretoken'}])
#     assert(len(l)==1)
#     return(l[0]["value"])
#     
# 
# outer_form = {"first_name": "", "last_name": "", "filer_type": "4", "candidate_state": "", "submitted_start_date": "", "submitted_end_date": "",
# "csrfmiddlewaretoken":"a"}
# 
# 
# 
# 
# payload = {"prohibition_agreement": "1"}
# 
# with requests.Session() as s:
#     first_get = s.get("https://efdsearch.senate.gov/search/home/")
#     payload["csrfmiddlewaretoken"] = get_middleware_token(first_get.text)
# 
#         
#     first_post = s.post("https://efdsearch.senate.gov/search/home/", 
#                     data = payload,
#                     headers = {"referer": "https://efdsearch.senate.gov/search/home/"})
#     
#     print(first_post.status_code)
#     print(first_post.cookies)
#     print("AAAAAAAA")
#     password_cookie_dict = requests.utils.dict_from_cookiejar(first_post.cookies)
#     print(password_cookie_dict)
#     
#     mwtoken = get_middleware_token(first_post.text)
#     resp = s.post(REQUEST_PAGE, data = big_boy, cookies = s.cookies.get_dict(),
#                      headers = {"referer": MAIN_PAGE, "X-CSRFToken": mwtoken})
#     print(resp)
#     print(resp.status_code)
#     print(resp.cookies)
#     print("OOOOOOOOOOOOOOOOOOOOOO\n\n\n\n")
#     print(resp.text)
#     jj = json.loads(resp.text)
#     print(jj)
#     print(len(jj["data"]))
# 
# 
# def get_cookies():
#     # The connection
#     with requests.Session() as s:
#         first_get = s.get("https://efdsearch.senate.gov/search/home/")
#         soup = BeautifulSoup(first_get.text)
#         print(soup.title)
#         crumb = s.cookies.get_dict()["crumb"]
#         
#         first_post = s.post(url_formatter.format(crumb), 
#                     json = payload,
#                     cookies = s.cookies.get_dict(),
#                     headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#                                "Content-Type": "application/json",
#                                "Accept": "*/*",
#                                "Accept-Encoding": "gzip, deflate",
#                                "Accept-Language": "en-US,en;q=0.9"})
#         
#         print(first_post)
#         print(first_post.headers)
#         print(first_post.status_code)
#         print(first_post.cookies)
#         password_cookie_dict = requests.utils.dict_from_cookiejar(first_post.cookies)
#     return(password_cookie_dict)



# import pickle
# 
# def load_obj(name ):
#     with open(name + '.pkl', 'rb') as f:
#         return pickle.load(f)    
#     
# 
# 
# MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
# 
# valid_ids = load_obj(MAIN_PATH+"all_series_ids")
# print(len(valid_ids))
# 
# with open(MAIN_PATH+"everything_log", "r", encoding="utf-8") as f:
#     lines = f.read().splitlines()
# print(len(lines))
# for e in lines[1907:1910]:
#     print(len(e))
#     print(e[0:2])
# good_lines = [e for e in lines if len(e) > 4 and e[0:2] == "('"]
# print(len(good_lines))
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


