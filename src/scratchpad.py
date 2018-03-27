'''
Created on Mar 26, 2018

@author: zburchill
'''

'''
TO-DO: 
    - add threading locks!!!!!!!!!!!!
'''

import random, requests
from basic_functions import soupify
from warnings import warn
from basic_functions import PageScrapeException
import functools



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
    """ A class meant to store the proxy information for a function.
    
    If you want that function's docs, use `<that function>.__doc__`. """
    
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
print(ninja_soupify("https://google.com"))


