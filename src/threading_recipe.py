'''
Created on Mar 12, 2020

@author: zburchill
'''

'''
THIS IS THE OLD THREADING RECIPE THAT USES A QUEUE AND GLOBAL VARIABLES =====================================
'''

import threading
from queue import Queue

NUM_THREADS = 20

def start_threads(l):
    from time import sleep
    global your_q
    your_q = Queue()
    for i in range(): 
        t = threading.Thread(target=your_worker)
        t.daemon = True
        t.start()
    # Put the data into the queue
    for e in l:
        your_q.put(e)
    # Just for output if you want
    while (your_q.qsize() > 0):
        print("There are still {0} worker threads in the queue!".format(your_q.qsize()))
        sleep(30)
    # Block until all tasks done
    your_q.join()
    
def your_worker():
    # Could do without global but whatever
    global your_q
    while True:
        # Get the info that was put on the stack
        arg1, arg2, *moreargs = your_q.get()
        # Needs the try statement to be safer
        try:
            # Do stuff
            pass
        except Exception as error_m:
            # E.g., if arg1 is an ID
            print("Uh oh, error with: ".format(arg1))
            raise
        finally:
            your_q.task_done()
            
'''
THIS IS THE 'NEW' THREADING RECIPE THAT USES A POOL AND RETURNS ALL VALUES TOGETHER =====================================
'''            
            
from multiprocessing.dummy import Pool as ThreadPool  # holy shit this is easy

NUM_THREADS = 20

# If you don't need the worker function to have more than one argument,
#    also, if you want to use the crappier non-with syntax:
def run_a_pool_v1(l, request_rate):
    from time import sleep
    
    def worker(e):
        # Do stuff
        pass
        # Sleep a little bit if things are going to quickly
        sleep(NUM_THREADS/request_rate) #SLEEEEEP
        return "This is the return value"
    
    pool = ThreadPool(NUM_THREADS)
    results = pool.map(worker, l)
    pool.close()
    pool.join()
    return results

# Or even better, use this version!!!!!!!
def run_a_pool_v2(l, request_rate):
    from time import sleep 
    # Worker takes multiple arguments
    def worker(e, rr):
        # Do stuff
        pass
        # Sleep a little bit if things are going to quickly
        sleep(NUM_THREADS/rr) #SLEEEEEP
        return "This is the return value"
    
    # We can use repeat() in zip() to give a constant value for every value of l
    from itertools import repeat
    with ThreadPool(NUM_THREADS) as pool:
        # starmap lets use you use multiple arguments
        results = pool.starmap(worker, zip(l, repeat(request_rate)))
    
    return results




        