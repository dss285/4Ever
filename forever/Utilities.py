from typing import Union
import pytz
import aiohttp
import time
import re
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
session = None
def utc2local(timestamp):
    local_tz = pytz.timezone("Europe/Helsinki")
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(local_tz)
def ts2string(timestamp, pattern='%d.%m.%Y %H:%M:%S | %Z%z'):
    return utc2local(timestamp).strftime(pattern)
async def fetch_url(url, params={}):
    if session:
        async with session.get(url, params=params) as resp:
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
def dict_search(dictionary, searched_key):
    if not isinstance(dictionary, dict):
        raise Exception("Not a dictionary")
    if searched_key in dictionary:
        return searched_key
    results = []
    for i in dictionary:
        if i.lower().startswith(searched_key.lower()):
            results.append(i)
    if results and len(results) == 1:
        return results[0]
    return results
    
def log(messages, file="log.txt"):
    if isinstance(messages, str):
        messages = [messages]
    fo = open("log.txt", "a+")
    for i in messages:
        print(i, "\n")
        fo.write(f"{i}\n")
    fo.close()
def run_in_executor(function):
    async def __decorator(*args, **kwargs):
        def run_function():
            return function(*args, **kwargs)
        self = args[0]
        return await self.client.loop.run_in_executor(None, run_function)
    return __decorator
class Args():
    #?P<first_name>
    ANY_ARG = "(?P<{}>.+)"
    STRING_ARG = "(?P<{}>\S+)"
    INT_ARG = "(?P<{}>\d+)"
    MENTION_ARG = "(?P<{}><@[!|&]?(?:\d+)>)"
    CHANNEL_MENTION_ARG = "(?P<{}>\<\#?\d+\>)"
    OPTIONAL_STRING_ARG = "?(?P<{}>\S+)?"
    OPTIONAL_INT_ARG = "?(?P<{}>\d+)?"
    URL_PREFIX = "(http[s]?:\/\/(www\.)?"

    def __init__(self, *args, **kwargs) -> None:
        self.names = []
        self.args = []
        for name, arg in kwargs.items():
            self.names.append(name)
            self.args.append(arg.format(name))
        self.pattern = None
    def set_pattern(self, prefix, aliases) -> None:
        self.pattern = self.construct_regex(prefix, aliases)
    def construct_regex(self, prefix: str, aliases: list) -> str:
        prefix = re.escape(prefix)
        aliases = f"(?P<command>{'|'.join(aliases)})"
        args = r"\s".join(self.args)
        regex = f"{prefix}\s{aliases}\s{args}"
        return regex
    def parse(self, content: str) -> Union[dict, None]:
        reg = re.match(self.pattern, content)
        if reg:
            return reg.groupdict()
        else:
            return None
if __name__ == "__main__":
    custom = "(?:(?P<{}>\d+)|(?:https:\/\/steamcommunity\.com\/(?:profiles\/(?P<steamid>\d+)|id\/(?P<profile>.+))))"
    ar = Args(steam=custom)
    ar.set_pattern("$gfl", ["doll", "d"])
    print(ar.pattern)
    print(ar.parse("$gfl doll 213213123"))
    print(ar.parse("$gfl doll https://steamcommunity.com/id/dss285-aeon/"))
    print(ar.parse("$gfl doll https://steamcommunity.com/profiles/21312312122"))