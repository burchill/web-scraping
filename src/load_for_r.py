'''
Created on Apr 2, 2018

@author: zburchill
'''
import shelve, pickle


# This is a function that will be used by R to load the shelf dictionary
# There's a weird thing where my version of OSX can't really handle large shelf objects
# Basically, I can't do something like `for k, v in shelve.open(path)`.
# So I have to already know all the possibly keys and try all the possible values,
#    which kinda sucks. But whatever

def load_dicts(db_path, id_path):
    def load_obj(name):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    
    list_of_dicts = []
    ids = set(load_obj(id_path))
    
    with shelve.open(db_path) as db:
        for k in ids:
            if k in db:
                a = db[k]
                a["id"] = k
                list_of_dicts += [a]

    print(len(list_of_dicts))
    return(list_of_dicts)

# Since I'm saving the issue information a bit differently, I'm just making this a separate function
def load_issue_dicts(db_path, id_path, 
                     page_num_suffix = "_pagenum",
                     page_infix = "_page_"):
    """Returns a tuple, with the results as a dictionary for the first element
    and a dictionary of missing chapters as the second element """
    
    def load_obj(name):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    
    big_dict = {} # a dict of dicts which will have the results
    dict_of_all_saved_manga_ids = {} # dict
    dict_of_missing_chapters = {} # dictionary of lists
    ids = set(load_obj(id_path))

    with shelve.open(db_path) as db:
        # Get all the series that have any issues recorded
        for k in ids:
            first_page_starter = str(k) + page_num_suffix
            if first_page_starter in db:
                max_pages = db[first_page_starter]
                if k in dict_of_all_saved_manga_ids:
                    raise ValueError("Series number {!s} erroneously appears at least twice!".format(k))
                dict_of_all_saved_manga_ids[k] = max_pages
                
        # Get all the pages you can
        for k, v in dict_of_all_saved_manga_ids.items():
            at_least_one = False
            for page_number in range(1, v+1):
                val = "{series_id}{infix}{n!s}".format(series_id = k,
                                                       infix = page_infix,
                                                       n =  page_number)
                if val in db:
                    at_least_one = True
                    a = db[val]
                    if k in big_dict:
                        if page_number in big_dict[k]:
                            raise ValueError("Series number {!s}, page {!s} erroneously appears at least twice!".format(k, page_number))
                        else:
                            big_dict[k][page_number] = a
                    else:
                        big_dict[k] = {page_number: a}                       
                else:
                    if k in dict_of_missing_chapters:
                        dict_of_missing_chapters[k] = dict_of_missing_chapters[k] + [page_number]
                    else:
                        dict_of_missing_chapters[k] = [page_number]
            if not at_least_one:
                raise ValueError("Series number {!s} doesn't actually have any chapters!".format(k))
    return((big_dict, dict_of_missing_chapters))

# This just returns the ids, and is used to see what ids were saved.
#    Again, on a better computer, you could just do shelf.keys() or something
def get_ids_from_db(db_path, id_path):
    def load_obj(name):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    
    list_of_ids = []
    ids = set(load_obj(id_path))
    
    with shelve.open(db_path) as db:
        for k in ids:
            if k in db:
                list_of_ids += [k]
    return(list_of_ids)


if __name__ == "__main__": 
    
    MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
    ids = "/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"
    
    results, missing_chapters = load_issue_dicts(MAIN_PATH + "first_1891_issues", ids)
    for k, v in missing_chapters.items():
        print("{0}: {1}, {2}".format(k, len(v), v))
    print(len(missing_chapters.keys()))
    print(len(results.keys()))
    print(results["3552"])


