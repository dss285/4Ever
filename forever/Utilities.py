import pytz
import aiohttp
import time
from datetime import datetime
class Utilities:
    def utc2local(timestamp):
        local_tz = pytz.timezone("Europe/Helsinki")
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(local_tz)
    def ts2string(timestamp, pattern='%d.%m.%Y %H:%M:%S | %Z%z'):
        return Utilities.utc2local(timestamp).strftime(pattern)
    async def fetchURL(url, params={}):
        async with aiohttp.ClientSession() as client:
            async with client.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    return None
    def ts2ifmodifiedsince(timestamp):
        return time.strftime("%a, %d %b %Y %H:%M%S GMT", time.gmtime(timestamp)) 
