'''
Created on Apr 2, 2018

@author: zburchill
'''
# 
from basic_functions import PersistentDict
from warnings import warn
 
def load_dict(db_path):
    db =  PersistentDict(db_path, flag='r', format="json")
    d = db.to_dict()
    return(d)

def add_page(d, manga_id, page, k):
    if manga_id in d:
        if page in d[manga_id]:
            print("{0} {1} already in dictionary!")
            x=0/0
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
            

missing_pages, good_d = clean_issues_dictionary("everything_json_issues.json") 
print(len(missing_pages))

print("AAA")
print(good_d["33"][1])
print(good_d["33"][1])
    
with PersistentDict("everything_json_issues_slimmed.json", 'c', format='json') as db:
    for k, v in good_d.items():
        db[k] = v

    

    
#     
# 
# 
#    for page_number in range(1, v+1):
#                 val = "{series_id}{infix}{n!s}".format(series_id = k,
#                                                        infix = page_infix,
#                                                        n =  page_number)
#                 if val in db:
#                     at_least_one = True
#                     a = db[val]
#                     if k in big_dict:
#                         if page_number in big_dict[k]:
#                             raise ValueError("Series number {!s}, page {!s} erroneously appears at least twice!".format(k, page_number))
#                         else:
#                             big_dict[k][page_number] = a
#                     else:
#                         big_dict[k] = {page_number: a}                       
#                 else:
#                     if k in dict_of_missing_chapters:
#                         dict_of_missing_chapters[k] = dict_of_missing_chapters[k] + [page_number]
#                     else:
#                         dict_of_missing_chapters[k] = [page_number]
#             if not at_least_one:
#                 raise ValueError("Series number {!s} doesn't actually have any chapters!".format(k))
#         
#     
# 
# 
# 
# 
# print(len(max_pages))
# print(len(max_pages2))
# print(len(d.keys()))
# print(max_pages[1:10])
# 
# 
# 
# 
# # 
# # 
# with shelve.open(db_path) as db:
#     # Get all the series that have any issues recorded
#     for k in ids:
#         first_page_starter = str(k) + page_num_suffix
#         if first_page_starter in db:
#             max_pages = db[first_page_starter]
#             if k in dict_of_all_saved_manga_ids:
#                 raise ValueError("Series number {!s} erroneously appears at least twice!".format(k))
#             dict_of_all_saved_manga_ids[k] = max_pages







# 
# list_of_dicts = []
# 
# with shelve.open("everything") as db:
#     for key in all_possible_keys:
#         if k in db:
#             a = db[k]
#             a["id"] = k
#             list_of_dicts += [a]




# 
# 
# if __name__ == "__main__": 
#     
#     MAIN_PATH = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
#     db =  PersistentDict("everything_json.json", flag='r', format="json")
#     print(type(db))
#     print(type(db.to_dict()))
#     print(type({"a":1}))
    
#     with PersistentDict(MAIN_PATH+"everything_json.json", flag='r', format="json") as d:
#         print(len(d.keys()))
#         print(d["33"])
#     print(d["33"])
#     from basic_functions import soupify, get_string
#     
#     soup = soupify("https://www.mangaupdates.com/series.html?id=33")
#     print(soup.span["class"])
#     print(get_string(soup.find('span',{'class': ['releasestitle', 'tabletitle']})))
#     
#     
# #     
#     
#     print(dbm.whichdb(MAIN_PATH+"everything.db"))
#     print(dbm.whichdb(MAIN_PATH+"everything"))
#     with dbm.gnu.open(MAIN_PATH+"everything") as db:
#         print(db.keys)
#     ds = load_metadata_dicts(MAIN_PATH+"everything", "all_series_ids")
# #     print(len(ds))
#     ds = load_metadata_dicts("/Users/zburchill/Desktop/everything", "all_series_ids")
#     print(len(ds))
#     print(ds[0].keys())
#     with shelve.open("small_fry") as db:
#         db["12463"] = ds[0]
    

    
#     

#     ids = "all_series_ids"
#     
#     
#     errors = get_data_from_error("errors")
# #     errs = load_obj("errors")
# #     errs[:] = [e[1] for e in errs]
#     print(len(errors))
#     print(len(errors[0]))
#     print(len(errors[len(errors)-1]))
#     print([e for e in errors if "This id is bad and should be removed" == e[0] ])
# #     results, missing_chapters = load_issue_dicts(MAIN_PATH + "first_1891_issues", ids)
# #     for k, v in missing_chapters.items():
# #         print("{0}: {1}, {2}".format(k, len(v), v))
# #     print(len(missing_chapters.keys()))
# #     print(len(results.keys()))
# #     print(results["3552"])
# #     print(len(results["133571"]))
#     print(get_data_from_error("errors"))
# #     only_over_one = [e for e in results.keys() if ]


