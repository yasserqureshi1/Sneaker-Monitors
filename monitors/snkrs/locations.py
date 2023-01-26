# For regions that do not use the standard API
from bs4 import BeautifulSoup
import requests
import json
import traceback

import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

___standard_api___ = [
    'GB', 'US', 'AU', 'AT', 'BE', 'BG', 'CA', 'CN', 'HR', 'CZ', 'DK', 'EG', 
    'FI', 'FR', 'DE', 'HU', 'IN', 'ID', 'IE', 'IT', 'MY', 'MX', 'MA', 'NL', 
    'NZ', 'NO', 'PH', 'PL', 'PT', 'PR', 'RO', 'RU', 'SA', 'SG', 'SI', 'ZA', 
    'ES', 'SE', 'CH', 'TR', 'AE', 'VN', 'JP' 
]


async def get_content(url, user_agent, proxy):
    browser = await launch()
    page = await browser.newPage()
    await stealth(page)
    await page.emulate({
        'userAgent': user_agent,
        'viewport': {
            'width': 414,
            'height': 736,
            'deviceScaleFactor': 3,
            'isMobile': True,
            'hasTouch': True,
            'isLandscape': False
        }
    })
    await page.goto(url)
    content = await page.content()
    await page.close()
    return content


def standard_api(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9',
        'appid': 'com.nike.commerce.snkrs.web',
        'content-type': 'application/json; charset=UTF-8',
        'dnt': '1',
        'nike-api-caller-id': 'nike:snkrs:web:1.0',
        'origin': 'https://www.nike.com',
        'referer': 'https://www.nike.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    to_discord = []

    anchor = 0
    while anchor < 160:
        url = f'https://api.nike.com/product_feed/threads/v3/?anchor={anchor}&count=50&filter=marketplace%28{LOCATION}%29&filter=language%28{LANGUAGE}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29'
        html = requests.get(url=url, timeout=20, verify=False, headers=headers, proxies=proxy)
        output = json.loads(html.text)

        # Stores details in array
        for item in output['objects']:
            try:
                for product in item['productInfo']:
                    if (product['availability']['available'] == True) and (product['merchProduct']['status'] == 'ACTIVE'):
                        if KEYWORDS == []:
                            first = 0
                            sizes = ''
                            for k in product['availableGtins']:
                                stored = [product['productContent']['fullTitle'], product['productContent']['colorDescription'], k['gtin']]
                                if k['available'] == True:
                                    if stored in ITEMS:
                                        pass
                                    else:
                                        ITEMS.append(stored)
                                        
                                        for s in product['skus']:
                                            if first == 0:
                                                if s['gtin'] == k['gtin']:
                                                    sizes = str(s['nikeSize']) + ': ' + str(k['level'])
                                                    first = 1
                                                    break
                                            else:
                                                if s['gtin'] == k['gtin']:
                                                    sizes += '\n' + str(s['nikeSize']) + ': ' + str(k['level'])
                                                    break
                                else:
                                    if stored in ITEMS:
                                        ITEMS.remove(stored)
                            
                            if sizes != '' and start == 0:
                                print('Sending notification to Discord...')
                                to_discord.append(dict(
                                    title=product['productContent']['fullTitle'],
                                    description=product['productContent']['colorDescription'],
                                    url='https://www.nike.com/' + LOCATION + '/launch/t/' + product['productContent']['slug'],
                                    thumbnail=item['publishedContent']['nodes'][0]['nodes'][0]['properties']['squarishURL'],
                                    price=str(product['merchPrice']['currentPrice']),
                                    style_code=str(product['merchProduct']['styleColor']),
                                    sizes=sizes))

                        else:
                            for key in KEYWORDS:
                                if key.lower() in product['merchProduct']['labelName'].lower() or key.lower() in product['productContent']['colorDescription'].lower():
                                    first = 0
                                    sizes = ''
                                    for k in product['availableGtins']:
                                        stored = [product['productContent']['fullTitle'], product['productContent']['colorDescription'], k['gtin']]
                                        if k['available'] == True:
                                            if stored in ITEMS:
                                                pass
                                            else:
                                                ITEMS.append(stored)
                                                
                                                for s in product['skus']:
                                                    if first == 0:
                                                        if s['gtin'] == k['gtin']:
                                                            sizes = str(s['nikeSize']) + ': ' + str(k['level'])
                                                            first = 1
                                                            break
                                                    else:
                                                        if s['gtin'] == k['gtin']:
                                                            sizes += '\n' + str(s['nikeSize']) + ': ' + str(k['level'])
                                                            break
                                        else:
                                            if stored in ITEMS:
                                                ITEMS.remove(stored)
                                    
                                    if sizes != '' and start == 0:
                                        print('Sending notification to Discord...')
                                        to_discord.append(dict(
                                            title=product['productContent']['fullTitle'],
                                            description=product['productContent']['colorDescription'],
                                            url='https://www.nike.com/' + LOCATION + '/launch/t/' + product['productContent']['slug'],
                                            thumbnail=item['publishedContent']['nodes'][0]['nodes'][0]['properties']['squarishURL'],
                                            price=str(product['merchPrice']['currentPrice']),
                                            style_code=str(product['merchProduct']['styleColor']),
                                            sizes=sizes))
            except KeyError:
                pass

            except:
                print(traceback.format_exc())

        anchor += 50
        
    return to_discord

    
def brazil(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    # need to bs4 
    url = 'https://www.nike.com.br/Snkrs/Feed?p=2&demanda=true'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    to_discord = []
    html = requests.get(url=url, headers=headers, proxies=proxy)
    soup = BeautifulSoup(html.text, 'html.parser')
    output = soup.find_all('div', {'class': 'produto produto--esgotado'})
    for product in output:
        if KEYWORDS == []:
            item = dict(
                title=product.find('h2', {'class': 'produto__detalhe-titulo'}).text,
                description=None,
                url=product.find('div', {'class': 'produto__imagem'})['href'],
                thumbnail=product.find('div', {'class': 'produto__imagem'})['src'],
                price=None,
                style_code=None,
                sizes=None
            )

            if item in ITEMS:
                pass
            elif start == 0:
                to_discord.append(item)
                start = 1
        
        else:
            for key in KEYWORDS:
                if key.lower() in product.find('h2', {'class': 'produto__detalhe-titulo'}).text.lower():
                    item = dict(
                        title=product.find('h2', {'class': 'produto__detalhe-titulo'}).text,
                        description=None,
                        url=product.find('div', {'class': 'produto__imagem'})['href'],
                        thumbnail=product.find('div', {'class': 'produto__imagem'})['src'],
                        price=None,
                        style_code=None,
                        sizes=None
                    )

                    if item in ITEMS:
                        pass
                    elif start == 0:
                        to_discord.append(item)
                        start = 1

    return to_discord



def chile(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    url = 'https://www.nike.cl/api/catalog_system/pub/products/search?&_from=0&_to=49'
    to_discord = []
    html = asyncio.get_event_loop().run_until_complete(get_content(url, user_agent, proxy))
    html = html.replace('</pre></body></html>','').replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">','')
    html = '{"data": ' + html + '}'

    output = json.loads(html)

    # For each product
    for product in output['data']:
        # For each size
        sizes = ''
        s = 0
        for size in product['items']:
            item = [product['productName'], product['productReferenceCode'], size['name']]
            if int(size['sellers'][0]['commertialOffer']['AvailableQuantity']) > 0:
                if item not in ITEMS:
                    ITEMS.append(item)
                    if s == 0:
                        sizes = str(size['name']) + ': [' + str(size['sellers'][0]['commertialOffer']['AvailableQuantity']) + ' Available' +  f']({size["sellers"][0]["addToCartLink"]})'
                        s = 1
                    else:
                        sizes += '\n' + str(size['name']) + ': [' + str(size['sellers'][0]['commertialOffer']['AvailableQuantity']) + ' Available' + f']({size["sellers"][0]["addToCartLink"]})'
            
            else:
                if item in ITEMS:
                    ITEMS.remove(item)
        
        if sizes != '' and start == 0:
            if KEYWORDS == []:
                to_discord.append(dict(
                    title=product['productName'],
                    description=str(product['items'][0]['color'][0]),
                    url=product['link'],
                    thumbnail=str(int(product['items'][0]['images'][0]['imageUrl'])/1000),
                    price=str(product['items'][0]['sellers'][0]['commertialOffer']['Price']),
                    style_code=str(product['productReferenceCode']),
                    sizes=sizes))

            else:
                for key in KEYWORDS:
                    if key.lower() in product['productName'].lower():
                        to_discord.append(dict(
                            title=product['productName'],
                            description=str(product['items'][0]['color'][0]),
                            url=product['link'],
                            thumbnail=str(int(product['items'][0]['images'][0]['imageUrl'])/1000),
                            price=str(product['items'][0]['sellers'][0]['commertialOffer']['Price']),
                            style_code=str(product['productReferenceCode']),
                            sizes=sizes))
    return to_discord

