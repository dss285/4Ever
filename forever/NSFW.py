import random
import asyncio
import json
import xml.etree.ElementTree as ET

from forever.Utilities import Utilities

class NSFW():
    async def rule34XXX(string):
        if ' ' in string:
            string = string.split(" ")
            string.append("-furry")
        params = {
            'limit' : 100,
            'tags' : string,
            'q' : 'index',
            's' : 'post',
            'page' : 'dapi'

        }
        response = await Utilities.fetchURL('https://rule34.xxx/index.php', params)
        if response:
            posts = ET.fromstring(response)
            posts = [{"img" : el.attrib.get('file_url'), "tags" : el.attrib.get('tags')[:120]+"..."} for el in posts.findall('.//post')]
            return random.choice(posts)
    async def realbooru(string):
        if ' ' in string:
            string = string.split(" ")
            string.append("-furry")
        params = {
            'limit' : 100,
            'tags' : string,
            'q' : 'index',
            's' : 'post',
            'page' : 'dapi'

        }
        response = await Utilities.fetchURL('https://realbooru.com/index.php', params)
        if response:
            posts = ET.fromstring(response)
            posts = [{"img" : el.attrib.get('file_url'), "tags" : el.attrib.get('tags')[:120]+"..."} for el in posts.findall('.//post')]
            return random.choice(posts)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(NSFW.rule34XXX('bondage'))
    


