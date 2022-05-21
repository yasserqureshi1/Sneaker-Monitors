from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import requests as rq
import urllib3
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback

import config

logging.basicConfig(filename='SNKRS.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

proxy_obj = FreeProxy(country_id=[config.FREE_PROXY_LOCATION], rand=True)

INSTOCK = []


def scrape_site(headers, proxy):
    """
    Scrapes SNKRS site and adds items to array
    """
    items = []

    # Makes request to site
    anchor = 0
    while anchor < 160:
        url = f'https://api.nike.com/product_feed/threads/v3/?anchor={anchor}&count=50&filter=marketplace%28{config.LOCATION}%29&filter=language%28{config.LANGUAGE}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29'
        html = rq.get(url=url, timeout=20, verify=False, headers=headers, proxies=proxy)
        output = json.loads(html.text)

        # Stores details in array
        for item in output['objects']:
            items.append(item)

        anchor += 50
    logging.info(msg='Successfully scraped SNKRS site')
    return items


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def test_webhook():
    '''
    Sends a test Discord webhook notification
    '''
    data = {
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these montiors!",
            "color": int(config.COLOUR),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(title, description, url, thumbnail, price, style_code, sizes):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        'username': config.USERNAME,
        'avatar_url':  config.AVATAR_URL,
        'embeds': [{
            'title': title,
            'description': description,
            'url': url,
            'thumbnail': {'url': thumbnail},
            'color': int(config.COLOUR),
            'footer': {'text': 'Made by Yasser'},
            'timestamp': str(datetime.utcnow()),
            'fields': [
                {'name': 'Price', 'value': price},
                {'name': 'Style Code', 'value': style_code},
                {'name': 'Sizes', 'value': sizes}
            ]
        }]
    }
    
    result = rq.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(j, start):
    first = 0
    sizes = ''
    for k in j['availableGtins']:
        item = [j['productContent']['fullTitle'], j['productContent']['colorDescription'], k['gtin']]
        if k['available'] == True:
            if checker(item):
                pass
            else:
                INSTOCK.append(item)
                
                for s in j['skus']:
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
            if checker(item):
                INSTOCK.remove(item)
    
    if sizes != '' and start == 0:
        print('Sending notification to Discord...')
        discord_webhook(
            title=j['merchProduct']['labelName'],
            description=j['productContent']['colorDescription'],
            url='https://www.nike.com/' + config.LOCATION + '/launch/t/' + j['productContent']['slug'],
            thumbnail=j['imageUrls']['productImageUrl'],
            price=str(j['merchPrice']['currentPrice']),
            style_code=str(j['merchProduct']['styleColor']),
            sizes=sizes)



def monitor():
    """
    Initiates the monitor
    """
    print('''\n---------------------------
--- MONITOR HAS STARTED ---
---------------------------\n''')
    print(''' ** Now you will recieve notifications when an item drops or restocks **
This may take some time so you have to leave this script running. It's best to do this on a server (you can get a free one via AWS)!
    
Check out the docs at https://yasserqureshi1.github.io/Sneaker-Monitors/ for more info.
    
Join the Sneakers & Code family via Discord and subscribe to my YouTube channel https://www.youtube.com/c/YasCode\n\n''')
    logging.info(msg='Successfully started monitor')

    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    if config.ENABLE_FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    else:
        proxy_no = 0
        proxy = {} if config.PROXY == [] else {"http": f"http://{config.PROXY[proxy_no]}"}

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
        'user-agent': user_agent_rotator.get_random_user_agent()
    }

    # Collecting all keywords (if any)
    keywords = config.KEYWORDS
    while True:
        # Makes request to site and stores products 
        items = scrape_site(proxy=proxy, headers=headers)
        for item in items:
            try:
                for j in item['productInfo']:
                    if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                        if keywords == []:
                            # If no keywords set, checks whether item status has changed
                            comparitor(j, start)

                        else:
                            # For each keyword, checks whether particular item status has changed
                            for key in keywords:
                                if key.lower() in j['merchProduct']['labelName'].lower() or key.lower() in j['productContent']['colorDescription'].lower():
                                    comparitor(j, start)

                    else:
                        for item in INSTOCK:
                            if item[0] == j['merchProduct']['labelName'] and item[1] == j['productContent']['colorDescription']:
                                INSTOCK.remove(item)
            
            except KeyError as e:
                pass

            except rq.exceptions.HTTPError as e:
                logging.error(e)

                # Rotates headers
                headers['user-agent'] = user_agent_rotator.get_random_user_agent()
                
                if config.ENABLE_FREE_PROXY:
                    proxy = {'http': proxy_obj.get()}

                elif config.PROXY != []:
                    proxy_no = 0 if proxy_no == (len(config.PROXY)-1) else proxy_no + 1
                    proxy = {"http": f"http://{config.PROXY[proxy_no]}"}

            except Exception as e:
                print(f"Exception found: {traceback.format_exc()}")

        # Allows changes to be notified
        start = 0

        # User set delay
        time.sleep(float(config.DELAY))


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
