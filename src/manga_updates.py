'''
THE NEW VERSION!

@author: zburchill

proxy stuff inspired by: https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/
'''
import operator
import re
import csv
import random, requests

# for threading
import threading
from queue import Queue
import time
from basic_functions import soupify, PageScrapeException, ninja_soupify_simpler
from bs4 import Tag
from warnings import warn
from bs4.element import NavigableString
from string import ascii_uppercase
from itertools import combinations_with_replacement

import pickle
from functools import wraps # for the decorators


'''
TO-DO:
     
     * make the constants all good (ie series_metadata_url_format and NUMBER_OF_NONALPHA_MANGA_PAGES)
     * make `get_manga_ids_from_table` analogous to `get_issue_info_from_table` in the sense that it takes a soup object
     
'''


    
def random_proxy():
    global Proxies_list
    return random.randint(0, len(Proxies_list) - 1)

# Only does https currently
def ninja_soupify(url, tolerance=10, **kwargs):
    # If it's time to switch to a new proxy, do so
    global Proxies_list
    global SWITCH_PROXIES_AFTER_N_REQUESTS
    global Proxy_index
    global Request_counter
    if Request_counter % SWITCH_PROXIES_AFTER_N_REQUESTS == 0:
        Proxy_index = random_proxy()
    dead_proxy_count = 0
    while dead_proxy_count <= tolerance:
        # If for some reason there isn't a proxies list, make one
        if not Proxies_list: Proxies_list = get_proxies()
        proxy = { "https": "http://{ip}:{port}".format(**Proxies_list[Proxy_index]) }
        try:
            r = soupify(url, proxies = proxy, **kwargs)
            Request_counter += 1
            return(r)
        except (requests.exceptions.SSLError, requests.exceptions.ProxyError) as err:
            warn("Proxy {d[ip]}:{d[port]} deleted because of: {error_m!s}".format(d=Proxies_list[Proxy_index], error_m=err))
            del Proxies_list[Proxy_index]
            Proxy_index = random_proxy()
            dead_proxy_count += 1
    raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))
         
            
        
        
        
        

    


# ------------------------------------------ Basic functions -----------------------------------
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)     
 
def is_error_tag(tag):
    """
    A function for `bs4.find()` that searches for an element that indicates a manga page doesn't exist. 
    I.e. it finds the element that holds "Error" in "Error: You specified an invalid series id."
    """    
    try: return("tab_middle" in tag["class"] and tag.name=="td" and "Error" in tag.string)
    except KeyError: return(False)

def is_page_count(tag):
    """A function for `bs4.find()`. Returns the td element that has the page count
    """
    try: return "specialtext" in tag["class"] and "center" in tag["align"] and "33%" in tag["width"] and tag.name=="td"
    except KeyError: return(False)
    
def check_whether_series_valid(soup):
    """
    Checks a soup object and checks if it's a "real" manga series page or not
    """
    return(soup.find(is_error_tag) is None)

def assert_category_tag(tag):
    """
    Asserts a certain bs4 element (ie tag) is one that contains a category
    """
    try:
        assert tag["class"]==["sContent"] and tag.name=="div"
    except AssertionError as errorm:
        print("Category tag is not a category: ")
        print(tag)
        raise AssertionError("Category assertion error: '{0}'\nCategory tag is a :'{1}'".format(str(errorm), tag.name))

def get_next_sibling_tag(tag):
    """
    Will go through a BS4 tree, looking for the next siblings (ignoring intervening strings)
    
    Currently used to move through categories.
    """
    next_thing = tag.next_sibling
    while next_thing is not None:
        if isinstance(next_thing, Tag):
            return(next_thing)
        else:
            next_thing = next_thing.next_sibling
    return(next_thing)

def get_strings(soup_obj, start_index=None, end_index=None):
    """
    Concatenates all the strings of an element into a single string. 
    
    By default, returns the entire string. You can specify start and end indices.
    """
    string_list = list(soup_obj.strings)
    string_temp = "".join(string_list[start_index:end_index])
    return(string_temp)

def get_soup_row_list(soup_obj):
    """
    Returns the rows that contain updates (for a series)
    """
    table = soup_obj.find("td",{'class','releasestitle'}).parent.parent
    rows = list(table.find_all("tr"))
    # Drop the title row and drop the empty first row
    return(rows[2:])
def soup_row_to_string_list(soup_row):
    """
    Turns the values in row of updates (bs4 element) into a list of strings if they aren't already
    """
    row_l = [get_strings(e) for e in soup_row if not isinstance(e, NavigableString)]
    return(row_l)

def get_page_count(soup_obj):
    """
    Returns the max number of pages from a soupified page.
    """
    # gets the td element with the page counts in it
    td_obj=soup_obj.find(is_page_count)
    try:
        # gets the strings of its contents
        s_temp=td_obj.contents[0].string
        # gets the {num} in 'Pages ({num})'
        return(int(s_temp[7:].split(")")[0]))
    except AttributeError:
        return(None)




######################## 


def get_manga_ids_from_table(url):
    """
    Gets the id numbers associated with each manga from the table in a url.
    
    I.e. at urls like: "https://www.mangaupdates.com/series.html?page={0}&letter={1}&perpage=100&filter=some_releases&type=manga"
    """
    s = ninja_soupify(url)
    # Finds the table that holds all the rows of manga
    table = s.find("table",{"class":"series_rows_table"})
    # Removes the first 2 rows (cuz they're titles)
    #     and the last six rows (i forget why)
    rows = table.find_all("tr")[2:-6]
    manga_ids = [e.find("td").a["href"].split("=")[-1] for e in rows]
    if manga_ids == []:
        raise PageScrapeException(message="No manga id rows were found on page!", url=url)
    return(manga_ids)

def collect_valid_series():
    """
    Collects the "series IDs" for all manga series that meet certain qualifications and returns them in a list.
    
    These qualifications are specified in the `url_format` strings via the way the site filters rows: 
        they must be "manga" and they must have "some releases"
    """
    # This is the format of the urls that let us browse all the manga by first letter
    url_format          = "https://www.mangaupdates.com/series.html?page={0}&letter={1}&perpage=100&filter=some_releases&type=manga"
    # In order to get those that don't begin with a letter, we use this format
    nonalpha_url_format = "https://www.mangaupdates.com/series.html?page={0}&perpage=100&filter=some_releases&type=manga"
    all_manga_ids = []
    
    # go through all the pages of manga that don't start with alphabetic characters
    #    currently there are 4 
    for counter in range(1, NUMBER_OF_NONALPHA_MANGA_PAGES):
        try:
            all_manga_ids += get_manga_ids_from_table(nonalpha_url_format.format(counter))
        except PageScrapeException as err:
            # I know for a fact that there are "non-alpha" manga. If I can't find any, something has gone horribly wrong
            raise AssertionError("There should be non-alphabetical manga to load! "+err.url)
    
    # Due to limitations of how many pages can be displayed for any given letter, it's easier to go by
    #    two letter combinations, e.g. manga that start with "AB", etc.
    # Just trust me, alright?  This makes it easier/possible, believe it or not
    letterpairs = list(combinations_with_replacement(ascii_uppercase,2))
    letterpairs[:] = [e[0]+e[1] for e in letterpairs]
    for letter in letterpairs:
        try:
            all_manga_ids += get_manga_ids_from_table(url_format.format(1,letter))
        except PageScrapeException:
            # Sometimes there aren't manga that start with certain characters
            print("no "+letter+" values")
        # Gets the number of pages that start with that letter combo...
        page_count = get_page_count(ninja_soupify(url_format.format(1,letter)))
        if page_count:
            # ...and puts them on the queue too
            for i in range(2, page_count+1):
                try:
                    all_manga_ids += get_manga_ids_from_table(url_format.format(i,letter))
                except PageScrapeException:
                    print("no {0} values for page #{1!s}".format(letter, i))
    return(all_manga_ids)




def get_all_categories(soup_obj):
    """
    Given a soupified page, returns dict of categories.
    """
    d={}
    categories = soup_obj.find_all('div',{'class','sCat'})
    for category in categories:
        name=str("-".join(category.strings))
        if name in d:
            warn("Already a category named"+name+", overriding.")
        d[name] = get_next_sibling_tag(category)
    return(d)
        


    


#######################  Data processing functions ########################################################
# These functions get the HTML data for the various categories of information on a series' page,
#    e.g., "Completely Scanlated?", "Author(s)", "Artist(s)", etc.,
# and turn process them into more useable formats.
# CAUTION! In order to use the decorator for all these classes, the first argument should also be named "soup_obj"

# If you don't know what a decorator is, read: https://realpython.com/primer-on-python-decorators/
def check_tag_is_category_decorator(function):
    """
    A decorator for the category cleaning functions (e.g., 'clean_genre_category()')
    that just checks to make sure the element being "cleaned" is in fact a "category" soup element.
    
    It either needs the first argument to be the soup element, or the soup element needs to be a named keyword, 'soup_obj'.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if args:
            assert_category_tag(args[0])
        else:
            assert_category_tag(args["soup_obj"])
        return function(*args, **kwargs)
    return wrapper

@check_tag_is_category_decorator
def clean_genre_category(soup_obj):
    """Returns list of strings of genre names"""
    genres = [e.string for e in soup_obj.find_all("a")]
    if not genres:
        assert soup_obj.string.strip() == "N/A"
    genres = genres[:-1] # Drop the "see more thing")
    return(genres)
@check_tag_is_category_decorator
def clean_categories_category(soup_obj, get_only_final_score=True):
    """Returns a list of pairs: x = category string, y = final score"""
    categories = soup_obj.find_all("li")
    categories[:] = [(e.string, int(e.a["title"].split()[1])) for e in categories]
    if not categories:
        assert soup_obj.string.strip()=="N/A"
    return(categories)
@check_tag_is_category_decorator
def clean_list_stats_category(soup_obj):
    """Returns dicts of string->int"""
    d={}
    type_of_lists = [e.next_sibling.split()[0]  for e in soup_obj.find_all("b")]
    stats = [int(e.string) for e in soup_obj.find_all("b")]
    for key, val in zip(type_of_lists,stats):
        d[key]=val
    assert len(type_of_lists) == len(stats)
    if not (len(stats) >= 4 and len(stats) <= 6):
        print("TTTTTTTTTT")
        print(soup_obj)
        assert 1==2
    return(d)
@check_tag_is_category_decorator
def clean_forum_category(soup_obj):
    """Returns (<int, # of topics>, <int, # of posts>)"""
    text_list=soup_obj.contents[0].split()
    pair=(int(text_list[0]), int(text_list[2]))
    return(pair)
@check_tag_is_category_decorator
def clean_user_rating_category(soup_obj):
    """Returns a dictionary of:
        - The average rating <float>
        - The Bayesian average rating <float>
        - The number of votes <int>
        - The distribution of votes <a dict of string keys and int values>"""
    if get_strings(soup_obj).strip() == "N/A":
        return("N/A")
    first_line=soup_obj.next_element.split()
    reg_avg=float(first_line[1])
    num_votes=int(first_line[4][1:])
    bayesian_avg = float(soup_obj.next_element.next_element.next_element.next_element.string.strip()) # Oh lawdy, there's a better way, im sure
    d={}
    scores_n_shit = [e for e in get_strings(soup_obj).split("\n")[1:] if e != ""]
    for score, vote_string in list(zip(scores_n_shit,scores_n_shit[1:]))[::2]:
        num_votes_per=int(vote_string.split("(")[1].split()[0])
        d[score]=num_votes_per
    if sum(d.values()) != num_votes:
        raise AssertionError("Summed number of votes ({0}) does not equal total votes ({1})!".format(sum(d.values()),num_votes))
    big_d={}
    big_d["Average"]=reg_avg
    big_d["Total votes"]=num_votes
    big_d["Bayesian Average"]=bayesian_avg
    big_d["Distribution"]=d
    return(big_d)
@check_tag_is_category_decorator
def clean_anime_category(soup_obj):
    """
    Returns `True`/`False` if there was an anime.
    """
    return(get_strings(soup_obj).strip() != "N/A")
@check_tag_is_category_decorator
def clean_status_category(soup_obj):
    """ 
    Returns the status of a manga.
    Generally something like "Ongoing" "Complete" or "On hiatus".
    
    It basically gets whatever is in the parentheses from text that is like: 
    "32 Volumes (On hiatus)".  Returns `False` if there are no parentheses.
    """
    m = re.search("\(.*\)", get_strings(soup_obj))
    if m:
        return(m.group(0)[1:-1])
    else:
        return(False)
# This is for any information you want to process later
@check_tag_is_category_decorator
def clean_default_category(soup_obj):
    """
    A 'default' category information cleaner. 
    Just returns a list of stripped strings from all of the category content
    """
    return([e.strip() for e in soup_obj.strings])





def metadata_task(url):
    # Load the series' page and soupify it
    soup = ninja_soupify(url, new_header=True)
    # Get the categories
    category_dict = get_all_categories(soup)
#     image_cat_name = [e for e in category_dict.keys() if "Image" in e]
#     bleh = category_dict.pop(image_cat_name[0])
    
    # Let's turn those categories into useable data
    genre = clean_genre_category(category_dict["Genre"])
    categories = clean_categories_category(category_dict["Categories"])
    forum_stuff= clean_forum_category(category_dict["Forum"])
    user_ratings = clean_user_rating_category(category_dict["User Rating"])
    was_anime = clean_anime_category(category_dict["Anime Start/End Chapter"])
    status = clean_status_category(category_dict["Status in Country of Origin"])
#     print("----------------")
#     print(status)
#     print(category_dict.keys())
    
    # ----------- 'Defaultly' cleaned categories:
    description = clean_default_category(category_dict["Description"])
    type = clean_default_category(category_dict["Type"])
    related_series = clean_default_category(category_dict["Related Series"])
    associated_names = clean_default_category(category_dict["Associated Names"])
    completely_scanlated = clean_default_category(category_dict["Completely Scanlated?"])
    last_updated = clean_default_category(category_dict["Last Updated"])
    category_recs = clean_default_category(category_dict["Category Recommendations"])
    recs = clean_default_category(category_dict["Recommendations"])
    authors = clean_default_category(category_dict["Author(s)"])
    artists = clean_default_category(category_dict["Artist(s)"])
    year = clean_default_category(category_dict["Year"])
    original_pub = clean_default_category(category_dict["Original Publisher"])
    serialized_in = clean_default_category(category_dict["Serialized In (magazine)"])
    licensed = clean_default_category(category_dict["Licensed (in English)"])
    english_pub = clean_default_category(category_dict["English Publisher"])
    
    
    
    # ----------- Not implemented:
    # activity_stats
    
    try:
        list_stats = clean_list_stats_category(category_dict["List Stats"])
    except AssertionError as errorm:
        raise KeyboardInterrupt(str(errorm))
    
#     print(genre)
#     print(categories)
#     print(list_stats)
#     print(forum_stuff)
    
    return(";".join(sorted(list(category_dict.keys()))))
    



# The worker thread pulls an item from the queue and processes it
def manga_worker():
    global update_info_list
    global metadata_list
    global Error_list
    global manga_q
    while True:
        manga_id, is_metadata, *page_number = manga_q.get()
        try:
            if is_metadata:
                metadata_results = metadata_task(SERIES_METADATA_URL_FORMAT.format(manga_id))
                with metadata_lock:
                    metadata_list+=[metadata_results]
            else:
                issue_results = issue_task(ISSUE_URL_FORMAT.format(manga_id, page_number[0]), manga_id, page_number[0])
                with update_info_lock:
                    update_info_list+=issue_results
        except Exception as error_m:
            print("MANGA ID FUCK UP = {!s}".format(manga_id))
            Error_list+=[[str(error_m), manga_id, is_metadata]]
#             raise
        finally:
            manga_q.task_done()
        
# def manga_worker():
#     global update_info_list
#     global metadata_list
#     global Error_list
#     while True:
#         manga_id, is_metadata, *page_number = manga_q.get()
#         if is_metadata:
#             metadata_results = metadata_task(SERIES_METADATA_URL_FORMAT, manga_id)
#             with metadata_lock:
#                 metadata_list+=[metadata_results]
#         else:
#             issue_results = issue_task(ISSUE_URL_FORMAT, manga_id, page_number[0])
#             with update_info_lock:
#                 update_info_list+=issue_results
#         manga_q.task_done()



def get_issue_info_from_table(soup_obj, manga_id, expected_number_of_columns=5):
    """ Returns all the information for each row for a soup object of an updates page, 
    with the last value of each row being the manga id number.
    
    If it doesn't have the right number of columns (default being 5), return `None`"""
    # Get the rows of the updates
    soup_rows = get_soup_row_list(soup_obj)
    # Turn the list of soup objects into a list of strings
    string_rows_list = [soup_row_to_string_list(e) for e in soup_rows]
    # Add in the manga id
    string_rows_list[:] = [e+[manga_id] for e in string_rows_list]
    # If the first row doesn't have the right amount of columns...
    # it's probably a page with no updates, so don't return anything
    if len(string_rows_list[0]) == expected_number_of_columns + 1:
        return(string_rows_list)
    else:
        return(None)
    


    
      
            


def issue_task(url, manga_id, page_number):
#     print("manga id: {0}, page: {1}".format(manga_id, page_number))
    # Load the page and soupify it
    soup = ninja_soupify(url)
    # If it's the first page and a valid series...
    if check_whether_series_valid(soup):
        if page_number == 1:
            # see how many other pages there are...
            max_page = get_page_count(soup)
            if max_page:
                # and put them on the queue too
                for i in range(2, max_page+1):
                    manga_q.put([manga_id, False, i])
                    
        global EXPECTED_COL_NUM
        return(get_issue_info_from_table(soup, manga_id, EXPECTED_COL_NUM))
    else: 
        return(None)
         
    
    




def main():
    global update_info_lock
    global update_info_list
    update_info_lock = threading.Lock()
    update_info_list = []
    
    global metadata_lock
    global metadata_list
    metadata_lock = threading.Lock()
    metadata_list = []
    
    global manga_q
    
    manga_q = Queue()
    for i in range(100): 
        t = threading.Thread(target=manga_worker)
        t.daemon = True
        t.start()
        
    start = time.perf_counter() 
    manga_ids=set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))    
    for m_id in list(manga_ids)[:1000]:
#         manga_q.put([m_id, False, 1])
        manga_q.put([m_id, True])
        print(m_id)
    
    manga_q.join()       # block until all tasks are done
#     with open("/Users/zburchill/Desktop/delete2.csv","w",newline='',encoding='utf-8') as f:
#         filewriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
#         for thing in update_info_list:
#             print(thing)
#             filewriter.writerow(thing)
# #         filewriter.writerows(update_info_list)
#         print(len(update_info_list))
    print(len(set(metadata_list)))
    print(len(Error_list))
    print(",".join([e[1] for e in Error_list]))
    print("DONE")





# l=collect_valid_series()
# save_obj(l, "valid_series_ids")
# valid_series_ids = load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids")

# 
# s=ninja_soupify("https://www.mangaupdates.com/series.html?id=138324")
# d=get_all_categories(s)
# print(clean_list_stats_category(d["List Stats"]))
# # print(list(d["List Stats"].strings))
# # for e in d["List Stats"].strings:
# #     if e[0]=="\n":
# #         print("IXIX")
# #     print(str(e)+"LLLLLLLL")
# # print([int(e.string) for e in d["List Stats"].find_all("b")])
# # stats = [e for e in d["List Stats"].find_all("b")]
# # print([e.next_sibling.split()[0] for e in stats])


def define_global_variables():
    # Global Constants
    global NUMBER_OF_NONALPHA_MANGA_PAGES # the number of pages of manga that don't begin with letters we have to scroll through 
    NUMBER_OF_NONALPHA_MANGA_PAGES = 4 
    global EXPECTED_COL_NUM
    EXPECTED_COL_NUM = 5
    global SERIES_METADATA_URL_FORMAT
    SERIES_METADATA_URL_FORMAT="https://www.mangaupdates.com/series.html?id={0}"
    global ISSUE_URL_FORMAT
    ISSUE_URL_FORMAT="https://www.mangaupdates.com/releases.html?page={1}&search={0}&stype=series&perpage=100"
    global SWITCH_PROXIES_AFTER_N_REQUESTS # make really really big if you don't want to switch
    SWITCH_PROXIES_AFTER_N_REQUESTS = 10
    
    global Error_list # something to store all the errors
    Error_list = []


if __name__ == "__main__":
    define_global_variables()
    ninja_soupify = ninja_soupify_simpler(SWITCH_PROXIES_AFTER_N_REQUESTS)
    
#     metadata_task(SERIES_METADATA_URL_FORMAT,16)
    print("CCCCCCCCCCCCCC")
    print(ninja_soupify("https://google.com"))
    
    # clean_status_category = clean_category_default
#     print("ABABABABA")
#     s = ninja_soupify("https://www.mangaupdates.com/series.html?id=3920")
#     print("ABABABABA")
#     d = get_all_categories(s)
#     
#     # print(get_strings(d["User Rating"]))
#     print(d["User Rating"].next_element.split())
#     print(d["User Rating"].next_element.next_element.next_element.next_element.string)
#     print("XXXX")
#     print(clean_status_category(d["Status in Country of Origin"]))
#     print(d.keys())
#     main()
