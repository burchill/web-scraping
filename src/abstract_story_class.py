'''
Created on Nov 23, 2019

@author: zburchill
'''
from basic_functions import *
from os.path import join as pathjoin
from abc import ABC, abstractmethod






    
    


    


class AbstractStory(ABC):
    ''' This is an 'abstract' story class. It really is just a class that needs a few methods to be overwritten to be 
        useful. It's not really an abstract class, but is designed to be extendable '''
    md_d = {}
    pd_d = {}
    vi_d = {} # What's this for again? viewer input?
    page_nums = unfinished_jobs = []
    story_id = unique_id = base_url = url = ""
    dir_story = dir_image = dir_json = ""
    q = None
    checklist = {"started": False, "good_pd":False, "good_md":False, "all_images":False}
    # Constants for this class. Note how it doesn't have `unfinished_jobs`
    necessary_fields = ["md_d", "pd_d", "vi_d", "page_nums", "story_id", "unique_id", "base_url", 
                        "url", "site", "dir_story", "dir_image", "dir_json", "pd_json", "md_json", 
                        "story_json", "checklist"]
    pd_json = "personal_metadata.json"
    md_json = "auto_metadata.json"
    story_json = "story_obj.json"
    # Temporary constants
    json_rel_path  = "json/"
    image_rel_path = "images/"
    
    # These are here to essentially remind people to set these three attributes
    @abstractmethod
    def site__base_url__main_path(self):
        """
        Currently, the `site`, `base_url` and `main_path` attributes need to be set for subclasses.
        This function exists just to remind you that you have to set them and is never called 
        """
        pass
    
    def __init__(self, load_dir=None, q2use=None, make_empty=False, json_path=None, json_file=None,
                 overwrite_pd=False, overwrite_md=False, **kwargs):
        ''' `make_empty` is for internal use only initializes an empty Story for `make_from_match()` '''
        self.dir_story = load_dir

        if not make_empty:
            assert os.path.exists(load_dir)
            json_path = self.json_rel_path if json_path is None else json_path
            json_file = self.story_json if json_file is None else json_file
            json_dir = pathjoin(load_dir, json_path)
            
            if self.has_good_saved_story(pathjoin(json_dir, json_file)):
                self.read_from_json(pathjoin(json_dir, json_file))
                if q2use is None:
                    logging.warn("Story "+self.dir_story+" does not have a Queue")
                self.q = q2use
            else:
                self.set_paths(**kwargs)
                self.set_url(**kwargs)
                
            self.sync(overwrite_pd = overwrite_pd, overwrite_md = overwrite_md)
           
    @classmethod   
    def cold_load(cls, load_dir, story_file=None, json_path=None, pd_file=None,
                  overwrite_pd = False, overwrite_md = False):
        ''' meant to be a simpler way to load from a file '''
        json_path  = cls.json_rel_path if json_path  is None else json_path
        story_file = cls.story_json    if story_file is None else story_file
        pd_file    = cls.pd_json       if pd_file    is None else pd_file
        
        story_file = pathjoin(load_dir, json_path, story_file)
        pd_file    = pathjoin(load_dir, json_path, pd_file)
        
        if cls.is_good_saved_story(story_file) and False:
            new_story = cls(make_empty=True)
            new_story.read_from_json(story_file)
        elif cls.is_good_pd(pd_file):
            pd = load_dict(pd_file)
            try:
                new_story = cls.make_from_match(pd["og_match"], q2use=None)
            except KeyError:  # moving forward, this won't be a problem
                new_story = cls(make_empty=True)
                new_story.pd_d = pd
                new_story.unique_id = get_dirname(load_dir)
                new_story.story_id = cls.get_nonunique_id(new_story.unique_id)
                new_story.set_paths(main_path = n_parent_dir(load_dir)+"/")
                new_story.set_url()
        elif os.path.exists(load_dir):
            new_story = cls(make_empty=True)
            new_story.unique_id = get_dirname(load_dir)
            new_story.story_id = cls.get_nonunique_id(new_story.unique_id)
            new_story.set_paths(main_path = n_parent_dir(load_dir)+"/")
            new_story.set_url()
        else:
            raise Exception(load_dir+" doesn't exist...")
        
        assert new_story.unique_id == get_dirname(load_dir)
        new_story.sync(overwrite_pd=overwrite_pd, overwrite_md=overwrite_md)
        return new_story
        
            
    # Match_dict is the match object.groupdict()
    @classmethod
    def make_from_match(cls, match_dict, q2use, overwrite_pd=True, overwrite_md=False, **kwargs):
        """
        Called as Story.make_from_match(), and will take an `re.match` object with capturing groups 'ID', 'rating', and 'tags'
            and build a Story from this data.
        If you want different paths / base_urls, **kwargs needs to contain the kwargs for `set_paths()` and `set_url()`,
            otherwise the default will be used.        
        """
        new_story = cls(make_empty=True)
        new_story.pd_d = new_story.get_pd_from_match(match_dict)
        new_story.set_offline_info(match_dict)
        new_story.set_paths(**kwargs)
        new_story.set_url(**kwargs)
        new_story.q = q2use
        
        new_story.sync(overwrite_pd=overwrite_pd, overwrite_md=overwrite_md)
        return new_story
            
    # ------------------------------------ Repairing and syncing functions ------------------------------------

    def sync(self, overwrite_pd = False, overwrite_md=False):
        """
        Aligns the information on disk with the information in memory.
        The overwrite arguments are whether to use the currently loaded metadata information (if they're
            well-formed; i.e., overwriting the info on disk) or to drop them for the saved metadata.
        This function is a little bit dangerous because it could remove critical information, so use sparingly.
        """
        if self.has_good_saved_story():
            self.read_from_json(pathjoin(self.json_dir(), self.story_json), overwrite_pd = overwrite_pd)
            self.save_story_obj()
        self.repair_pd(overwrite_pd = overwrite_pd)
        self.repair_md(overwrite_md = overwrite_md)
        self.save_story_obj()
    
    # Doesn't check if pd is different when overwriting
    def repair_pd(self, overwrite_pd = False):
        ''' Makes sure the personal metadata is the same in memory as is on disk '''
        good_saved = self.has_good_saved_pd()
        if self.is_good_pd(self.pd_d):
            if overwrite_pd or not good_saved:
                self.save_personal_metadata()
                if self.has_good_saved_pd(): self.checklist["good_pd"] = True
                else: raise Exception("Story <"+self.dir_story+"> did not save personal metadata properly!")
            elif good_saved:
                self.pd_d = load_dict(pathjoin(self.json_dir(), self.pd_json))
                self.checklist["good_pd"] = True
        else:
            if not good_saved:
                raise Exception("Story <"+self.dir_story+"> has no directories nor tags.")
            else:
                self.pd_d = load_dict(pathjoin(self.json_dir(), self.pd_json))
                self.checklist["good_pd"] = True
                
    def repair_md(self, overwrite_md = False):
        ''' Makes sure the automatic metadata is the same in memory as is on disk '''
        good_saved = self.has_good_saved_md()
        if self.is_good_md(self.md_d):
            if overwrite_md or not good_saved:
                self.save_auto_metadata()
                if self.has_good_saved_md(): self.checklist["good_md"] = True
                else: raise Exception("Story <"+self.dir_story+"> did not save automatic metadata properly!")
            elif good_saved:
                self.md_d = load_dict(pathjoin(self.json_dir(), self.md_json))
                self.checklist["good_md"] = True
        else:
            if good_saved:
                self.md_d = load_dict(pathjoin(self.json_dir(), self.md_json))
                self.checklist["good_md"] = True
            else:
                self.checklist["good_md"] = False
        
    def initiate_repairs(self, overwrite_pd=False, force_check=True):
        """
        This function will automatically try to repair whatever is missing about a Story on file.
        If it can solve a problem without going online, it will do so automatically. Otherwise,
            it will put whatever jobs it needs to do online in the `unfinished_jobs` attribute.
        The format of 'unfinished_jobs' is a list of list, with each sublist containing (in order):
            the url to visit, the function to apply to the html of that url, and then additional
            arguments for that function (in order).
        Realistically, these sublists should probably be (kwarg) dictionaries so the order isn't critical.
            That's something for the ole' To-Do list.
                
        If force_check==True, it will manually check to see if the Story:
            1) has been started
            2) has well-formed personal metadata on file
            3) has well-formed automatic metadata on file
            4) has all the images saved.
        If force_check==False, it will just trust whatever the checklist said previously.
        """
        md_bad = False
        if force_check:
            self.checklist["started"] = self.has_directories()
            self.checklist["good_pd"] = self.has_good_saved_pd()
            self.checklist["good_md"] = self.has_good_saved_md()
            self.checklist["all_images"] = self.has_all_images()
            self.save_story_obj()
        
        if not self.checklist["started"]:
            if not self.is_good_pd(self.pd_d):
                raise Exception("Story <"+self.dir_story+"> has no directories nor tags.")
            else:
                self.make_dirs()
                if self.has_directories(): self.checklist["started"] = True
                else: raise Exception("Story <"+self.dir_story+"> did not create directories properly!")
                
        if not self.checklist["good_pd"]:
            self.repair_pd(overwrite_pd=overwrite_pd)
            
        if not self.checklist["good_md"]:
            if not self.is_good_md(self.md_d):
                md_bad = True
            else:
                self.save_auto_metadata()
                if self.has_good_saved_md(): self.checklist["good_md"] = True
                else: raise Exception("Story <"+self.dir_story+"> did not save automatic metadata properly!")
                
        if not self.checklist["all_images"]:
            if md_bad:
                self.unfinished_jobs = [[self.url, self.download_story, True]]
            else:
                image_holes = self.identify_image_holes()
                if image_holes:
                    urls = [self.page_num_to_url(e) for e in image_holes]
                    self.unfinished_jobs = [[url, self.download_image, self.image_dir()] for url in urls]
                else:
                    self.checklist["all_images"] = True
                    self.sync()                    
        elif md_bad == True:
            self.unfinished_jobs = [[self.url, self.download_story, False]]  

    # ---------------------------------- Downloading functions ------------------------------------------------------
    
    def download_story(self, soup_obj, spawn_links=True, *args):
        """
        This function is meant to be the first function in the downloading process, and collects the automatic metadata,
            presumably from the landing page of the comic.
        If spawn_links==True, it will check which image files need to be downloaded and will add those jobs to the
            Story's thread queue.
        """
        thread_safe_mkdir(self.story_dir())
        
        if spawn_links:
            image_holes = self.identify_image_holes()
            urls = [self.page_num_to_url(e) for e in image_holes]
            jobs = [[url, self.download_image, self.image_dir()] for url in urls]
            for job in jobs:
                self.q.put(job)
        
        self.process_auto_metadata(soup_obj)
        self.save_auto_metadata()
        self.save_story_obj()
        return("done!")
    
    @abstractmethod
    def download_image(self, soup_obj, save_dir):
        ''' 
        Abstract method
        Downloads and saves an image based from a page's URL 
        '''
        pass
    
    # ----------------------------------  Functions that check to see if things are valid ------------------------------
    
    @staticmethod
    def is_good_pd(pd_dict):
        ''' 
        Is a personal metadata dictionary well-formed? 
        Currently just checks if it's a dict and has 'rating' as a key 
        '''
        return isinstance(pd_dict, dict) and"rating" in pd_dict.keys()
    @staticmethod
    @abstractmethod
    def is_good_md(md_dict):
        ''' 
        Abstract method
        Is an automatic metadata dictionary well-formed? 
        '''
        pass
    @classmethod
    def is_good_story(cls, story_dict):
        ''' 
        Is a Story structure well-formed? 
        Currently just checks if it's a dict has all the necessary fields.
        '''
        if not isinstance(story_dict, dict): return False
        keys = list(story_dict.keys())
        all_fields = all([e in keys for e in cls.necessary_fields])
        
        return all_fields and cls.is_good_md(story_dict["md_d"]) and cls.is_good_pd(story_dict["pd_d"])
    @classmethod
    def is_good_saved_pd(cls, json_file):
        ''' Identifies whether a Story's saved personal metadata is well-formed. '''
        try:
            d = load_dict(json_file)
            return cls.is_good_pd(d)
        except Exception:
            return(False)
    @classmethod
    def is_good_saved_md(cls, json_file):
        ''' Identifies whether a Story's saved automatic metadata is well-formed. '''
        try:
            d = load_dict(json_file)
            return cls.is_good_md(d)
        except Exception:
            return(False)
    @classmethod
    def is_good_saved_story(cls, json_file):
        ''' Identifies whether a Story's SAVED structure is well-formed. '''
        try:
            d = load_dict(json_file)
            return cls.is_good_story(d)
        except Exception:
            return(False)
    def identify_image_holes(self):
        ''' Identifies any missing page numbers and returns them. '''
        pages = self.page_nums
        try:
            image_files = get_dirlist(self.image_dir())
        except FileNotFoundError:
            return(pages)
        file_nums = [self.filename_to_page(e) for e in image_files]
        missing_nums = [e for e in pages if e not in file_nums]
        return(missing_nums) 
    
    # HACK: wrongly assumes all directories are created at the same time, atomically
    def has_directories(self):
        ''' Does a Story have any directory on disk? '''
        if self.dir_story is None or self.dir_story is "":
            raise Exception("Empty story error!")
        try:
            return all(os.path.exists(e) for e in [self.story_dir(), self.image_dir(), self.json_dir()])
        except Exception:
            return False
    
    # The non-class functions, that by default check a story's own files
    def has_good_saved_pd(self, json_file=None):
        ''' Identifies whether the current Story's SAVED personal metadata is well-formed. '''
        json_file = pathjoin(self.json_dir(), self.pd_json) if json_file is None else json_file
        return self.is_good_saved_pd(json_file)
    def has_good_saved_md(self, json_file=None):
        ''' Identifies whether the current Story's SAVED automatic metadata is well-formed. '''
        json_file = pathjoin(self.json_dir(), self.md_json) if json_file is None else json_file
        return self.is_good_saved_md(json_file)
    def has_good_saved_story(self, json_file=None):
        ''' Identifies whether the current Story's SAVED structure is well-formed. '''
        json_file = pathjoin(self.json_dir(), self.story_json) if json_file is None else json_file
        return self.is_good_saved_story(json_file)
    def has_all_images(self):
        ''' Checks whether all images are downloaded. Returns false if the pages aren't specified. '''
        if self.page_nums is None or not self.page_nums:
            return False # Since it must be that there is no md
        else:
            return len(self.identify_image_holes()) == 0
      
    # ------------------------ Setting functions ----------------------------------------------------
          
    # Get instantly accessible info        
    def set_offline_info(self, match_dict, pd_d=None):
        """
        Sets all the additional offline information that should stay outside the personal
            metadata dictionary, like unique id, page numbers, etc.
        If pd_d is not supplied, it uses whatever it has saved.
        Meant to be called from `Story.make_from_match()`.
        """
        self.unique_id = self.story_id = match_dict["ID"]
        if pd_d is None:
            pd_d = self.pd_d
        if "id_suffix" in pd_d.keys():
            self.unique_id += pd_d["id_suffix"]
            self.page_nums = pd_d["custom_pages"]

    # Sets the paths of the Story
    def set_paths(self, main_path=None, image_path=None, json_path=None, **kwargs):
        main_path  = self.main_path      if main_path  is None else main_path
        image_path = self.image_rel_path if image_path is None else image_path
        json_path  = self.json_rel_path  if json_path  is None else json_path
        if self.unique_id:
            self.dir_story = pathjoin(main_path, self.unique_id)+"/"
        elif not self.dir_story:
            Exception("Story path cannot be set without unique ID or a previously set main directory.")
        self.dir_image = pathjoin(self.dir_story, image_path)
        self.dir_json  = pathjoin(self.dir_story, json_path)
    @abstractmethod
    def set_url(self, base_url=None, **kwargs):
        pass        
    #  ---------------------------------- Handling personal metadata --------------------------------
    
    @classmethod
    def get_pd_from_match(cls, match_dict):
        """
        Gets the pd from a match object (i.e., the input of the 
            personal metadata string).
        """
        assert set(["ID", "tags", "rating"]) == set(match_dict.keys())
        pd_d = cls.handle_pd_tags(match_dict["tags"])
        pd_d["og_match"] = match_dict
        pd_d["untagged?"] = match_dict["tags"] is None or match_dict["tags"] is ""
        
        try:
            pd_d["rating"] = cls.calculate_rating(match_dict["rating"])
        except ValueError as err:
            if " is not a valid rating" in str(err): raise ValueError(str(err) + " for <" + cls.story_id + ">")
            else: raise
        
        return pd_d
    
    @staticmethod        
    def handle_custom_pages(s):
        """
        If you don't want to save ALL the images of a story, you can include the pages you want to keep at the end
            of the input tag string if you enclose them in double square brackets (i.e., [[...]])
        This can be any combination of single pages and ranges, e.g., '[[1,5,7-10,13,3]]'
        This function takes the string inside the brackets and turns it into those page numbers.
        """
        l = s.split(",")
        singles = [int(e) for e in l if "-" not in e]
        doubles = [e.split("-") for e in l if "-" in e]
        vals = set(singles)
        for i, j in doubles:
            for x in range(int(i),int(j)+1):
                vals.add(x)
        return list(vals)     
    
    @classmethod
    def make_id_suffix(cls, s):
        return "_"+re.sub(",", "_", s)
    @classmethod
    def get_nonunique_id(cls, s):
        return s.split("_")[0]
    @abstractmethod
    def page_num_to_url(self, page_num):
        pass
    @abstractmethod
    def filename_to_page(self, filename):
        pass 
           
    @classmethod
    def handle_pd_tags(cls, s):
        """
        Turns a string of personal metadata information (i.e., tags) into a more intelligent personal metadata
            dictionary, separating tags by whitespaces. Tags in all capital letters will be stored separately, 
            and will be given a weight of '10', if you want to weigh tags differently (e.g., for searching).
        You can also specify which pages to save at the end of the tags (for instructions, see `handle_custom_pages()`.
            If you specify custom pages, the directory name will include this information, allowing you to break
            longer stories into multiple shorter stories, each with their own personal metadata.
        """
        d = {"small_tags":[], "big_tags":[], "all_tags":{}}
        if s is None or s is "":
            return(d)
        
        custom_pages = re.findall(r"(?<=\[\[)[0-9\-,]+(?=\]\])", s)
        if len(custom_pages) >= 1:
            assert len(custom_pages) == 1
            d["custom_pages"] = cls.handle_custom_pages(custom_pages[0])
            d["id_suffix"] = cls.make_id_suffix(custom_pages[0])
            s = re.sub(r"\[\[[0-9\-,]+\]\]", "", s)
        
        tags = s.split()
        for tag in tags:
            if tag not in d["all_tags"]:
                if tag.upper() == tag:
                    d["big_tags"] += [tag]
                    d["all_tags"][tag] = 10
                else:
                    d["small_tags"] += [tag]
                    d["all_tags"][tag] = 0
        return d

    @staticmethod
    def calculate_rating(rating):
        """ 
        Calculates a personal rating based on the number and type of punctuation points following a Story's ID
            in the input tag string.
        '!' = 'good', '?' = 'questioning', '~' = 'eh'.
        For example an input tag string like: 
            123456!!!!! --funny long translated black_and_white
            would mean that Story '123456' has a rating of `('good', 5).
        Currently doesn't accept mixed punctuation marks.
        """
        if rating is None or rating is "":
            return ("good", 0)
        elif "!" in rating:
            return ("good", len(rating))
        elif "?" in rating:
            return ("questioning", len(rating))
        elif "~" in rating:
            return ("eh", len(rating))
        else:
            raise ValueError("{} is not a valid rating".format(rating))
             
    # ---------------------------------   Processes the automatic metadata --------------------------------------------
    @abstractmethod
    def process_auto_metadata(self, soup_obj, autosave=True):
        '''
        Abstract method
        Processes the HTML into automatic metadata
        '''
        pass

    # ------------------------  Getting methods and saving methods --------------------------------------------
    # Should probably turn into properties in the future
    def story_dir(self):
        if self.dir_story is "" or self.dir_story is None:
            raise Exception("Story has no main directory specified!")
        return self.dir_story
    def image_dir(self):
        if self.dir_image is "" or self.dir_image is None:
            raise Exception("Story has no image directory specified!")
        return self.dir_image
    def json_dir(self):
        if self.dir_json is "" or self.dir_json is None:
            raise Exception("Story has no JSON directory specified!")
        return self.dir_json
    def story_url(self):
        if self.url is "" or self.url is None:
            raise Exception("Story has no URL specified!")
        return self.url
    def unique_ID(self):
        if self.unique_id is "" or self.unique_id is None:
            raise Exception("Story has no unique ID specified!")
        return self.unique_id
    def story_ID(self):
        if self.story_id is "" or self.story_id is None:
            raise Exception("Story has no story ID specified!")
        return self.story_id
    
    def save_auto_metadata(self):
        assert self.md_d
        jfile = pathjoin(self.json_dir(), self.md_json)
        self.make_dirs()
        save_dict(self.md_d, jfile)
#         make_hash(jfile)
    def save_personal_metadata(self):
        assert self.pd_d
        jfile = pathjoin(self.json_dir(), self.pd_json)
        self.make_dirs()
        save_dict(self.pd_d, jfile)
#         make_hash(jfile)
    def make_dirs(self):
        if not os.path.exists(self.main_path):
            raise Exception("Drive not plugged in?")
        if not all([e is not None and e is not "" for e in [self.dir_story, self.dir_image, self.dir_json]]):
            raise Exception("Story <"+self.dir_story+"> all directories specified before they can be made")
        else:
            # Make the directories
            thread_safe_mkdir(self.story_dir())
            thread_safe_mkdir(self.image_dir())
            thread_safe_mkdir(self.json_dir())
        
    def to_dict(self):
        ''' 
        Converts the Story object to a JSON-able dictionary. 
        The output should generally be saved and then discarded, since this function doesn't
            test for mutability beyond using `.copy()` for dictionaries. Modifying certain items
            in the output could modify the Story's ACTUAL attributes.
         '''
        d = {}
        for k in self.necessary_fields:
            v = getattr(self, k)
            if isinstance(v, dict) or isinstance(v, list): d[k] = v.copy()
            else: d[k] = v
        return d
    def save_story_obj(self, filepath=None):
        ''' Saves story object as JSON file. The default file is `json_dir() + story_json` '''
        if filepath is None:
            filepath = pathjoin(self.json_dir(), self.story_json)
        self.make_dirs()
        save_dict(self.to_dict(), filepath)
    def read_from_json(self, json_file, overwrite_pd=False):
        ''' Loads a Story object's attributes from a JSON file '''
        d = load_dict(json_file)
        for k, v in d.items():
            if k in ["pd_d", "md_d"] and not v: pass
            elif k is "pd_d" and overwrite_pd is True and self.is_good_pd(self.pd_d): pass
            else: setattr(self, k, v)

