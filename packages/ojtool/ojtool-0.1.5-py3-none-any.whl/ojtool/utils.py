"""
包含常用常量与各种工具类
"""
import math
import random as rd
from typing import Callable, TypeVar
from . import data
import bisect

PI = math.pi
E = math.e

ALPHABET_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
NUMBERS = "0123456789"

def num(a, b):
    '''
    生成 [a,b] 范围内的随机整数。
    PS：函数内部自动转整数，自动处理大小关系。
    '''
    a = int(a)
    b = int(b)
    if a < b:
        return rd.randint(a, b)
    else:
        return rd.randint(b, a)
    

def prime_e0_e2():
    '''
    获取 0-99 范围内的所有质数。
    '''
    return data.__PRIME_NUMBERS[0]

def prime_e2_e3():
    '''
    获取 100-999 范围内的所有质数。
    '''
    return data.__PRIME_NUMBERS[1]

def prime_e3_e4():
    '''
    获取 1000-9999 范围内的部分质数。
    '''
    return data.__PRIME_NUMBERS[2]

def prime_e4_e5():
    '''
    获取 10000-99999 范围内的部分质数。
    '''
    return data.__PRIME_NUMBERS[3]

def prime_e5_e6():
    '''
    获取 100000-999999 范围内的部分质数。
    '''
    return data.__PRIME_NUMBERS[4]

def prime_e6_e7():
    '''
    获取 1000000-9999999 范围内的部分质数。
    '''
    return data.__PRIME_NUMBERS[5]

def prime_e7_e8():
    '''
    获取 10000000-99999999 范围内的部分质数。
    '''
    return data.__PRIME_NUMBERS[6]


T = TypeVar('T')

class Seq():
    def __init__(self, func: Callable[[int, Callable[[int], T]], T], initData=()):
        '''
        序列生成器。
        '''
        if not callable(func):
            self.func = lambda i, f: 0
        else:
            self.func = func

        if isinstance(initData, dict):
            self.data = initData.copy()
        elif isinstance(initData, list) or isinstance(initData, tuple):
            self.data = dict(enumerate(initData))
        else:
            self.data = {}
    
    def get(self, id: int) -> T:
        '''
        获取指定id的序列值。
        '''
        if id in self.data:
            return self.data[id]
        else:
            v = self.func(id, self.get)
            self.data[id] = v
            return v
    
    def getrange(self, start: int, end: int) -> list[T]:
        '''
        获取指定范围内的序列值列表，包含start和end。
        '''
        if start >= end:
            start, end = end, start
        return [self.get(i) for i in range(start, end+1)]
    
# def prime(a, b):
#     '''
#     获取 [a,b] 范围内的所有质数。
#     PS：函数内部自动转整数，自动处理大小关系。
#     '''
#     a = int(a)
#     b = int(b)
#     if a > b:
#         (a,b) = (b,a)
#     ia = bisect.bisect_left(data.PRIMARY, a)
#     ib = bisect.bisect_right(data.PRIMARY, b)
#     if ib == ia:
#         if data.PRIMARY[ia] == a:
#             return [a]
#         return []
#     return data.PRIMARY[ia: ib]
