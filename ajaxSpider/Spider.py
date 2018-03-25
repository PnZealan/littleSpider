#coding:utf-8
import json
import os

import requests
import re
from bs4 import BeautifulSoup
import pymongo
from config import *
from multiprocessing import Pool
from hashlib import md5


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
}


client = pymongo.MongoClient(MONGO_URL)
db = client.db[MONGO_DB]


def get_page_index(url, data):
    try:
        rep = requests.get(url, params=data, headers=headers)
        result = json.loads(rep.text)
        if result and 'data' in result.keys():
            for item in result.get('data'):
                yield item
        else:
            return None
    except:
        return None


def parse_page_index(content):
    for item in content:
        #print(item.get('article_url'))
        yield item.get('article_url')


def save_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('insert mongo successfully, {}'.format(result.get('title')))


def get_page_detail(url):
    try:
        #print(url)
        #rep = requests.get('https://www.toutiao.com/a6577026548690321928/')
        rep = requests.get(url=url, headers=headers)
        #print(rep.text)
        return rep.text
    except Exception as e:
        print(e)
        return None
    #ret = re.search(pattern, rep.text)
    #print(ret)


def parse_page_detail(html, pattern, url):
    try:
        if html:
            result = re.search(pattern, html)
            if result:
                title = BeautifulSoup(html, 'html.parser').select('title')[0].get_text()
                data = json.loads(result.group(1).replace('\\', ''))
                sub_images = data.get('sub_images')
                images = [item.get('url') for item in sub_images]
                return {
                    'title': title,
                    'url': url,
                    'images': images
                }
    except:
        return None


def save_images(content):
    base_path = os.path.join(os.getcwd(), 'picture')
    base_dir_path = os.path.join(base_path, content.get('title'))
    if not os.path.exists(base_dir_path):
        os.mkdir(base_dir_path)
    for item in content.get('images'):
        content = requests.get(item, headers=headers).content
        filename = str(md5(content).hexdigest()) + '.jpg'
        filepath = os.path.join(base_dir_path, filename)
        with open(filepath, 'wb') as f:
            f.write(content)


def main(offset):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': KEYWORD,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/'
    regex = 'gallery: JSON.parse\("(.*?)"\)'
    pattern = re.compile(regex, re.S)
    page_index = get_page_index(url, data)
    if page_index:
        urls = parse_page_index(page_index)
        for url in urls:
            html = get_page_detail(url)
            result = parse_page_detail(html, pattern, url)
            if result:
                save_mongo(result)
                save_images(result)


if __name__ == '__main__':
    p = Pool(5)
    OFFSET = ([x * 20 for x in range(START, END + 1)])
    p.map(main, OFFSET)
    p.close()
    p.join()

