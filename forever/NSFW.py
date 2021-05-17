import random
import asyncio
import json
import xml.etree.ElementTree as ET

from models.EmbedTemplate import EmbedTemplate
from forever import Utilities
cache = {}
async def booruAPI(keywords, url, api):

    if api not in cache or keywords not in cache.get(api):
        params = add_params(keywords, False)
        response = await Utilities.fetchURL(url, params)
        if response:
            posts = ET.fromstring(response)
            posts = [{"img" : el.attrib.get('file_url'), "tags" : el.attrib.get('tags')[:120]+"..."} for el in posts.findall('.//post')]
            if api not in cache:
                cache[api] = {}
                cache[api][keywords] = posts
            else:
                if keywords not in cache:
                    cache[keywords] = posts
    try:
        post = random.choice(cache[api][keywords])
        return construct_embed(post['img'], post['tags'], keywords)
    except IndexError:
        return EmbedTemplate(title='No results!', description='No results for keywords found')
async def rule34XXX(keywords):
    return await booruAPI(keywords, 'https://rule34.xxx/index.php', 'rule34')
async def realbooru(keywords):
    return await booruAPI(keywords, 'https://realbooru.com/index.php', 'realbooru')
async def safebooru(keywords):
    return await booruAPI(keywords, 'https://safebooru.org/index.php', 'safebooru')
async def gelbooru(keywords):
    return await booruAPI(keywords, 'https://gelbooru.com/index.php', 'gelbooru')
async def danbooru(keywords):
    if 'danbooru' not in cache or keywords not in cache.get('danbooru'):
        params = add_params(keywords, True)
        response = await Utilities.fetchURL('https://danbooru.donmai.us/posts.json', params)
        if response:
            posts = json.loads(response)
            if 'danbooru' not in cache:
                cache['danbooru'] = {}
                cache['danbooru'][keywords] = posts
            else:
                if keywords not in cache['danbooru']:
                    cache['danbooru'][keywords] = posts
    try:
        post = random.choice(cache['danbooru'][keywords])
        post = {'img' : post['file_url'], 'tags' : post['tag_string'][:120]+"..."}
        return construct_embed(post['img'], post['tags'], keywords)
    except IndexError:
        return EmbedTemplate(title='No results!', description='No results for keywords found')
def add_params(keywords, danbooru=False):
    if ' ' in keywords:
        keywords = keywords.split(" ")
        keywords.append("-furry")
    params = {
        'limit': 250,
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
    


