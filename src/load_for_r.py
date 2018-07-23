'''
Created on Apr 2, 2018

@author: zburchill
'''
# 
# from basic_functions import PersistentDict
# 
# def load_dict(db_path, id_path):
#     db =  PersistentDict(db_path, flag='r', format="json")
#     d = db.to_dict()
#     return(d)





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


