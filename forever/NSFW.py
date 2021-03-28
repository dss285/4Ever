import random
import asyncio
import json
import xml.etree.ElementTree as ET

from forever import Utilities
async def booruAPI(keywords, url):
    if ' ' in keywords:
        keywords = keywords.split(" ")
        keywords.append("-furry")
    params = {
        'limit' : 100,
        'tags' : keywords,
        'q' : 'index',
        's' : 'post',
        'page' : 'dapi'
    }
    response = await Utilities.fetchURL(url, params)
    if response:
        posts = ET.fromstring(response)
        posts = [{"img" : el.attrib.get('file_url'), "tags" : el.attrib.get('tags')[:120]+"..."} for el in posts.findall('.//post')]
        return random.choice(posts)
async def rule34XXX(keywords):
    return await booruAPI(keywords, 'https://rule34.xxx/index.php')
async def realbooru(keywords):
    return await booruAPI(keywords, 'https://realbooru.com/index.php')
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rule34XXX('bondage'))
    


