'''
Created on Mar 16, 2018

@author: zburchill
'''
import urllib.parse
import logging, os, random, functools, shelve, threading
import io # for loading images
from warnings import warn
import pickle, json, csv, shutil # for the PersistentDict

### TO-DO: make sure all the PageScrapeExceptions in the code have the new arugments

#--------- These are the non-standard libraries ---------#
from bs4 import BeautifulSoup # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup
from PIL import Image  # Use "Pillow"! http://pillow.readthedocs.io/en/latest/installation.html
import requests # http://docs.python-requests.org/en/latest/user/install/#install

import re, time

# ------------------------------ Real basic functions ------------------------------ #
# Loading and saving pickled stuff
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)     

# Turns navigable strings to normal ones
def get_string(soup_element):
    """ returns a bs4 element's NavigableString as a normal one """
    if soup_element.string:
        return(str(soup_element.string))
    else:
        return("")
    
# Outputs a normal string,
def get_full_string(soup_obj, start_index=None, end_index=None):
    """
    Concatenates all the strings of an element into a single string. 
    
    By default, returns the entire string. You can specify start and end indices.
    """
    string_list = list(soup_obj.strings)
    # Automatically converts to a normal string, I believe
    string_temp = "".join(string_list[start_index:end_index])
    return(string_temp)

def get_strings(soup_obj, remove_empty=False, stripped=True):
    """
    Returns a list of all the strings in a soup object, with the option to remove empty strings
    """
    if stripped: strings = [str(e) for e in soup_obj.stripped_strings]
    else:        strings = [str(e) for e in soup_obj.strings]
    if remove_empty: return [e for e in strings if e.strip() != ""]
    else: return strings 
    
def break_strings_by_line(soup_obj):
    """ 
    Returns a list of all the strings in a soup object, concatenated into lines
    """
    big_l = []
    temp_l = []
    for child in soup_obj.children:
        if child.name == "br":
            if temp_l:
                big_l+=["".join(temp_l)]
                temp_l = []
        else:
            if get_string(child).strip(): temp_l += [ get_string(child) ]
    if temp_l: big_l+= ["".join(temp_l)]
    return(big_l)


def remove_duplicate_elements(l):
    """ Right now, just `list(set(l))` """
    return (list(set(l)))

def join_urls(base, url, allow_fragments=True):
    return(urllib.parse.urljoin(base, url, allow_fragments))

def get_filename_from_url(url):
    path = urllib.parse.urlsplit(url).path
    _, basename = os.path.split(path)
    return(basename)


# ------------------------------ General saving functions ------------------------------------------ #



# from: https://code.activestate.com/recipes/576642/
# Because normal shelves suck
class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''

    def __init__(self, filename, flag='c', mode=None, format='json', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')
    
    def to_dict(self):
        return(dict(self))

class save_progress(object):
    """ Caches the key-value output of a function call, saving the whole thing to file every `n` calls,
    and then clearing out the RAM-intensive part of the cache.
    Uses `shelve` to store stuff. """
    
    def __init__(self, filename, f, save_after_n, make_new=False, use_regular_shelf=False):
        self._f = f
        self._save_after = save_after_n
        if make_new:
            os.remove(filename)
        if use_regular_shelf:
            self._shelf = shelve.open(filename)
        else:
            self._shelf = PersistentDict(filename, 'c', format='json')
        self.filename = filename
        
        # Not affected by args:
        self._writing_lock = threading.Lock()
        self._data_lock = threading.Lock() # I don't think I technically need a lock for editing a dictionary
        self._n = 0
        self.data = {}

    def __call__(self, *args, **kwargs):
        # If it needs to sync/save
        if self._n == self._save_after:
            self.sync_dict()
            self._n = 0
        with self._data_lock:
            k, v = self._f(*args, **kwargs)
            self.data[k] = v
        self._n += 1
            
    def sync_dict(self):
        """ Appends the dict cache to the shelf, saves the shelf, 
        and clears the dict cache """
        with self._writing_lock:
            with self._data_lock:
                # Sync shelf
                self.shelve_dict(self.data)
                self._shelf.sync()
                # Empty out dict
                del self.data
                self.data = {}
        
    def shelve_dict(self, d):
        """ Adds all items in the dict cache to the shelf """
        for k, v in d.items():
            if k in self._shelf:
                warn("{0}: {1} already in {2}".format(k, v, self.filename))
            try:
                self._shelf[k] = v
            except AttributeError as error_m:
                warn("{0} {1} has: {2}".format(k, v, error_m))
        
    def close(self):
        self.sync_dict()
        print("THE SAVED PROGRESS HAS {!s} ENTRIES---------------".format(len(self._shelf.items())))
        self._shelf.close()
    
    @staticmethod
    def identity(e):
        """ for functions that already output a key value tuple """
        return(e)


# ------------------------------ General loading / internet functions ------------------------------ #

# A generic custom exception so that I know when a failed to load properly or image failed to `Image.save()`
class PageScrapeException(Exception):
    "A generic custom exception so that I know when a failed to load properly or image failed to `Image.save()`"
    def __init__(self, message, url="NotGiven"):
        self.expression = url
        self.message = message
# For when I want to say that this page shouldn't be scraped again, basically
class BadPageException(Exception):
    "For when I want to say that this page shouldn't be scraped again, basically"
    def __init__(self, message, identifier="NotGiven"):
        self.expression = identifier
        self.message = message

# This is a function that tries to get a response from a url, trying to do so `n_attempts` number of times
def try_to_urlopen(url_t, timeout_sec=30, n_attempts=2, new_header=True, 
                   safer=False, # ignore_ssl_errors=True,
                   custom_header={'User-Agent': 'Mozilla/5.0'},
                   **kwargs):
    """ This function tries to retrieve a url with `requests.get` a specified number of times for specified lengths of time,
    and uses a customized header if it gets a 403 error. """
    attempts = 0
    # I have an option for when you think the URL might be really wonky. Doesn't really happen with 4chan
    if safer:
        url_t=urllib.parse.quote(url_t,safe=":/")
    while attempts <= n_attempts:
        try:
            if new_header:
                r = requests.get(url_t, timeout=timeout_sec, headers=custom_header, **kwargs)
                # check to see what the status was
                r.raise_for_status()
                break
            else:
                r = requests.get(url_t, timeout=timeout_sec, **kwargs)
                # check to see if the status sucked
                r.raise_for_status()
                break
        except requests.exceptions.HTTPError as err:
            # If you get a 'forbidden' (403) error, sometimes its because they can tell you're using a Python "browser"
            if err.response.status_code == 403:
                # If you get that error, you can generally avoid it by changing your headers
                if new_header:
                    raise requests.exceptions.HTTPError("Modifying the header for '{url!s}' couldn't fix 403 problem: {error!s}".format(url=url_t, error=err))
                else: new_header = True
            else:
                raise
        except requests.exceptions.Timeout:
            attempts += 1
            warning_string = "Url '{url!s}' timed out. {n!s} tries until skipping".format(url=url_t, n=n_attempts-attempts+1)
            logging.warning(warning_string)
    if attempts > n_attempts:
        raise requests.exceptions.Timeout("URL '{url!s}' timed out {n!s} times, at {sec!s} sec. each try.".format(url=url_t, n=n_attempts, sec=timeout_sec))
    return(r)

# Loads an image
def load_image(image_url, *args, **kwargs):
    """ Tries to open and save an image """
    image_file_response = try_to_urlopen(urllib.parse.quote(image_url, safe=":/"), *args, **kwargs)
    image_file = io.BytesIO(image_file_response.content)
    image_file.seek(0)
    im = Image.open(image_file)
    return(im)

# Saves an image
def save_image(image, path):
    image.save(path)

# Note, doesn't let you pass additional args to `soupify`
def soupify_and_pass(url, f, *args, **kwargs):
    """This function soupifies a url, and passes it in as the first argument of a function.
    Note that it will not pass any extra arguments in to the `soupify` function as it is currently."""
    soup = soupify(url)
    return(f(soup, *args, **kwargs))
    
# Note, doesn't let you pass additional args to `soupify`
def ninja_soupify_and_pass(ninja_soup_f, url, f, *args, **kwargs):
    """This function does a function on a url, and passes it in as the first argument of another function.
    Note that it will not pass any extra arguments in to the `soupify` function as it is currently."""
    soup = ninja_soup_f(url)
    return(f(soup, *args, **kwargs))

# ---------------------------------- soup functions ---------------------------------------- #

def soupify(url, safer=False, **kwargs):
    """ Returns a bs4 soup object from a url """
    response_for_url = try_to_urlopen(url, safer=safer, **kwargs)
    soup = BeautifulSoup(response_for_url.text)
    # turns the page into a soup object
    return(soup)

# Uses selenium and ChromeDriver (path hardcoded to '../chromedriver')
def js_soupify(url, title_text = None, wait_time = 10, chromedriver_path = '../chromedriver'):
    """ 
    A facsimile of soupify for tricking simple javascript-requiring sites, like those that use cloudflare.
    Essentially it uses selenium and ChromeDriver and opens up the url, optionally waits, and then downloads the HTML.
    If `title_text` is set, it will wait `wait_time` seconds checking if the title of the page 
        contains that text, and if it never does, it throws an error.
    """
    from selenium import webdriver
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chromedriver_path, chrome_options = options)  # Optional argument, if not specified will search path.
    driver.get(url)
    
    if title_text is not None:
        WebDriverWait(driver, wait_time).until(
            EC.title_contains(title_text)
        )
        if not EC.title_contains(title_text):
            actual_title = driver.find_element_by_id("title").text
            raise BadPageException("Title '{}' did not contain '{}' in alotted time ({})".format(actual_title, title_text, url))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return(soup) 

# So, you can also pass a FUNCTION as an argument to `soup.find()` to search the tree
# This function just makes it so that it puts the arguments in `soup.find()` in the right way
# Don't fret about this too much if you aren't familiar with bs4
def clean_find(soup_t, args):
    """ Does `bs4.BeautifulSoup.find()`, but if the argument is a non-function variable, it unpacks the arguments.
    E.g.: clean_find(soup, ['div',{'class': 'cc-newsbody'}]) """
    # for Python 3.x but before 3.2, use: `if hasattr(args, '__call__'):`
    if callable(args):
        return(soup_t.find(args))
    else:
        return(soup_t.find(*args))
    
# the 'soup.find_all' version of 'clean_find'
def clean_find_all(soup_t,args):
    """ Does the same thing as `clean_find()`, but for `bs4.BeautifulSoup.find_all()` """
    # for Python 3.x but before 3.2, use: `if hasattr(args, '__call__'):`
    if callable(args):
        return(soup_t.find_all(args))
    else:
        return(soup_t.find_all(*args))
    
    
# ---------------------------------- 'Ninja' functions ---------------------------------------- #
# These functions are built to basically sneak around websites that detect and block web-scraping
# There are two ways I made this work: 
#    The first is through more extendable decorators:`proxy_decorator()` and `manage_proxies()`. 
#        Examples for how to use those are shown farther below.
#    The second is just a prebuilt class called `ninja_soupify_simpler()` which is a less complicated,
#        but more rigid version.

def proxy_decorator(switch_after_n):
    """ A decorator that lets you specify the number of requests before 
    switching proxies for `manage_proxies` and keeps the decorator syntactic sugar."""
    def inner_decorator(fn):
        functools.wraps(fn)
        return(manage_proxies(fn, switch_after_n))
    return inner_decorator

class manage_proxies(object):
    """ A class meant to store the proxy information for a function.
    
    If you want that function's docs, use `<that function>.__doc__`. """
    
    # To make this class a decorator itself, just remove `switch_proxies_after_n_calls` from `__init__`
    #    (maybe add it in via as a default arg to `f`) 
    def __init__(self, f, switch_proxies_after_n_calls):
        self.__f = f
        self._switch_after_n = switch_proxies_after_n_calls
        self.__numcalls = self.proxy_index = 0
        self.proxies = self.get_proxies()
        functools.update_wrapper(self, f) #
    
    def __call__(self, *args, **kwargs):
        self.__numcalls += 1
        if self.__numcalls % self._switch_after_n == 0:
            self.proxy_index = self.get_random_proxy_index()
        return self.__f(*args, **kwargs)
    
    def count(self):
        "Return the number of times the function f was called."
        return self.__numcalls
    
    def get_random_proxy_index(self):
        "Return a random index from the proxy list"
        return random.randint(0, len(self.proxies) - 1)
    
    # inspired by: 'https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/'
    @staticmethod
    def get_proxies(**kwargs):
        """ 
        Returns a list of dicts of ssl proxies from sslproxies.org
        """
        proxies = []
        proxy_url = 'https://www.sslproxies.org/'
        soup = soupify(proxy_url, **kwargs)
        for row in soup.tbody.find_all("tr"):
            proxies.append({
                'ip':   row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })
        return(proxies)
  
# An example of how to use `proxy_decorator()` and `manage_proxies()`
# # Only does https currently
# @proxy_decorator(SWITCH_PROXIES_AFTER_N_REQUESTS)
# def ninja_soupify(url, tolerance=10, **kwargs):
#     dead_proxy_count = 0
#     # if you burn through too many proxies, there's probably a problem
#     while dead_proxy_count <= tolerance:
#         # If for some reason there isn't a proxies list, make one
#         if not ninja_soupify.proxies: 
#             ninja_soupify.proxies = ninja_soupify.get_proxies()
#         # If the proxy index needs to be updated
#         if ninja_soupify.proxy_index >= len(ninja_soupify.proxies):
#             ninja_soupify.proxy_index = ninja_soupify.get_random_proxy_index()
#         # Make a dict that Requests can use
#         proxy = { "https": "http://{ip}:{port}".format(**ninja_soupify.proxies[ninja_soupify.proxy_index]) }
#         try:
#             r = soupify(url, proxies = proxy, **kwargs)
#             return(r)
#         # If the proxy doesn't work:
#         except (requests.exceptions.SSLError, requests.exceptions.ProxyError) as err:
#             warn("Proxy {d[ip]}:{d[port]} deleted because of: {error_m!s}".format(d = ninja_soupify.proxies[ninja_soupify.proxy_index], error_m=err))
#             del ninja_soupify.proxies[ninja_soupify.proxy_index]
#             dead_proxy_count += 1
#     raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))
         
class ninja_soupify_simpler(object):
    """ A simpler, more rigid version of what `proxy_decorator` leads into.
    This class basically serves as a function that stores proxy information and rotates
    through using different ones while using `soupify()`. """
    
    def __init__(self, switch_proxies_after_n_calls, text_counts_as_ban=None):
        self.switch_after_n = switch_proxies_after_n_calls
        self.numcalls = self.proxy_index = 0
        self.proxies = self.get_proxies()
        self.bantext = text_counts_as_ban
        
    def __call__(self, url, tolerance=10, **kwargs):
        self.numcalls += 1
        if self.numcalls % self.switch_after_n == 0:
            self.proxy_index = self.get_random_proxy_index()        
        dead_proxy_count = 0
        # if you burn through too many proxies, there's probably a problem
        while dead_proxy_count <= tolerance:
            # If for some reason there isn't a proxies list, make one
            if not self.proxies: 
                self.proxies = self.get_proxies()
            # If the proxy index needs to be updated
            if self.proxy_index >= len(self.proxies):
                self.proxy_index = self.get_random_proxy_index()
            # Make a dict that Requests can use
            # Used to be: proxy = { "https": "http://{ip}:{port}".format(**self.proxies[self.proxy_index])}
            proxy = { "https": "http://{ip}:{port}".format(**self.proxies[self.proxy_index])}
            try:
                r = soupify(url, proxies = proxy, **kwargs)
                if self.bantext is not None and self.bantext in r.text:
                    raise requests.exceptions.SSLError("MYEH")
                return(r)
            # If the proxy doesn't work:
            except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                warn("Proxy {d[ip]}:{d[port]} deleted because of: {error_m!s}".format(d = self.proxies[self.proxy_index], error_m=err))
                del self.proxies[self.proxy_index]
                dead_proxy_count += 1
        raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))
        
    def get_random_proxy_index(self):
        "Return a random index from the proxy list"
        return random.randint(0, len(self.proxies) - 1)
    
    # inspired by: 'https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/'
    @staticmethod
    def get_proxies(**kwargs):
        """ 
        Returns a list of dicts of ssl proxies from sslproxies.org
        """
        proxies = []
        proxy_url = 'https://www.sslproxies.org/'
        soup = soupify(proxy_url, **kwargs)
        for row in soup.tbody.find_all("tr"):
            proxies.append({
                'ip':   row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })
        return(proxies)

# Example:
# ninja_soupify = ninja_soupify_simpler(SWITCH_PROXIES_AFTER_N_REQUESTS)
# print(ninja_soupify("https://google.com"))


class Proxifier(object):
    def __init__(self, proxsup, switch_proxies_after_n_calls=15,
                 n_proxies_on_deck = 10, raise_err_fn = None,
                 min_sleep = 0):
        self.switch_after_n = switch_proxies_after_n_calls
        self.numcalls = self.proxy_index = 0
        self.ps = proxsup
        self.proxies = self.ps.get_proxies()
        self.wait_for_new_proxies = 20
        self.n_on_deck = n_proxies_on_deck
        self._i_got_this = False
        self.err_fn = (lambda x: None) if raise_err_fn is None else raise_err_fn
        self.min_sleep = min_sleep
        self._lock = threading.Lock() # for deleting proxies
    
    def delete_proxy(self, proxy):
        with self._lock:
            if proxy in self.proxies:
                del self.proxies[self.proxies.index(proxy)]  
        self.get_random_proxy_index()
    
    def get_more_proxies(self):
        if self._i_got_this:
            return()
        self._i_got_this = True
        try:
            self.proxies += self.ps.get_proxies()
        finally:
            self._i_got_this = False
        
    def wait_for_more_proxies(self):
        "Makes sure no thread is already getting more proxies, and waits for them"
        if not self._i_got_this:
            self.get_more_proxies()
            if not self.proxies:
                raise Exception("Tried to get more proxies, but couldn't!")
            else:
                return(None)
        c = self.wait_for_new_proxies
        while c > 0 and not self.proxies:
            time.sleep(1)
        if not self.proxies: 
            raise Exception("Waited for {} s for proxies but none came".format(self.wait_for_new_proxies))
        else:
            return(None)

    def __call__(self, url, tolerance=10, **kwargs):
        time.sleep(self.min_sleep)
        
        self.numcalls += 1
        if self.numcalls % self.switch_after_n == 0:
            self.proxy_index = self.get_random_proxy_index()  
                  
        dead_proxy_count = 0
        # if you burn through too many proxies, there's probably a problem
        while dead_proxy_count <= tolerance:
            
            if len(self.proxies) < self.n_on_deck and not self._i_got_this:
                self.get_more_proxies()
            
            # If for some reason there isn't a proxies list, make one   
            if len(self.proxies) == 0:
                self.wait_for_more_proxies()    
                
            # If the proxy index needs to be updated
            if self.proxy_index >= len(self.proxies):
                self.proxy_index = self.get_random_proxy_index()
            
            # Make a dict that Requests can use
            proxy_dict = self.proxies[self.proxy_index]
            # Used to be: proxy = { "https": "http://{ip}:{port}".format(**self.proxies[self.proxy_index])}
            proxy = { "https": "http://{ip}:{port}".format(**proxy_dict)}
            
            try:
                r = soupify(url, proxies = proxy, **kwargs)
                self.err_fn(r) # should raise BadPageException
                return(r)
            
            # If the proxy doesn't work:
            except (requests.exceptions.SSLError, requests.exceptions.ProxyError, 
                    requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                    requests.exceptions.HTTPError, BadPageException) as err:
                s = "Proxy {p} deleted because of: {error_m!s}".format(p=proxy["https"], error_m=err)
                warn(s)
                self.delete_proxy(proxy_dict)
                dead_proxy_count += 1
            
        raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))
        
    def get_random_proxy_index(self):
        "Return a random index from the proxy list"
        if len(self.proxies) == 0:
            self.wait_for_more_proxies()
        return random.randint(0, len(self.proxies) - 1)


class ProxySupplier(object):
    def __init__(self, url):
        self.proxy_url = url
    
    def rows_from_soup(self, soup_obj):
        return(soup_obj.tbody.find_all("tr"))
    
    def proxy_from_row(self, row_soup_obj):
        proxy = {
            'ip':   row_soup_obj.find_all('td')[0].string,
            'port': row_soup_obj.find_all('td')[1].string
            }
        return(proxy)
    
    def _get_proxies(self, soup_obj):
        proxies = []
        for row in self.rows_from_soup(soup_obj):
            proxies.append(self.proxy_from_row(row))
        return(proxies)
        
    def get_proxies(self, **kwargs):
        soup = soupify(self.proxy_url, **kwargs)
        proxies = self._get_proxies(soup)
        return(proxies)
        
class HideMyNamePS(ProxySupplier):
    def __init__(self, url="https://hidemyna.me/en/proxy-list/?type=hs&anon=4"):
        self.proxy_url = url
        self.og_url = url
    
    def get_proxies(self):
        soup = js_soupify(self.proxy_url, title_text="Free")
        proxies = self._get_proxies(soup)
        arrow = clean_find(soup, ['li',{'class': 'arrow__right'}])
        if arrow is None:
            self.proxy_url = self.og_url
            warn("HideMyNamePS going back to original URL")
        else:
            self.proxy_url="https://hidemyna.me"+arrow.a["href"]
        return(proxies)


# print(HideMyNamePS().get_proxies())
# 
# 
# SSLProxies = ProxySupplier('https://www.sslproxies.org/')        
# HideMyName = ProxySupplier('https://hidemyna.me/en/proxy-list/?type=hs&anon=4',
#                            count_fn = hidemyname_pager)
# 
#     




    
    