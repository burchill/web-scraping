'''
Created on Oct 6, 2018

@author: zburchill
'''
from bs4 import BeautifulSoup
import requests
import json, shutil, os # for saving, mostly
from warnings import warn
from multiprocessing.dummy import Pool as ThreadPool  # holy shit this is easy
# My stuff
from basic_functions import clean_find, clean_find_all, join_urls, load_image, save_image,\
    soupify, get_string, get_strings, get_full_string, save_obj, load_obj, PageScrapeException
import pandas
from time import sleep # so we don't go too crazy


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
"order[0][column]": "4",  # this will order by date
"order[0][dir]": "asc",
"order[1][column]": "0",
"order[1][dir]": "desc",  # this will put newest dates first. the opposite is "asc"
"start": "0",
"length": "100",
"search[value]": "",
"search[regex]": "false",
"report_types": "[7]", # this is for annual reports only (includes candidate reports). for all docs, use "[]"
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

def process_url_datum(l):
    assert(len(l) == 5)
    bs = BeautifulSoup(l[3])
    report_name = get_full_string(bs.a).strip()
    amendment = "no"
    if "amendment" in report_name.lower():
        try:
            amendment = int(report_name.split()[-1][0:-1]) # kinda hacky
        except ValueError:
            amendment = 0 # ie '(Amendment)'
    link = str(bs.a["href"])
    d = {"first": l[0].strip(), "last": l[1].strip(), "filer_type": l[2].strip(), "date": l[4].strip(), 
         "amendment": amendment, "report_name": report_name, "link": link}
    return(d)
        
    

# ------------------------------------------ Functions that scrape the individual reports -----------------------------------



def scrape_reports(l, request_rate):
    NUM_THREADS = 10
    
    cookies = get_cookies()
    # so it can access cookies automatically
    def get_report(data_dict, 
                   base_url = "https://efdsearch.senate.gov"):
        url = join_urls(base_url, data_dict["link"])
        try:
            soup = soupify(url, cookies=cookies)
        except requests.exceptions.Timeout as e:
            sleep(10)
            try:
                soup = soupify(url, timeout_sec=60, cookies=cookies)
            except Exception as e:
                warn(e)
                return("url didn't work: "+url)
            
        try:
            report = Report(soup, process_html = False)
            report.set_row_metadata(data_dict)
        except PageScrapeException as e:
            warn(url)
            raise e
        
        sleep(NUM_THREADS/request_rate) #SLEEEEEP
        return(report)
    
    pool = ThreadPool(NUM_THREADS)
    results = pool.map(get_report, l)
    pool.close()
    pool.join()
    return(results)

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

def ommitted_assets(soup_obj):
    checkbox = clean_find(soup_obj, ["input",{"name":"filing_omitted_assets"}])
    try: return(checkbox["checked"]=="checked")
    except KeyError: return(False)

def get_report_tables(soup_obj, *args, **kwargs):
    tables = clean_find_all(soup_obj, ['section',{'class': 'card mb-2'}])
    if len(tables) != 12:
        raise Exception(str(len(tables)) + " table headers found instead of 12!")
    dict_table = {}
    for table in tables:
        df = DataTable(table, *args, **kwargs)
        dict_table[df.title] = df
    return(dict_table)

def get_report_metadata(soup_obj):
    if is_pdf_page(soup_obj):
        return(None)
    def temp_get_string(tag):
        try:
            text = remove_extra_whitespace(get_full_string(tag))
        except AttributeError:
            text = None
        return(text)
    d = {}
    d["report_name"] = temp_get_string(clean_find(soup_obj, ["h1", {"class": "mb-2"}]))
    d["filer_name"] = temp_get_string(clean_find(soup_obj, ["h2", {"class": "filedReport"}]))
    filing_dateime_string = temp_get_string(clean_find(soup_obj, ["p", {"class": "muted font-weight-bold"}]))
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
    
    name = candidate = filing_date = time_filed = state = candidacy_date = None
    omitted_assets = is_pdf = amendment = None
    row_metadata = None
    
    def set_amendment(self, amendment):
        self.amendment = amendment
        
    def is_amendment(self):
        return(self.amendment != "no" and self.amendment is not None)
    
    # Just in case this is ever useful
    def set_row_metadata(self, metadata_dict):
        self.row_metadata = metadata_dict
        if "amendment" in metadata_dict:
            self.amendment = metadata_dict["amendment"]
    
    def __init__(self, soup_obj, *args, **kwargs):
        d = get_report_metadata(soup_obj)
        if d is None:
            self.is_pdf = True
            self.name = self.candidate = self.filing_date = self.time_filed = self.state = self.candidacy_date = None
            dict.__init__(self)
        else:
            self.omitted_assets = ommitted_assets(soup_obj)
            self.is_pdf = False
            self.name = d["report_name"]
            self.candidate = d["filer_name"]
            self.filing_date = d["date_filed"]
            self.time_filed = d["time_filed"]
            self.state = d["state"]
            self.candidacy_date = d["candidacy_date"]
            
            tables = get_report_tables(soup_obj, *args, **kwargs)
            dict.__init__(self, tables)
        
class DataTable(pandas.DataFrame):
    title = None
    
    def get_table_header(self, soup_obj):
        header_row = clean_find_all(soup_obj.thead.tr, ["th"])
        header_row_text = [get_full_string(e) for e in header_row]
        header_row_text = [e.strip() for e in header_row_text if e.strip() != "" and e.strip() != "#"]
        if header_row_text[0] != "Document Title":
            header_row_text = ["Row Number"] + header_row_text
        return(header_row_text)
        
    def __init__(self, soup_obj, process_html, *args, **kwargs):
        temp = clean_find(soup_obj, ['div',{'class': 'card-body'}])
        text = "".join(get_strings(clean_find(temp, ["h3",{'class': 'h4'}])))
        self.title = text.split(".")[0]
        
        raw_rows = get_rows_in_table(soup_obj)
        if raw_rows is not None:
            header_row_text = self.get_table_header(soup_obj)

            rows = [extract_columns(row) for row in raw_rows]
            assert are_rowlens_equal(rows)
            
            if (len(header_row_text) == len(rows[0]) - 1):
                rows = drop_empty_first_row(rows)
            if (len(header_row_text) != len(rows[0])):
                warn("Header: `"+ "`, `".join(header_row_text)+ "`")
                warn("Row: `"+ "`, `".join([get_string(e).strip() for e in rows[0]])+ "`")
                raise PageScrapeException("Header has length {0} and rows are length {1}".format(len(header_row_text), 
                                                                                           len(rows[0])))
            if process_html == False:
                rows = [[str(cell) for cell in row] for row in rows]
            else:
                raise BaseException("Not implemented")
            
            pandas.DataFrame.__init__(self, data=rows, columns=header_row_text, *args, **kwargs)
        else:
            pandas.DataFrame.__init__(self, *args, **kwargs)
            
    
# ---------------------------------------------- MAIN ----------------------------------------------------------#

''' This stuff gets all the urls we need to scrape: ''' 
# data = get_all_rows(search_candidates_dict)
# save_as_json("/Users/zburchill/Desktop/delete.json", data)
# data = read_from_json("/Users/zburchill/Desktop/delete.json")
# # example https://efdsearch.senate.gov/search/view/annual/f4ab7cf4-80a0-43ab-ae74-c532c1515892/

# # Change it into the senator search
# senator_dict = search_candidates_dict
# senator_dict["submitted_start_date"] = "01/01/2017 00:00:00"
# data = get_all_rows(senator_dict, filer_type="[1]")
# save_as_json("/Users/zburchill/Desktop/senators.json", data)
# data = read_from_json("/Users/zburchill/Desktop/senators.json")


''' This stuff scrapes the aforementioned pages: '''         
# data = read_from_json("/Users/zburchill/Desktop/delete.json")
# data = [process_url_datum(e) for e in data]
# print(len(data))
# reports = scrape_reports(data, 0.5)
# save_obj(reports, "candidate_reports")

# For incumbents
# data = read_from_json("/Users/zburchill/Desktop/senators.json")
# data = [process_url_datum(e) for e in data]
# reports = scrape_reports(data, 0.5)
# save_obj(reports, "incumbent_reports")


reports = load_obj("incumbent_reports")
# reports = load_obj("candidate_reports")
amendments = [e for e in reports if e.is_amendment()]
non_amendment_names = [e.candidate for e in reports if not e.is_amendment()]

print(set([e.row_metadata["first"]+" "+e.row_metadata["last"] for e in reports if e.is_pdf == True]))
joes = [e for e in reports if ((e.is_pdf == True) and (e.row_metadata["last"] == "Donnelly"))]
pdfs = [e for e in reports if e.is_pdf == True]
d={}
for e in pdfs:
    if e.row_metadata["last"].lower() in d:
        d[e.row_metadata["last"].lower()] += 1
    else:
         d[e.row_metadata["last"].lower()] = 1
print(d)

print(joes)
x=0/0
# ya = [(e.candidate, e.row_metadata["first"]+" "+e.row_metadata["last"], e.state) for e in reports if e.is_pdf == False]
# ya = list(set(ya))
# with open("/Users/zburchill/Desktop/delete2.txt", "w") as f:
#     f.write("\n".join(["XXXXX".join(e) for e in ya]))
#     
# print("\n".join([e[0]+"XXXXX"+e[1] for e in ya]))
    
# print(ya[1:5])
print(reports[1].row_metadata)


print(reports[1]["Part 2"]["Who Was Paid"])
print("AAAAAA")
print(print(reports[1]["Part 2"].loc[:,"Who Was Paid"]))

def add(d, k):
    if k in d:
        d[k] += 1
    else:
        d[k] = 1


# part 2, who was paid is self or spouse rn




cols = reports[1]["Part 2"]
for col in cols:
    print("-------")
    print(col)

d = {}
for report in reports:
    if report.is_pdf == False:
        try:
            cols = report["Part 2"]["Who Was Paid"]
            other_cols = report["Part 2"]["Amount Paid"]
            for i in range(len(cols)):
                val = "".join(BeautifulSoup(cols[i]).stripped_strings)
                if val == "Spouse":
                    add(d, "".join(BeautifulSoup(other_cols[i]).stripped_strings))
        except Exception:
            pass
print(d)
        
#             
        




# soup = soupify("https://efdsearch.senate.gov/search/view/annual/bdbea374-64ea-454b-ac61-1f0a0346e2f7/", cookies=get_cookies())
# report = Report(soup, process_html = False)


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


