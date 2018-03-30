'''
Created on Mar 16, 2018

@author: zburchill
'''
import urllib.parse
import logging, os, random, functools
import io # for loading images
from warnings import warn

### TO-DO: make sure all the PageScrapeExceptions in the code have the new arugments

#--------- These are the non-standard libraries ---------#
from bs4 import BeautifulSoup # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup
from PIL import Image  # Use "Pillow"! http://pillow.readthedocs.io/en/latest/installation.html
import requests # http://docs.python-requests.org/en/latest/user/install/#install


# ------------------------------ Real basic functions ------------------------------ #

# Turns navigable strings to normal ones
def get_string(soup_element):
    """ returns a bs4 element's NavigableString as a normal one """
    return(str(soup_element.string))

def remove_duplicate_elements(l):
    """ Right now, just `list(set(l))` """
    return (list(set(l)))


# ------------------------------ General loading / internet functions ------------------------------ #


# A generic custom exception so that I know when a failed to load properly or image failed to `Image.save()`
class PageScrapeException(Exception):
    def __init__(self, message, url="NotGiven"):
        self.expression = url
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
            warning_string = "Url '{url!s}' timed out. {n!s} tries until skipping".format(url=url_t, n=n_attempts-attempts)
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


# Note, doesn't let you pass additional args to `soupify`
def soupify_and_pass(url, f, *args, **kwargs):
    """This function soupifies a url, and passes it in as the first argument of a function.
    Note that it will not pass any extra arguments in to the `soupify` function as it is currently."""
    soup = soupify(url)
    return(f(soup, *args, **kwargs))
    

# ---------------------------------- soup functions ---------------------------------------- #

def soupify(url, safer=False, **kwargs):
    """ Returns a bs4 soup object from a url """
    response_for_url = try_to_urlopen(url, safer=safer, **kwargs)
    soup = BeautifulSoup(response_for_url.text)
    # turns the page into a soup object
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
    """ A decorator that let's you specify the number of requests before 
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
    
    def __init__(self, switch_proxies_after_n_calls):
        self.switch_after_n = switch_proxies_after_n_calls
        self.numcalls = self.proxy_index = 0
        self.proxies = self.get_proxies()
        
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
            proxy = { "https": "http://{ip}:{port}".format(**self.proxies[self.proxy_index]) }
            try:
                r = soupify(url, proxies = proxy, **kwargs)
                return(r)
            # If the proxy doesn't work:
            except (requests.exceptions.SSLError, requests.exceptions.ProxyError) as err:
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



