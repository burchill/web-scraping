'''
THE NEW VERSION!

@author: zburchill

proxy stuff inspired by: https://codelike.pro/create-a-crawler-with-rotating-ip-proxy-in-python/
'''

import re, os

# for threading
import threading
from queue import Queue
from basic_functions import PageScrapeException, ninja_soupify_simpler, remove_duplicate_elements,\
    clean_find, get_string, save_progress, ninja_soupify_and_pass
from bs4 import Tag
from warnings import warn
from bs4.element import NavigableString
from string import ascii_uppercase
from itertools import combinations_with_replacement

import pickle
from functools import wraps, partial # for the decorators



'''
TO-DO:
     
     * make it so that when it's not starting a fresh, it gets only the ones that haven't been done
     * make `get_manga_ids_from_table` analogous to `get_issue_info_from_table` in the sense that it takes a soup object
     
     * filter out one-shots
             Status in Country of Origin:
                Oneshot (Complete)  ie 112368
     * Coin Rand ['Add']  is currently ['Coin Rand\xa0[', 'Add', ']'] ie 112368
     * Multiple completion datees:
            Oneshot (Complete)
            2 Volumes (Complete) ie 46225
     * get rid of what's in parentheses for "serialized_in"
         eg ['Betsucomi','(Shogakukan)', ''] 13581
             also strip ending (they can have multiple serializations though
     * get rid of extra blanks in "English pubs"
         eg ["Harlequin K.K.","","SoftBank Creative",""] 32093
     
'''

# 
#     
# def random_proxy():
#     global Proxies_list
#     return random.randint(0, len(Proxies_list) - 1)
# 
# # Only does https currently
# def ninja_soupify(url, tolerance=10, **kwargs):
#     # If it's time to switch to a new proxy, do so
#     global Proxies_list
#     global SWITCH_PROXIES_AFTER_N_REQUESTS
#     global Proxy_index
#     global Request_counter
#     if Request_counter % SWITCH_PROXIES_AFTER_N_REQUESTS == 0:
#         Proxy_index = random_proxy()
#     dead_proxy_count = 0
#     while dead_proxy_count <= tolerance:
#         # If for some reason there isn't a proxies list, make one
#         if not Proxies_list: Proxies_list = get_proxies()
#         proxy = { "https": "http://{ip}:{port}".format(**Proxies_list[Proxy_index]) }
#         try:
#             r = soupify(url, proxies = proxy, **kwargs)
#             Request_counter += 1
#             return(r)
#         except (requests.exceptions.SSLError, requests.exceptions.ProxyError) as err:
#             warn("Proxy {d[ip]}:{d[port]} deleted because of: {error_m!s}".format(d=Proxies_list[Proxy_index], error_m=err))
#             del Proxies_list[Proxy_index]
#             Proxy_index = random_proxy()
#             dead_proxy_count += 1
#     raise PageScrapeException(url=url, message="Burned through too many proxies ({!s})".format(tolerance))
         
            
        
        
        

    


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

# Outputs a normal string
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

def get_id_from_url(url, prefix="series.html\?"):
    """ Regexes an id from a mangaupdates url.
    For series, prefix should be "series.html\?", authors should be "authors.html\?", etc.
    """
    re_string = "(?<={prefix}id=)([^&])*".format(prefix=prefix)
    result = re.search(re_string, url)
    if result: return result.group(0) 
    else: return None

def get_ids_from_links(soup_obj, prefix="series.html?", remove_duplicates=True):
    """
    Searches through all the links, and if they have series' ids, returns them.
    For series, prefix should be "series.html?", authors should be "authors.html?", etc.
    """
    links = [e.get('href') for e in soup_obj.find_all("a")]
    id_urls = [e for e in links if ("javascript" not in e) and ("id=" in e)]
    ids = [get_id_from_url(e) for e in id_urls]
    if remove_duplicates:
        ids=remove_duplicate_elements(ids)
    return(ids)



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
        name = str("-".join(category.strings))
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
    genres = [get_string(e) for e in soup_obj.find_all("a")]
    if not genres:
        assert get_string(soup_obj).strip() == "N/A"
    genres = genres[:-1] # Drop the "see more thing")
    return(genres)
@check_tag_is_category_decorator
def clean_categories_category(soup_obj):
    """Returns a list of pairs: x = category string, y = final score"""
    categories = soup_obj.find_all("li")
    categories[:] = [(get_string(e), int(e.a["title"].split()[1])) for e in categories]
    if not categories:
        assert get_string(soup_obj).strip()=="N/A"
    return(categories)
@check_tag_is_category_decorator
def clean_list_stats_category(soup_obj):
    """Returns dicts of string->int"""
    d={}
    type_of_lists = [e.next_sibling.split()[0]  for e in soup_obj.find_all("b")]
    stats = [int(get_string(e)) for e in soup_obj.find_all("b")]
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
@check_tag_is_category_decorator
def clean_rec_category(soup_obj):
    """
    Similar to the default category cleaner, but removes repeated data before the "More..." if that exists
    """
    # Gets the series' ids
    no_dupe_ids = get_ids_from_links(soup_obj, remove_duplicates=True)
    
    # How I take care of the "More..., [...] L,ess..." stuff
    unlikely_string = "XXZACHBURCHILLXX"
    default_l = [str(e).strip() for e in soup_obj.strings]
    excised = re.search("(?:(?:{0})+M(?:{0})*ore\.\.\.(?:{0})*)(.*)(?:({0})*L(?:{0})*ess\.\.\.(?:{0})*)".format(unlikely_string), 
                      unlikely_string.join(default_l))
    if excised:
        default_l = excised.groups()[0].split(unlikely_string)
    else: 
        warn("Manga without the same rec format!")
    names = [e for e in default_l if e != ""]
    no_dupe_names = list(set(names))
    
    return({"ids": no_dupe_ids, "names": no_dupe_names})

@check_tag_is_category_decorator
def clean_activity_stats_category(soup_obj):
    
    pass

    
#     for i in range(0,len(default_l)-3):
#         print("===============")
#         print(default_l[i])
#         print("--------------")
#         if default_l[i] == "M" and default_l[i+1] == "ore...":
#             print("ZZZZZZZZ")
#             j = i+2
#             print(default_l[j])
#             while default_l[j] == "": 
#                 print("looop")
#                 j+=1
#                 print(default_l[j])
#                 
#             good_l = default_l[j:]
#             assert len(good_l) > 1
#             k = j+1
#             while k < len(default_l)-1 and 
#             return(good_l) 

@check_tag_is_category_decorator
def clean_related_series_category(soup_obj):
    """
    Returns either "N/A" or a dictionary of the following format:
        key = how the related series is related
        value = a dictionary where:
            "count": how many series fall under this relation
            "list": a list of tuples of (name, series id)
    """
    print(soup_obj)
    links = soup_obj.find_all("a")
    if not links:
        if get_strings(soup_obj).strip() == "N/A":
            return("N/A")
        else:
            l = clean_default_category(soup_obj, remove_empty=True)
            c = len(l)
            return({"(Misc.)": {"count": c, "list": [(e, None) for e in l]}})
    d = {}
    for link in links:
        series_id = get_id_from_url(link.get("href"))
        assert series_id != None
        if link.next_sibling.name == "br":
            classification = "(Misc.)"
        else:
            classification = get_string(link.next_sibling).strip()
        name = get_string(link).strip()
        if classification in d.keys():
            mini_d = d[classification]
            mini_d["count"] += 1
            mini_d["list"] += [(name, series_id)]
            d[classification] = mini_d
        else:
            mini_d = {}
            mini_d["count"] = 1
            mini_d["list"] = [(name, series_id)]
            d[classification] = mini_d
    return d
# This is for any information you want to process later
@check_tag_is_category_decorator
def clean_default_category(soup_obj, remove_empty=False):
    """
    A 'default' category information cleaner. 
    Just returns a list of stripped strings from all of the category content
    """
    strings = [str(e).strip() for e in soup_obj.strings]
    if remove_empty: return [str(e).strip() for e in strings if e != ""]
    else: return strings 
# Unused:
@check_tag_is_category_decorator
def get_series_id(soup_obj):
    """ Requires the "category" category as the soup_obj """
    def is_java_link(tag):
        try:  return("javascript:showCat" in tag["href"])
        except KeyError: return(False)
    javascript_link = clean_find(soup_obj, is_java_link)
    if javascript_link:
        series_id = javascript_link.get("href").split("javascript:showCat(")[-1].split(",")[0]
        return(series_id)
    else:
        warn("Manga does not have an id")
        return(None)
    





def metadata_task(soup):
    # Get the categories
    category_dict = get_all_categories(soup)    
    # the metadata dictionary
    m_d = {}
    # Let's turn those categories into useable data
    m_d["genre"] = clean_genre_category(category_dict["Genre"])
    m_d["categories"] = clean_categories_category(category_dict["Categories"])
    m_d["forum_stuff"] = clean_forum_category(category_dict["Forum"])
    m_d["user_ratings"] = clean_user_rating_category(category_dict["User Rating"])
    m_d["was_anime"] = clean_anime_category(category_dict["Anime Start/End Chapter"])
    m_d["status"] = clean_status_category(category_dict["Status in Country of Origin"])
    recs = clean_rec_category(category_dict["Recommendations"])
    m_d["rec_ids"] = recs["ids"]
    m_d["rec_names"] = recs["names"]
    m_d["related_series"] = clean_related_series_category(category_dict["Related Series"])
    
    # ----------- 'Defaultly' cleaned categories:
    m_d["description"] = clean_default_category(category_dict["Description"])
    m_d["type"] = clean_default_category(category_dict["Type"])
    m_d["associated_names"] = clean_default_category(category_dict["Associated Names"])
    m_d["completely_scanlated"] = clean_default_category(category_dict["Completely Scanlated?"])
    m_d["last_updated"] = clean_default_category(category_dict["Last Updated"])
    m_d["category_recs"] = clean_default_category(category_dict["Category Recommendations"])
    m_d["authors"] = clean_default_category(category_dict["Author(s)"], remove_empty=True)
    m_d["artists"] = clean_default_category(category_dict["Artist(s)"], remove_empty=True)
    m_d["year"] = clean_default_category(category_dict["Year"], remove_empty=True)
    m_d["original_pub"] = clean_default_category(category_dict["Original Publisher"], remove_empty=True)
    m_d["serialized_in"] = clean_default_category(category_dict["Serialized In (magazine)"])
    m_d["licensed"] = clean_default_category(category_dict["Licensed (in English)"])
    m_d["english_pub"] = clean_default_category(category_dict["English Publisher"])    
    # ----------- Not implemented:
    # activity_stats
    # getting author information, such as gender/blood type
    # image (don't see why this is useful)
    try:
        m_d["list_stats"] = clean_list_stats_category(category_dict["List Stats"])
    except AssertionError as errorm:
        raise KeyboardInterrupt(str(errorm))

    return(m_d)
    



# The worker thread pulls an item from the queue and processes it
def manga_worker():
    global Update_info_list
    global Metadata_list
    global Error_list
    global manga_q
    
    while True:
        manga_id, is_metadata, *page_number = manga_q.get()
        try:
            if is_metadata:
                # Uses the soupify_and_pass function to load a url and pass it into the metadata_task function
                metadata_results = nsap(SERIES_METADATA_URL_FORMAT.format(manga_id), metadata_task)
                metadata_saver((manga_id, metadata_results))
                print("GOOOD: ")
                print(metadata_results)
                Metadata_list += [manga_id]
            else:
                # Uses the soupify_and_pass function to load a url and pass it into the issue_task function
                issue_results = nsap(ISSUE_URL_FORMAT.format(manga_id, page_number[0]), issue_task, manga_id, page_number[0])
                with update_info_lock:
                    Update_info_list+=issue_results
        except Exception as error_m:
            print("MANGA ID FUCK UP = {!s}".format(manga_id))
            Error_list+=[[str(error_m), manga_id, is_metadata]]
            raise
        finally:
            manga_q.task_done()
        



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
        return((manga_id, get_issue_info_from_table(soup, manga_id, EXPECTED_COL_NUM)))
    else: 
        return(None)
         
    
    




def main():
    global START_OVER
    global METADATA_BOOL
    
    global Update_info_list
    Update_info_list = []
    
    global Metadata_list
    Metadata_list = []
    
    global Error_list
    Error_list = []
    
    global manga_q
    manga_q = Queue()
    for i in range(NUM_THREADS): 
        t = threading.Thread(target=manga_worker)
        t.daemon = True
        t.start()
        
#     start = time.perf_counter() 
    if START_OVER:
        manga_ids = list(set(load_obj("/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"))) 
    else:
        manga_ids = list(set(load_obj(MAIN_PATH + "remaining")))
        try: Error_list = load_obj(MAIN_PATH + "errors")
        except FileNotFoundError: print("Error file does not exist")
    original_manga_ids = manga_ids
    
    try:
        while len(manga_ids) > 0:
            if manga_q.qsize() < NUM_THREADS:
                for i in range(NUM_THREADS):
                    try: 
                        m_id = manga_ids.pop()
                    except IndexError:
                        break
                    else:
                        if METADATA_BOOL: manga_q.put([m_id, True]) # gets metadata
                        else: manga_q.put([m_id, False, 1]) # gets issues
    finally:
        print("Closing!")
        if METADATA_BOOL: close_up(Metadata_list, original_manga_ids, Error_list)
        else: close_up(Update_info_list, original_manga_ids)
        metadata_saver.close()
        issue_task_saver.close()
        
        print(len(set(Metadata_list)))
        print(len(Error_list))
        print(",".join([e[1] for e in Error_list]))
        for e in Error_list:
            print("--------------------")
            print(e)
        print("DONE")
                
    manga_q.join()       # block until all tasks are done
    
    print("Hey, looks like you're done!")
    print(len(set(Metadata_list)))
    print(len(Error_list))
    print(",".join([e[1] for e in Error_list]))
    for e in Error_list:
        print("--------------------")
        print(e)
    print("DONE")
    try:
        metadata_saver.close()
        issue_task_saver.close()
    finally:
        if METADATA_BOOL: close_up(Metadata_list, original_manga_ids, Error_list)
        else: close_up(Update_info_list, original_manga_ids, Error_list)


def close_up(finished_ids, original_ids, errors):
    global MAIN_PATH
    original_ids = set(original_ids)
    weirdo_list = []
    if len(set(finished_ids)) != len(finished_ids):
        print("There are ids that have been processed more than once!")
    finished_ids = set(finished_ids)
    for e in finished_ids:
        if e in original_ids:
            original_ids.remove(e)
        else: 
            weirdo_list += [e]
    if weirdo_list:
        print("Oddly, these manga were supposed to have been logged, but weren't in the set of ids used:")
        print(weirdo_list)
    save_obj(original_ids, MAIN_PATH + "remaining")
    save_obj(errors, MAIN_PATH + "errors")
           


def define_global_variables():
    # Global Constants
    global MAIN_PATH
    MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
    global NUM_THREADS 
    NUM_THREADS = 100
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
    # Redundant?
    global Error_list # something to store all the errors
    Error_list = []

if __name__ == "__main__":
    global START_OVER
    global METADATA_BOOL
    
    START_OVER = True
    METADATA_BOOL = True # if False, it runs the issue_task

    define_global_variables()
    global MAIN_PATH
    
    metadata_saver = save_progress(MAIN_PATH + "first", save_progress.identity, save_after_n=200)
    issue_task_saver = save_progress(MAIN_PATH + "issues", save_progress.identity, save_after_n=200)
    ninja_soupify = ninja_soupify_simpler(SWITCH_PROXIES_AFTER_N_REQUESTS)
    nsap = partial(ninja_soupify_and_pass, ninja_soupify)
    
    print("CCCCCCCCCCCCCC")

    main()
