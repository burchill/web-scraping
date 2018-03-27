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


# class countcalls_old(object):
#     "Decorator that keeps track of the number of times a function is called."
#     
#     __instances = {}
#     
#     def __init__(self, f):
#         self.__f = f
#         self.__numcalls = 0
#         countcalls_old.__instances[f] = self
#     
#     def __call__(self, *args, **kwargs):
#         self.__numcalls += 1
#         return self.__f(*args, **kwargs)
#     
#     def count(self):
#         "Return the number of times the function f was called."
#         return countcalls_old.__instances[self.__f].__numcalls
#     
#     # inspired by: 'https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/'
#     @staticmethod
#     def get_proxies(self, **kwargs):
#         """ 
#         Returns a list of dicts of ssl proxies from sslproxies.org
#         """
#         proxies = []
#         proxy_url = 'https://www.sslproxies.org/'
#         soup = soupify(proxy_url, **kwargs)
#         for row in soup.tbody.find_all("tr"):
#             proxies.append({
#                 'ip':   row.find_all('td')[0].string,
#                 'port': row.find_all('td')[1].string
#             })
#         return(proxies)
# 
#     @staticmethod
#     def counts():
#         "Return a dict of {function: # of calls} for all registered functions."
#         return dict([(f.__name__, countcalls_old.__instances[f].__numcalls) for f in countcalls_old.__instances])

# class countcalls(object):
#     "Decorator that keeps track of the number of times a function is called."
#     
#     __instances = {}
#     
#     def __init__(self, f):
#         self.__f = f
#         self.__numcalls = 0
#         countcalls.__instances[f] = self
#     
#     def __call__(self, *args, **kwargs):
#         self.__numcalls += 1
#         return self.__f(*args, **kwargs)
#     
#     def count(self):
#         "Return the number of times the function f was called."
#         return countcalls.__instances[self.__f].__numcalls
#     
#     # inspired by: 'https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/'
#     @staticmethod
#     def get_proxies(self, **kwargs):
#         """ 
#         Returns a list of dicts of ssl proxies from sslproxies.org
#         """
#         proxies = []
#         proxy_url = 'https://www.sslproxies.org/'
#         soup = soupify(proxy_url, **kwargs)
#         for row in soup.tbody.find_all("tr"):
#             proxies.append({
#                 'ip':   row.find_all('td')[0].string,
#                 'port': row.find_all('td')[1].string
#             })
#         return(proxies)
# 
#     @staticmethod
#     def counts():
#         "Return a dict of {function: # of calls} for all registered functions."
#         return dict([(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances])
    
    
class manage_proxies(object):
    "Decorator "
    
    def __init__(self, f):
        self.__f = f
        self.__numcalls = 0
        self.proxy_index = 0
        self.proxies = self.get_proxies()
        self.test =["A"]
    
    def __call__(self, *args, **kwargs):
        global SWITCH_PROXIES_AFTER_N_REQUESTS
        self.__numcalls += 1
        if self.__numcalls % SWITCH_PROXIES_AFTER_N_REQUESTS == 0:
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
    


    
    
@manage_proxies
def x():
    print("THIS IS X")
    print(x.count())

@manage_proxies
def g():
    print("THIS IS G")
    print(g.count())

x()
x()
x()



#     print(g.proxies)

g()
g()
g()






# Only does https currently
@manage_proxies
def ninja_soupify(url, tolerance=10, **kwargs):
    dead_proxy_count = 0
    # if you burn through too many proxies, there's probably a problem
    while dead_proxy_count <= tolerance:
        # If for some reason there isn't a proxies list, make one
        if not ninja_soupify.proxies: 
            ninja_soupify.proxies = ninja_soupify.get_proxies()
        # If the proxy index needs to be updated
        if ninja_soupify.proxy_index >= len(ninja_soupify.proxies):
            ninja_soupify.proxy_index = ninja_soupify.get_random_proxy_index()
        # Make a dict that Requests can use
        proxy = { "https": "http://{ip}:{port}".format(**ninja_soupify.proxies[ninja_soupify.proxy_index]) }
        try:
            r = soupify(url, proxies = proxy, **kwargs)
            return(r)
        # If the proxy doesn't work:
        except (requests.exceptions.SSLError, requests.exceptions.ProxyError) as err:
            warn("Proxy {d[ip]}:{d[port]} deleted because of: {error_m!s}".format(d = ninja_soupify.proxies[ninja_soupify.proxy_index], error_m=err))
            del ninja_soupify.proxies[ninja_soupify.proxy_index]
            dead_proxy_count += 1
    raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))


@manage_proxies
def shit():
    print("________________")
    print(shit.proxies)
    print(shit.proxy_index)
    print(len(shit.proxies))
    print(shit.test)
    pass


print(shit.proxies)
print(shit.proxy_index)
print(len(shit.proxies))
print(shit.test)

shit()


print(ninja_soupify.proxies)
print(ninja_soupify.proxy_index)
print(len(ninja_soupify.proxies))
print(ninja_soupify.test)

# ninja_soupify.proxies = [{"ip": "10", "port":"80"}]
# ninja_soupify.proxy_index = 0
s=ninja_soupify("https://google.com")
print(s)
s=ninja_soupify("https://google.com")
print(s)
s=ninja_soupify("https://google.com")
print(s)
         

