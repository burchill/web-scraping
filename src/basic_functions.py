'''
Created on Mar 16, 2018

@author: zburchill
'''
import urllib.parse
import logging, os
import io # for loading images

### TO-DO: make sure all the PageScrapeExceptions in the code have the new arugments

#--------- These are the non-standard libraries ---------#
from bs4 import BeautifulSoup # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup
from PIL import Image  # Use "Pillow"! http://pillow.readthedocs.io/en/latest/installation.html
import requests # http://docs.python-requests.org/en/latest/user/install/#install

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

# inspired by: 'https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/'
def get_proxies(**kwargs):
    """ 
    Returns a list of dicts of ssl proxies from sslproxies.org
    """
    proxies = []
    proxy_url='https://www.sslproxies.org/'
    soup = soupify(proxy_url, **kwargs)
    for row in soup.tbody.find_all("tr"):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })
    return(proxies)


# ---------------------------------- soup functions ----------------------------------------

def soupify(url_t, safer=False, **kwargs):
    """ Returns a bs4 soup object from a url """
    response_for_url = try_to_urlopen(url_t, safer=safer, **kwargs)
    soup = BeautifulSoup(response_for_url.text)
    # turns the page into a soup object
    return(soup)

# So, you can also pass a FUNCTION as an argument to `soup.find()` to search the tree
# This function just makes it so that it puts the arguments in `soup.find()` in the right way
# Don't fret about this too much if you aren't familiar with bs4
def clean_find(soup_t, args):
    """ Does `bs4.BeautifulSoup.find()`, but if the argument is a non-function variable, it unpacks the arguments """
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



