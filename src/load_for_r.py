'''
Created on Apr 2, 2018

@author: zburchill
'''
import shelve, pickle

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

