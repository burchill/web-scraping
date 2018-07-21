


# for threading
import threading
from queue import Queue
from basic_functions import ninja_soupify_simpler, ninja_soupify_and_pass, save_obj
from manga_updates import get_page_count, get_manga_ids_from_table


from string import ascii_uppercase
from itertools import combinations_with_replacement

from functools import partial # for the decorators

from time import sleep # ehhh


# The worker thread pulls an item from the queue and processes it
def manga_id_worker():
    global manga_q
    global manga_id_list
    
    while True:
        # Gets the manga id, and whether the worker should process the releases or the metadata 
        url = manga_q.get()
        try:
            manga_id_list.extend(nsap(url, get_manga_ids_from_table))
        except Exception:
            print("MANGA ID FUCK UP = {!s}".format(url))
        finally:
            manga_q.task_done()
        

def main():
       
    # Make a global queue
    global manga_q
    global manga_id_list
    manga_q = Queue()
    for i in range(NUM_THREADS): 
        t = threading.Thread(target = manga_id_worker)
        t.daemon = True
        t.start()
    
    # This is the format of the urls that let us browse all the manga by first letter
    url_format          = "https://www.mangaupdates.com/series.html?page={0}&letter={1}&perpage=100&filter=some_releases&type=manga"
    # In order to get those that don't begin with a letter, we use this format
    nonalpha_url_format = "https://www.mangaupdates.com/series.html?page={0}&perpage=100&filter=some_releases&type=manga"

    # go through all the pages of manga that don't start with alphabetic characters
    #    currently there are 4 
    for counter in range(1, NUMBER_OF_NONALPHA_MANGA_PAGES):
        manga_q.put(nonalpha_url_format.format(counter))
    
    # I no longer know if the following is true, but hey, whatever:
    # # Due to limitations of how many pages can be displayed for any given letter, it's easier to go by
    # #    two letter combinations, e.g. manga that start with "AB", etc.
    # # Just trust me, alright?  This makes it easier/possible, believe it or not
    letterpairs = list(combinations_with_replacement(ascii_uppercase,2))
    letterpairs[:] = [e[0]+e[1] for e in letterpairs]
    display_counter = 0 # for printout purposes
    for letter in letterpairs:
        # For displaying updates
        display_counter += 1
        if display_counter % 30 == 0:
            print("Starting pair: "+letter)
        
        manga_q.put(url_format.format(1, letter))
        # Gets the number of pages that start with that letter combo...
        page_count = nsap(url_format.format(1, letter), get_page_count) 
        if page_count:
            # ...and puts them on the queue too
            for i in range(2, page_count+1):
                manga_q.put(url_format.format(i, letter))
                
    print("All threads now on queue")
    
    full_q_size = manga_q.qsize()
    while manga_q.qsize() > 0:
        size_of_queue = manga_q.qsize()
        size = round(size_of_queue/full_q_size * 50)
        bar = "".join(["[", "".join(["|" for e in range(0, size)]), "]"])
        print(bar + "  {}/{}".format(size_of_queue, full_q_size))
        sleep(10)
    
    manga_q.join()
    print("Done!")
    print(manga_id_list)
    save_obj(list(set(manga_id_list)), "new_threaded_series_ids")
    print("Saved!")
    
def define_global_variables():
    # Global Constants
    global MAIN_PATH
    MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
    global NUM_THREADS 
    NUM_THREADS = 100
    global NUMBER_OF_NONALPHA_MANGA_PAGES # the number of pages of manga that don't begin with letters we have to scroll through 
    NUMBER_OF_NONALPHA_MANGA_PAGES = 4 
    global EXPECTED_COL_NUM # number of columns in the issues tables
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
    global BAD_IDS
    BAD_IDS = ["132433", "134159"] # I don't know what the fuck this does, but they're not real series. check for example: https://www.mangaupdates.com/releases.html?search=134159&stype=series&perpage=100
    global MAXPAGES
    MAXPAGES = 100 # There should never be more than 10,000 updates for any one series



if __name__ == "__main__": 
    define_global_variables()
    global MAIN_PATH
    
    global manga_id_list
    manga_id_list = []
    
    ninja_soupify = ninja_soupify_simpler(SWITCH_PROXIES_AFTER_N_REQUESTS)
    nsap = partial(ninja_soupify_and_pass, ninja_soupify)
        
    print("CCCCCCCCCCCCCC")
    
    main()

