'''
Created on Oct 6, 2018

@author: zburchill
'''
from bs4 import BeautifulSoup
import requests
import json, shutil, os # for saving, mostly
from warnings import warn
# My stuff
from basic_functions import clean_find, clean_find_all, join_urls, load_image, save_image,\
    soupify, get_string, get_strings, get_full_string
import numpy, pandas


MAIN_PAGE = "https://efdsearch.senate.gov/search/"
INTRO_PAGE = "https://efdsearch.senate.gov/search/home/"
REQUEST_PAGE = "https://efdsearch.senate.gov/search/report/data/" #referer: https://efdsearch.senate.gov/search/

search_candidates_dict = {"draw": "1",
"columns[0][data]": "0",
"columns[0][name]": "",
"columns[0][searchable]": "true",
"columns[0][orderable]": "true",
"columns[0][search][value]": "",
"columns[0][search][regex]": "false",
"columns[1][data]": "1",
"columns[1][name]": "",
"columns[1][searchable]": "true",
"columns[1][orderable]": "true",
"columns[1][search][value]": "",
"columns[1][search][regex]": "false",
"columns[2][data]": "2",
"columns[2][name]": "",
"columns[2][searchable]": "true",
"columns[2][orderable]": "true",
"columns[2][search][value]": "",
"columns[2][search][regex]": "false",
"columns[3][data]": "3",
"columns[3][name]": "",
"columns[3][searchable]": "true",
"columns[3][orderable]": "true",
"columns[3][search][value]": "",
"columns[3][search][regex]": "false",
"columns[4][data]": "4",
"columns[4][name]": "",
"columns[4][searchable]": "true",
"columns[4][orderable]": "true",
"columns[4][search][value]": "",
"columns[4][search][regex]": "false",
"order[0][column]": "1",
"order[0][dir]": "asc",
"order[1][column]": "0",
"order[1][dir]": "asc",
"start": "0",
"length": "100",
"search[value]": "",
"search[regex]": "false",
"report_types": "[]",
"filer_types": "[4]",   # current senators is "[1]"
"submitted_start_date": "01/01/2012 00:00:00",
"submitted_end_date": "",
"candidate_state": "",
"senator_state": "",
"office_id": "",
"first_name": "",
"last_name": ""}


# ------------------------------------------ Basic functions -----------------------------------

def read_from_json(filename):
    if os.access(filename, os.R_OK):
        fileobj = open(filename, 'r')
        with fileobj:
            fileobj.seek(0)
            data = json.load(fileobj)
        return(data)
    else:
        BaseException("file not readable")

def save_as_json(filename, obj):
    tempname = filename + '.tmp'
    fileobj = open(tempname, 'w')
    try:
        json.dump(obj, fileobj, separators=(',', ':'))
    except Exception:
        os.remove(tempname)
        raise
    shutil.move(tempname, filename)
    
def remove_extra_whitespace(s):
    return(" ".join(s.split()))



# ------------------------------------------ Functions to scrape the report URLs -----------------------------------

def check_box(cur_sesh, url=INTRO_PAGE):
    first_get = cur_sesh.get(INTRO_PAGE)
    payload = {"prohibition_agreement": "1",
               "csrfmiddlewaretoken": get_middleware_token(first_get.text) }
    first_post = gov_post(cur_sesh, url = url, payload = payload, from_resp=first_get)
    return(first_post)

def get_middleware_token(text):
    soup_obj = BeautifulSoup(text)
    l = clean_find_all(soup_obj, ['input',{'name': 'csrfmiddlewaretoken'}])
    assert(len(l)==1)
    return(l[0]["value"])
    
def get_cookies():
    with requests.Session() as s:
        check_box(s)
        print(s.cookies.get_dict())
        cookies = s.cookies.get_dict()
    return(cookies)

def gov_post(sesh, url, payload, from_resp=None, extra_headers=None):
    if sesh is None:
        raise Exception("Not Implemented Yet")
    if from_resp is None:
        raise Exception("Not Implemented Yet")
    header = {"referer":from_resp.url}
    if "xhr.setRequestHeader(\"X-CSRFToken\"" in from_resp.text:
        header["X-CSRFToken"] = sesh.cookies.get_dict()["csrftoken"]
    if extra_headers:
        for k, v in extra_headers.items():
            if k in header:
                warn("`{0}` (`{1}`) already in header (`{2}`)".format(k, v, header[k]))
            header[k] = v 
    resp = sesh.post(url, data = payload, headers=header)
    return(resp)
    

# example of a pdf page: https://efdsearch.senate.gov/search/view/paper/AEE22AEA-96F7-4973-B26C-A0D8B08AD22E/

def get_rowdata_from_payload(payload, sesh, previous_post, req_page = REQUEST_PAGE):
    resp = gov_post(sesh, req_page, payload = payload, from_resp = previous_post)
    jall = json.loads(resp.text)
    jdata = jall["data"]
    return(jdata)

def move_next(payload_dict, new_len = None):
    cur_pos = int(payload_dict["start"])
    num_res = int(payload_dict["length"])
    payload_dict["start"] = str(cur_pos+num_res)
    if new_len:
        payload_dict["length"] = str(new_len)
    return(payload_dict)

def get_all_rows(base_payload_dict, filer_type="[4]"):
    base_payload_dict["filer_types"] = filer_type
    with requests.Session() as s:
        first_post = check_box(s)
        
        rows = get_rowdata_from_payload(base_payload_dict, s, first_post, REQUEST_PAGE)
        all_rows = rows
        
        while (len(rows) == int(base_payload_dict["length"])):
            base_payload_dict = move_next(base_payload_dict)
            rows = get_rowdata_from_payload(base_payload_dict, s, first_post, REQUEST_PAGE)
            all_rows += rows
            
        return(all_rows)
        
        
''' This stuff gets all the urls we need to scrape: ''' 
# data = get_all_rows(search_candidates_dict)
# save_as_json("/Users/zburchill/Desktop/delete.json", data)
# data = read_from_json("/Users/zburchill/Desktop/delete.json")
# example https://efdsearch.senate.gov/search/view/annual/f4ab7cf4-80a0-43ab-ae74-c532c1515892/


# ------------------------------------------ Functions that scrape the individual reports -----------------------------------

def get_rows_in_table(table_obj):
    rows = clean_find_all(table_obj, ['tr',{'class': 'nowrap'}])
    if len(rows) == 0:
        return(None)
    else: 
        return(rows)   

# Check to see if all row lengths are equal
def are_rowlens_equal(rows):
    firstlen = len(rows[0])
    return(all([len(row) == firstlen for row in rows]))

# Careful though, this removes the row values from ALL instances of the soup object
def extract_columns(row_obj, colval = "td"):
    cols = clean_find_all(row_obj, [colval])
    assert len(cols) > 0
    extracted_cols = [col.extract() for col in cols]
    return(extracted_cols)

# For some of the tables, there's an empty first row. this drops it
def drop_empty_first_row(rows):
    first_col_strings = [get_full_string(row[0]) for row in rows]
    if all([s.strip() == "" for s in first_col_strings]):
        return([row[1:] for row in rows])
    else:
        return(rows)

def is_pdf_page(soup_obj):
    return(clean_find(soup_obj, ["div", {"id":"myCarousel"}]) is not None)

def get_report_tables(soup_obj):
    tables = clean_find_all(soup_obj, ['section',{'class': 'card mb-2'}])
    if len(tables) != 12:
        raise Exception(str(len(tables)) + " table headers found instead of 12!")
    dict_table = {}
    for table in tables:
        df = DataTable(table)
        dict_table[df.title] = df
    return(dict_table)

def get_report_metadata(soup_obj):
    if is_pdf_page(soup_obj):
        return(None)
    def temp_get_string(tag):
        try:
            text = remove_extra_whitespace(get_full_string(tag))
        except AttributeError as e:
            text = None
        return(text)
    d = {}
    d["report_name"] = temp_get_string(clean_find(soup_obj, ["h1", {"class": "mb-2"}]))
    d["filer_name"] = temp_get_string(clean_find(soup_obj, ["h2", {"class": "filedReport"}]))
    filing_dateime_string = temp_get_string(clean_find(soup, ["p", {"class": "muted font-weight-bold"}]))
    candidacy_string = temp_get_string(clean_find(soup_obj, ["p", {"class": "muted"}]))
    d["date_filed"] = filing_dateime_string.split()[1]
    d["time_filed"] = " ".join(filing_dateime_string.split()[-2:])
    d["state"] = candidacy_string.split()[3] # pretty hacky, i admit
    d["candidacy_date"] = candidacy_string.split()[-1]
    
    return(d)
    
    
# ------------------------------------------ Classes that house the scraped data -----------------------------------
class Report(dict):
    '''
    Inherits dict, but has metadata values and a custom init function that takes in a soup object.
    If it's a pdf page, it will be an empty dict
    '''
    
    name = candidate = filing_date = time_filed = state = candidacy_date = ""
    is_pdf = "N/A"
    
    def __init__(self, soup_obj):
        d = get_report_metadata(soup_obj)
        if d is None:
            self.is_pdf = True
            self.name = self.candidate = self.filing_date = self.time_filed = self.state = self.candidacy_date = None
            dict.__init__(self)
        else:
            self.is_pdf = False
            self.name = d["report_name"]
            self.candidate = d["filer_name"]
            self.filing_date = d["date_filed"]
            self.time_filed = d["time_filed"]
            self.state = d["state"]
            self.candidacy_date = d["candidacy_date"]
            
            tables = get_report_tables(soup_obj)
            dict.__init__(self, tables)
        
class DataTable(pandas.DataFrame):
    title = None

    def __init__(self, soup_obj, *args, **kwds):
        temp = clean_find(soup_obj, ['div',{'class': 'card-body'}])
        text = "".join(get_strings(clean_find(temp, ["h3",{'class': 'h4'}])))
        self.title = text.split(".")[0]
        
        raw_rows = get_rows_in_table(soup_obj)
        if raw_rows is not None:
            # Get the header
            header_row = clean_find_all(soup_obj.thead.tr, ["th"])
            header_row_text = [get_full_string(e) for e in header_row]
            header_row_text = ["Row Number"] + [e.strip() for e in header_row_text if e.strip() != "" and e.strip() != "#"]

            rows = [extract_columns(row) for row in raw_rows]
            assert are_rowlens_equal(rows)
            
            if (len(header_row_text) == len(rows[0]) - 1):
                rows = drop_empty_first_row(rows)
            if (len(header_row_text) != len(rows[0])):
                warn("Header: `"+ "`, `".join(header_row_text)+ "`")
                warn("Row: `"+ "`, `".join([get_string(e).strip() for e in rows[0]])+ "`")
                raise BaseException("Header has length {0} and rows are length {1}".format(len(header_row_text), 
                                                                                           len(rows[0])))

            pandas.DataFrame.__init__(self, data=rows, columns=header_row_text, *args, **kwds)
        else:
            pandas.DataFrame.__init__(self, *args, **kwds)
            
            
            
            
            
            
try:
    cookies = get_cookies()
    soup = soupify("https://efdsearch.senate.gov/search/view/annual/f4ab7cf4-80a0-43ab-ae74-c532c1515892/", cookies=cookies)
except Exception:
    with open("/Users/zburchill/Desktop/delete.html") as f:
        soup = BeautifulSoup(f)
groups = clean_find_all(soup, ['section',{'class': 'card mb-2'}])

# soup = soupify("https://efdsearch.senate.gov/search/view/paper/AEE22AEA-96F7-4973-B26C-A0D8B08AD22E/", cookies=cookies)

rows = get_rows_in_table(groups[1])
# print(rows)
rows2 = clean_find_all(groups[1].thead.tr, ["th"])
print([get_string(e) for e in rows2])

# print(rows[0].find_all("td"))
# print("--------------------------")
# new_row = extract_columns(rows[0])
# print(new_row)
# print(groups[1])
# print(groups)
# print(len(groups))


    





            




# with requests.Session() as s:
#     first_post = check_box(s)
#  
#     resp = gov_post(s, REQUEST_PAGE, payload = search_candidates_dict,
#                     from_resp = first_post)
#     jall = json.loads(resp.text)
#     jdata = jall["data"]
#     print(jdata)
#      
#     tester = s.get("https://efdsearch.senate.gov/search/view/annual/92e21be2-80d5-4cb6-b3b6-16cb4805809d/")
#     print(tester.text)




# ''' ############################################################     '''
# from urllib.parse import urlencode, quote_plus
# from urllib3.exceptions import HTTPError
# class CRPApiError(Exception):
#     """ Exception for CRP API errors """
# 
# # results #
# class CRPApiObject(object):
#     def __init__(self, d):
#         self.__dict__ = d
# 
# # namespaces #
# 
# class CRP(object):
# 
#     apikey = None
#     
#     @staticmethod
#     def _apicall(func, params):
#         if CRP.apikey is None:
#             raise CRPApiError('Missing CRP apikey')
#         print(params)
#         url = 'https://www.opensecrets.org/api/?method=%s&output=json&apikey=%s&%s' % \
#               (func, CRP.apikey, urlencode(params))
# 
#         
#         try:
#             response = requests.get(url).text
#             return json.loads(response)['response']
#         except HTTPError as e:
#             raise CRPApiError(e.read())
#         except (ValueError, KeyError) as e:
#             raise CRPApiError('Invalid Response')
# 
#     class getLegislators(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('getLegislators', kwargs)['legislator']
#             return results
# 
#     class memPFDprofile(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('memPFDprofile', kwargs)['member_profile']
#             return results
# 
#     class candSummary(object):
#         @staticmethod
#         def get(**kwargs):
#             result = CRP._apicall('candSummary', kwargs)['summary']
#             return result['@attributes']
# 
#     class candContrib(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('candContrib', kwargs)['contributors']['contributor']
#             return results
# 
#     class candIndustry(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('candIndustry', kwargs)['industries']['industry']
#             return results
# 
#     class candSector(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('candSector', kwargs)['sectors']['sector']
#             return results
# 
#     class candIndByInd(object):
#         @staticmethod
#         def get(**kwargs):
#             result = CRP._apicall('CandIndByInd', kwargs)['candIndus']
#             return result['@attributes']
# 
#     class getOrgs(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('getOrgs', kwargs)['organization']
#             return results
#             
#     class orgSummary(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('orgSummary', kwargs)['organization']
#             return results
#             
#     class congCmteIndus(object):
#         @staticmethod
#         def get(**kwargs):
#             results = CRP._apicall('congCmteIndus', kwargs)['committee']['member']
#             return results
#         
# ''' ############################################################     '''
# ''' ############################################################     '''




# CRP.apikey = 'ca0a147fb514ecd672a84ccfe504b5cf'
# print(CRP.getLegislators.get(id='NJ04'))

# import csv 
# 
# # from: https://www.opensecrets.org/resources/datadictionary/Data%20Dictionary%20pfd_income.htm
# header = ["ID","Chamber","CID","CalendarYear",
#           "ReportType","IncomeSource","Orgname",
#           "Ultorg","Realcode","Source","IncomeLocation",
#           "IncomeSpouseDep","IncomeType","IncomeAmt",
#           "IncomeAmtText","Dupe"]
# print(len(header))
# 
# with open("/Users/zburchill/Downloads/PDF_STuff/PFD/PFDincome.txt") as csv_file:
#     csv_reader = csv.DictReader(csv_file, delimiter=",", quotechar="|", fieldnames=header)
#     line_count = 0
#     for row in csv_reader:
#         print(row)
#         line_count+=1
#         if line_count == 10:
#             break
#     print("A")
#     print(csv_reader["IncomeAmt"][1:4])
#     lines = csv_file.read().splitlines()
#     for line in lines[1:10]:
#         print(line.split(","))
