import random
import asyncio
import json
import xml.etree.ElementTree as ET

from models.EmbedTemplate import EmbedTemplate
from forever import Utilities

async def booruAPI(keywords, url):
    params = add_params(keywords, False)
    response = await Utilities.fetchURL(url, params)
    if response:
        posts = ET.fromstring(response)
        posts = [{"img" : el.attrib.get('file_url'), "tags" : el.attrib.get('tags')[:120]+"..."} for el in posts.findall('.//post')]
        try:
            post = random.choice(posts)
            return construct_embed(post['img'], post['tags'], keywords)
        except IndexError:
            return EmbedTemplate(title='No results!', description='No results for keywords found')
async def rule34XXX(keywords):
    return await booruAPI(keywords, 'https://rule34.xxx/index.php')
async def realbooru(keywords):
    return await booruAPI(keywords, 'https://realbooru.com/index.php')
async def safebooru(keywords):
    return await booruAPI(keywords, 'https://safebooru.org/index.php')
async def gelbooru(keywords):
    return await booruAPI(keywords, 'https://gelbooru.com/index.php')
async def danbooru(keywords):
    params = add_params(keywords, True)
    response = await Utilities.fetchURL('https://danbooru.donmai.us/posts.json', params)
    if response:
        posts = json.loads(response)
        try:
            post = random.choice(posts)
            post = {'img' : post['file_url'], 'tags' : post['tag_string'][:120]+"..."}
            return construct_embed(post['img'], post['tags'], keywords)
        except IndexError:
            return EmbedTemplate(title='No results!', description='No results for keywords found')
def add_params(keywords, danbooru=False):
    if ' ' in keywords:
        keywords = keywords.split(" ")
        keywords.append("-furry")
    params = {
        'limit': 50,
        'tags' : keywords,
    }
    if not danbooru:
        params['s'] = 'post',
        params['q'] = 'index',
        params['page'] = 'dapi'
    return params
def construct_embed(image_url, tags, title):
    em = EmbedTemplate(title=title, description=tags.replace("*", ""))
    em.set_image(url=image_url)
    return em
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(danbooru('girls_frontline')))
    


