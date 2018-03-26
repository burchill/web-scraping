'''
Created on Mar 26, 2018

@author: zburchill
'''
import random
from random import randint


class countcalls(object):
    "Decorator that keeps track of the number of times a function is called."

    __instances = {}
    __random_numbers = 0

    def __init__(self, f):
        self.__f = f
        self.__numcalls = 0
        self.__random_numbers = randint(0, 100)
        countcalls.__instances[f] = self

    def __call__(self, *args, **kwargs):
        self.__numcalls += 1
        return self.__f(*args, **kwargs)

    def count(self):
        "Return the number of times the function f was called."
        return countcalls.__instances[self.__f].__numcalls
    
    def random_num(self):
        "Return the number of times the function f was called."
        return countcalls.__instances[self.__f].__random_numbers

    @staticmethod
    def counts():
        "Return a dict of {function: # of calls} for all registered functions."
        return dict([(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances])


# class my_function(object):
#     
#     def __init__(self):
#         self.__numcalls = 0
#         self.__random_number = randint(0, 100)
#         
#     def __call__(self, x, y=2, *args, **kwargs):
#         self.__numcalls += 1
#         return(x+y)
#     
#     def count(self):
#         "Return the number of times the function f was called."
#         return my_function.__numcalls
#     
#     def random_num(self):
#         return(self.__random_number)
#     
# print(my_function(2))
# print(my_function(2))
# print(my_function(2,10))     

@countcalls
def x():
    print("AAAA")
    print(x.count())
    print(x.random_num())
 
@countcalls
def g():
    print("ZZZZZZZ")
    print(g.count())
    print(g.random_num())
x()
x()
x()
print(x.count())
g()
print(g.random_num())