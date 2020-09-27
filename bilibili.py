import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import math
import json
import time
import collections
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")

headers ={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9,zh-HK;q=0.8',
'Connection': 'keep-alive',
'Host': 'www.bilibili.com',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}

style_id = {'all': -1,'culture': 19,'history': 25,'technology': 27,'explore': 29,'journey': 31,'nature': 34,'food': 39,'military': 988,'animal': 989,'universe': 1201, 'pet': 1202,'society': 1203,'medical': 1204,'disaster': 1205,'crime': 1205,'mystery': 1205,'sport': 1205 }
producer_id  = {'all': -1,'BBC': 1,'NHK': 2,'SKY': 3,'cctv': 4,'ITV': 5,'history': 6,'discovery': 7,'tv': 8,'homemade': 9,'ZDF': 10,'Cooperation': 11,'domestic': 12,'foreign': 13}
year = {'all' :-1,'2019' :'2009','2018' :'2018','2017' :'2017','2016' :'2016','2015' :'2015','2014-2010' :'2014-2010','2009-2005' :'2009-2005','2004-2000' :'2004-2000','90s' :'90年代','80s' :'80年代','before': '更早'}

def get_url(style_id = style_id['all'],producer_id = -1,year = -1,page = 1 ):
    url = r'https://bangumi.bilibili.com/media/web_api/search/result?style_id={0}&producer_id={1}&year={2}&order=2&st=3&sort=0&page={3}&season_type=5&pagesize=20'.format(style_id ,producer_id,year,page)
    return url


page_num = 0
page_all = 0
drama_frame = []
while (page_num <= page_all):
    r = requests.get(get_url(page=page_num + 1))
    page_num += 1
    drama_dict = eval(r.text)
    drama_data = drama_dict['result']['data']

    if page_all == 0:
        drama_page = drama_dict['result']['page']
        page_all = math.ceil(drama_page['total'] / drama_page['size'])

    for drama in drama_data:
        try:
            drama_frame.append([drama['title'], time.localtime(drama['order']['pub_date']).tm_year, drama['season_id']])
        except:
            pass

drama_table = pd.DataFrame(drama_frame,columns = ['title','years','season_id'])

def get_information(table):
    url = r'https://bangumi.bilibili.com/view/web_api/season?season_id={0}'.format(table['season_id'])
    print(url)
    r = requests.get(url)
    try:
        info = eval(r.text)['result']
        table['danmakus'] = info['stat']['danmakus']
        table['favorites'] = info['stat']['favorites']
        table['views'] = info['stat']['views']
        table['coins'] = info['stat']['coins']
        table['area'] = info['areas'][0]['name']
        table['style'] = info['style']
    except:
        pass
    return table

drama_information = drama_table.apply(get_information, axis = 1)

drama_information['area'] = drama_information['area'].replace('英国','Britain').replace('中国大陆','Mainland China').replace('美国','America').replace('法国','France').replace('日本','Japan').replace('加拿大','Canada').replace('澳大利亚','Australia').replace('德国','German').replace('俄罗斯','Russia').replace('新加坡','Singapore').replace('丹麦','Denmark').replace('西班牙','Spain').replace('中国香港','Hong Kong,China').replace('泰国','Thailand').replace('瑞典','Sweden').replace('中国台湾','Tai Wan,China')

for i in range(len(drama_information['style'])):
    if drama_information['style'][i] is not np.nan:
        drama_information['style'][i] = str(drama_information['style'][i])
        drama_information['style'][i] = drama_information['style'][i].replace('剧情','Plot')
        drama_information['style'][i] = drama_information['style'][i].replace('悬疑','Suspense')
        drama_information['style'][i] = drama_information['style'][i].replace('搞笑','Hilarious')
        drama_information['style'][i] = drama_information['style'][i].replace('青春','Youth')
        drama_information['style'][i] = drama_information['style'][i].replace('奇幻','Fantasy')
        drama_information['style'][i] = drama_information['style'][i].replace('战争','War')
        drama_information['style'][i] = drama_information['style'][i].replace('武侠','Martial')
        drama_information['style'][i] = drama_information['style'][i].replace('都市','City')
        drama_information['style'][i] = drama_information['style'][i].replace('古装','Costume')
        drama_information['style'][i] = drama_information['style'][i].replace('谍战','Spy')
        drama_information['style'][i] = drama_information['style'][i].replace('经典','Classic')
        drama_information['style'][i] = drama_information['style'][i].replace('情感','Emotion')
        drama_information['style'][i] = drama_information['style'][i].replace('励志','Inspirational')
        drama_information['style'][i] = drama_information['style'][i].replace('神话','Myth')
        drama_information['style'][i] = drama_information['style'][i].replace('穿越','Time-travel')
        drama_information['style'][i] = drama_information['style'][i].replace('年代','Old')
        drama_information['style'][i] = drama_information['style'][i].replace('农村','Rural')
        drama_information['style'][i] = drama_information['style'][i].replace('刑侦','Criminal')
        drama_information['style'][i] = drama_information['style'][i].replace('家庭','Family')
        drama_information['style'][i] = drama_information['style'][i].replace('历史','History')
        drama_information['style'][i] = drama_information['style'][i].replace('军旅','Military')

drama_information = drama_information[['title','area','years','style','views','coins','danmakus','favorites','season_id']]
drama_information = drama_information.rename(columns={'favorites':'favourites'})
drama_information.dropna(inplace = True)
drama_information.head()