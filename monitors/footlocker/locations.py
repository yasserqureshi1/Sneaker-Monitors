import requests
import json
import time


def US(ITEMS, user_agent, proxy, KEYWORDS, start):
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-fl-request-id': '7ea428d0-facd-11ec-8b70-b16510ce7958',
        'user-agent': user_agent
    }
    url = 'https://www.footlocker.com/api/products/search?query=men&currentPage=1&sort=newArrivals&pageSize=60'
    html = requests.get(url=url, headers=headers, proxies=proxy)

    try:
        output = json.loads(html.text)['products']
    except:
        print('Could not load products. Below was the response: ')
        print(html.text)
        return None

    to_discord = []
    
    for product in output:
        try:
            sku = product['sku']
            url = f'https://www.footlocker.com/api/products/pdp/{sku}'
            html = requests.get(url=url, headers=headers)
            item = json.loads(html.text)
            
            time.sleep(1)

            # Sizes
            sizes = ''
            sizes_start = 1
            for size in item['sellableUnits']:
                store = [size['sku'], size['code']]
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
                if KEYWORDS is []:
                    to_discord.append(dict(
                        name=item['name'],
                        sku=product['sku'],
                        price=product['price']['formattedValue'],
                        thumbnail=product['images'][0]['url'],
                        url='https://www.footlocker.com/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                    ))
                else:
                    for key in KEYWORDS:
                        if key.lower() in item['name'].lower():
                            to_discord.append(dict(
                                name=item['name'],
                                sku=product['sku'],
                                price=product['price']['formattedValue'],
                                thumbnail=product['images'][0]['url'],
                                url='https://www.footlocker.com/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                            ))

        except:
            pass

    return to_discord


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
    try:
        output = json.loads(html.text)['products']
    except:
        print('Could not load products. Below was the response: ')
        print(html.text)
        return None

    to_discord = []
    
    for product in output:
        try:
            sku = product['sku']
            url = f'https://www.footlocker.co.uk/api/products/pdp/{sku}'
            html = requests.get(url=url, headers=headers)
            item = json.loads(html.text)
            time.sleep(1)

            # Sizes
            sizes = ''
            sizes_start = 1
            for size in item['sellableUnits']:
                store = [size['sku'], size['code']]
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
                if KEYWORDS is []:
                    to_discord.append(dict(
                        name=item['name'],
                        sku=product['sku'],
                        price=product['price']['formattedValue'],
                        thumbnail=product['images'][0]['url'],
                        url='https://www.footlocker.co.uk/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                    ))
                
                else:
                    for key in KEYWORDS:
                        if key.lower() in item['name'].lower():
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


def AU(ITEMS, user_agent, proxy, KEYWORDS, start):
    url = 'https://www.footlocker.com.au/api/products/search?query=men&currentPage=1&sort=newArrivals&pageSize=60'
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-api-lang': 'en-GB',
        'x-fl-request-id': '1470ff80-fae4-11ec-8f44-7b3338a6657b',
        'x-flapi-session-id': 'th0pgu3oo28l13bhvwqj5yq3i.fzcxwefapipdb828881'
    }
    html = requests.get(url=url, headers=headers, proxies=proxy)
    
    try:
        output = json.loads(html.text)['products']
    except:
        print('Could not load products. Below was the response: ')
        print(html.text)
        return None

    to_discord = []
    
    for product in output:
        try:
            sku = product['sku']
            url = f'https://www.footlocker.com.au/api/products/pdp/{sku}'
            html = requests.get(url=url, headers=headers)
            item = json.loads(html.text)
            time.sleep(1)

            # Sizes
            sizes = ''
            sizes_start = 1
            for size in item['sellableUnits']:
                store = [size['sku'], size['code']]
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
                if KEYWORDS is []:
                    to_discord.append(dict(
                        name=item['name'],
                        sku=product['sku'],
                        price=product['price']['formattedValue'],
                        thumbnail=product['images'][0]['url'],
                        url='https://www.footlocker.com.au/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                    ))
                else:
                    for key in KEYWORDS:
                        if key.lower() in item['name'].lower():
                            to_discord.append(dict(
                                name=item['name'],
                                sku=product['sku'],
                                price=product['price']['formattedValue'],
                                thumbnail=product['images'][0]['url'],
                                url='https://www.footlocker.com.au/product/'+product['name'].replace(' ', '-')+'/'+product['sku'] + '.html'
                            ))

        except:
            pass

    return to_discord