import requests
from bs4 import BeautifulSoup
import json
import time


def US(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    headers = {
        'user-agent': user_agent
    }
    html = requests.get('', headers=headers, proxies=proxy)
    soup = BeautifulSoup(html.text, 'html.parser')
    # Do parsing
    #return data

def UK(ITEMS, user_agent, proxy, KEYWORDS, start):
    url = 'https://www.footlocker.co.uk/api/products/search?query=men&currentPage=1&sort=newArrivals&pageSize=60'
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-api-lang': 'en-GB'
    }
    html = requests.get(url=url, headers=headers, proxies=proxy)
    output = json.loads(html.text)['products']
    to_discord = []
    
    for product in output:
        try:
            sku = product['sku']
            url = f'https://www.footlocker.co.uk/api/products/pdp/{sku}'
            html = requests.get(url=url, headers=headers)
            item = json.loads(html.text)
            time.sleep(0.1)

            # Sizes
            sizes = ''
            sizes_start = 1
            for size in item['sellableUnits']:
                store = [size['sku'], size['barcode'], size['code']]
                if size['stockLevelStatus'] == 'inStock' and store not in ITEMS:
                    ITEMS.append(store)
                    if sizes_start == 1:
                        sizes = ''
                        sizes_start = 0
                    else:
                        sizes += '\n' + ''

                elif size['stockLevelStatus'] != 'inStock' and store in ITEMS:
                    # delete from ITEMS
                    ITEMS.remove(store)


            if start == 0 and sizes != '':
                if KEYWORDS is None:
                    to_discord.append(dict(
                        name=item['name'],
                        sku=product['sku'],
                        price=product['price']['formattedValue'],
                        thumbnail=product['images'][0]['url'],
                        url='https://www.footlocker.co.uk/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                    ))
                else:
                    for key in KEYWORDS:
                        if key in item['name']:
                            to_discord.append(dict(
                                name=item['name'],
                                sku=product['sku'],
                                price=product['price']['formattedValue'],
                                thumbnail=product['images'][0]['url'],
                                url='https://www.footlocker.co.uk/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                            ))

        except:
            pass

    return to_discord
