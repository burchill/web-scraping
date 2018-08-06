'''
Created on Apr 2, 2018

@author: zburchill
'''
from basic_functions import PersistentDict
from warnings import warn

# This is for paring down the issues data base, and seeing if there are missing pages
 
def load_dict(db_path):
    db =  PersistentDict(db_path, flag='r', format="json")
    d = db.to_dict()
    return(d)

def add_page(d, manga_id, page, k):
    if manga_id in d:
        if page in d[manga_id]:
            print("{0} {1} already in dictionary!")
            x=0/0 # cheap way to stop it
        d[manga_id][page] = k
    else:
        d[manga_id] = {page: k}
        
    
def clean_issues_dictionary(json_file, page_infix="_page_"):
    d = load_dict(json_file)
    max_pages =     [e for e in d.keys() if "pagenum" in e]
    non_max_pages = [e for e in d.keys() if not "pagenum" in e]
    set_ids = list(set([e.split("_")[0] for e in non_max_pages]))
    
    if len(set_ids) != len(max_pages):
        warn("The number of unique series does not match the number of page entries")

    used_series_ids = []
    used_keys = []
    max_page_dict = {}
    missing_pages = []
    good_dictionary = {}
    
    # Add the max pages to a dictionary
    for i in max_pages:
        manga_id = i.split("_")[0]
        mp = d[i]
        max_page_dict[manga_id] = mp
    # Go through the dictionary:
    for k, v in max_page_dict.items():
        for page_number in range(1, v+1):
            val = "{series_id}{infix}{n!s}".format(series_id = k,
                                                   infix = page_infix,
                                                   n =  page_number)
            # This shouldn't happen
            if val in used_keys:
                print("oh shit!")
                print(d[val])
                x=0/0
            
            if val in non_max_pages:
                used_keys += [val]
                non_max_pages.remove(val)
                add_page(good_dictionary, k, page_number, d[val])
                
            else:
                missing_pages += [(k, page_number)]
        used_series_ids += [k]
    
    print(len(non_max_pages))
    print(non_max_pages)
    print(missing_pages)
    print(used_series_ids)
    
    return( (missing_pages, good_dictionary) )
            

missing_pages, good_d = clean_issues_dictionary("../data/manga_project/everything_json_issues.json") 

print(len(missing_pages))


with PersistentDict("../data/manga_project/everything_json_issues_slimmed.json", 'c', format='json') as db:
    for k, v in good_d.items():
        db[k] = v

    