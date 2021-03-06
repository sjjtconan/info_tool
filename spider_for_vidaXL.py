import requests
import time
import re
from bs4 import BeautifulSoup
from openpyxl import Workbook
import numpy as np
from multiprocessing import Pool
import pymongo
import os

# 连接数据库
client = pymongo.MongoClient('localhost', 27017)
vidaXL = client['vidaXL']
sheet_info = vidaXL['sheet_info']



hds = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}

def get_info_links(Homepage):
    req = requests.get(Homepage, headers=hds)
    soup = BeautifulSoup(req.text, 'lxml')
    links = [x.get('href') for x in soup.select('#products-content > div.amshopby-page-container > div.items > div > a')]
    return links

    
def get_info(info_url):
    req = requests.get(info_url, headers=hds)
    time.sleep(np.random.rand()*5)
    soup = BeautifulSoup(req.text, 'lxml')
    img_urls = [x.get('href') for x in soup.select('a.cloud-zoom-gallery')]
    title = soup.select('#right-container > div > h1')[0].get_text().strip()
    price = soup.select('div.special-price span')[0].get_text().strip()
    title_h2_s = soup.select('#product-view > div.padding-container > div > div.product-specifications-box > h2')[0].get_text().strip()
    content1 = [x.get_text().strip() for x in soup.select('#product-view > div.padding-container > div > div.product-specifications-box > div > ul > li')]
    title_h2_d = soup.select('#product-view > div.padding-container > div > div.product-description-box > h2')[0].get_text().strip()
    content2 = [x.get_text().strip() for x in soup.select('#product-view > div.padding-container > div > div.product-description-box > div > p')]
    content = title_h2_s + '\n' + '\n'.join(content1) + '\n'*2 + title_h2_d + '\n' + '\n'.join(content2)
    sku = get_sku(content1)
    data = {
        'title': title,
        'price': price,
        'content': content,
        'sku': sku,
        'img_urls': img_urls
    }
    print({
        'title': title,
        'price': price,
        'sku': sku
    })
    sheet_info.insert_one(data)
    

    
def get_sku(content):
    for i in content:
        if 'SKU' in i:
            sku = i.split()[-1]
            return sku
        else:
            pass

def get_img(info_url):
    req = requests.get(info_url, headers=hds)
    soup = BeautifulSoup(req.text, 'lxml')
    img_urls = [x.get('href') for x in soup.select('a.cloud-zoom-gallery')]
    content1 = [x.get_text().strip() for x in soup.select('#product-view > div.padding-container > div > div.product-specifications-box > div > ul > li')]
    sku = get_sku(content1)
    path1 = r'D:/photo1/{}-FR'.format(sku)
    try:
        os.makedirs(path1)
    except:
        print('文件已存在')
    for i, img_url in enumerate(img_urls):
        req = requests.get(img_url, headers=hds)
        time.sleep(np.random.rand()*5)
        path2 = path1 + r'/0 ({}).jpg'.format(i+1)
        with open(path2, 'wb') as f:
            f.write(req.content)
        #print('已下载%d张' % (i+1))
    print('图片OK')

        
    
    
def do_spider_excel(info_list):
    wb = Workbook()
    ws = wb.active
    ws.append(['sku', '产品英文名', '价格', '产品描述'])
    for i in info_list:
        ws.append([i['sku'], i['title'], i['price'], i['content']])
    wb.save('product_info.xlsx')

do_spider_excel(sheet_info.find())   #导出excel
  


# 下载产品信息

# if __name__ == '__main__':
#     homepage = 'https://www.vidaxl.fr/g/502973/panneaux-de-cloture?attributes%5B0%5D=cms_brand_90%7CvidaXL&p=2'
#     links = get_info_links(homepage)
#     pool = Pool()
#     pool.map(get_info, links)



# 多主页下载产品信息
# if __name__ == '__main__':
#     for i in range(1,100):
#         homepage = ''
#


# 下载图片

# if __name__ == '__main__':
#     homepage = 'https://www.vidaxl.fr/g/6362/meubles-de-bureau'
#     links = get_info_links(homepage)
#     pool = Pool()
#     pool.map(get_img, links)
