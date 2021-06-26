import pytz
import aiohttp
import time
import asyncio
import discord
from datetime import datetime

class Cache():
    def __init__(self,):
        self.cache = {}
    def add_and_get(self, key, item, timeout=None):
        self.add(key, item, timeout)
        return self.get(key)
    def add(self, key, item, timeout=None):
        if key in self.cache and timeout is not None:
            if time.time()-self.cache[key]["timestamp"] > timeout:
                self.cache[key]["function"] = item
                self.cache[key]["timestamp"] = time.time()
        elif key not in self.cache:
            self.cache[key] = {"function":item, "timestamp" :time.time()}
        return
    def get(self, key):
        return self.cache.get(key)
    def __contains__(self, item):
        return True if item in self.cache.keys() else False
    def cached(self, timeout=600):
        def __decorator_wrapper(func):
            def __decorator(*args, **kwargs):
                key = None
                if not args:
                    key = "null"
                else:
                    key = " ".join([str(x) for x in args])
                if func.__name__ in self.cache:
                    if key in self.cache[func.__name__]:
                        if time.time()-self.cache[func.__name__][key]["timestamp"] > timeout:
                            
                            self.cache[func.__name__][key] = {"function" : func(*args, **kwargs)}
                            self.cache[func.__name__][key]["timestamp"] = time.time()
                    else:
                        self.cache[func.__name__][key] = {"function" : func(*args, **kwargs)}
                        self.cache[func.__name__][key]["timestamp"] = time.time()
                else:
                    self.cache[func.__name__] = {}
                    self.cache[func.__name__][key] = {"function": func(*args, **kwargs)}
                    self.cache[func.__name__][key]["timestamp"] = time.time()
                return self.cache[func.__name__][key]["function"]
            return __decorator
        return __decorator_wrapper
    def async_cached(self, timeout=600):
        def __decorator_wrapper(func):
            async def __decorator(*args, **kwargs):
                key = None
                if not args:
                    key = "null"
                else:
                    key = " ".join([str(x) for x in args])
                if func.__name__ in self.cache:
                    if key in self.cache[func.__name__]:
                        if time.time()-self.cache[func.__name__][key]["timestamp"] > timeout:
                            self.cache[func.__name__][key] = {"function" : await func(*args, **kwargs)}
                            self.cache[func.__name__][key]["timestamp"] = time.time()
                    else:
                        self.cache[func.__name__][key] = {"function" : await func(*args, **kwargs)}
                        self.cache[func.__name__][key]["timestamp"] = time.time()
                else:
                    self.cache[func.__name__] = {}
                    self.cache[func.__name__][key] = {"function": await func(*args, **kwargs)}
                    self.cache[func.__name__][key]["timestamp"] = time.time()
                return self.cache[func.__name__][key]["function"]
            return __decorator
        return __decorator_wrapper
cache_obj = Cache()

def utc2local(timestamp):
    local_tz = pytz.timezone("Europe/Helsinki")
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(local_tz)
def ts2string(timestamp, pattern='%d.%m.%Y %H:%M:%S | %Z%z'):
    return utc2local(timestamp).strftime(pattern)
async def fetchURL(url, params={}):
    async with aiohttp.ClientSession() as client:
        async with client.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                return None

def ts2ifmodifiedsince(timestamp):
    return time.strftime("%a, %d %b %Y %H:%M%S GMT", time.gmtime(timestamp))

def is_number(m):
    try:
        float(m)
        return True
    except ValueError:
        return False
def is_int(m):
    try:
        float(m)
        return True
    except ValueError:
        return False
def log(messages, file="log.txt"):
    if isinstance(messages, str):
        messages = [messages]
    fo = open("log.txt", "a+")
    for i in messages:
        fo.write(str(i)+"\n")
    fo.close()
def run_in_executor(function):
    async def __decorator(*args, **kwargs):
        def run_function():
            return function(*args, **kwargs)
        self = args[0]
        return await self.client.loop.run_in_executor(None, run_function)
    return __decorator
class ArgParse():
    STRING_ARG = r"(\S)"
    INT_ARG = r"(\d+)"
    URL_PREFIX = r"(http[s]?:\/\/(www\.)?"
    @staticmethod
    def _construct_regex(prefix, command, args):
        args = "\s".join(args)
        regex = f"{prefix}\s{command}\s{args}"
        return regex