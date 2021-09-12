from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import requests as rq
import urllib3

from datetime import datetime
import time

import json
import logging
import dotenv
import traceback

logging.basicConfig(filename='SNKRSlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

INSTOCK = []


def scrape_site(headers, proxy):
    """
    Scrapes SNKRS site and adds items to array
    """
    items = []

    # Makes request to site
    anchor = 0
    while anchor < 180:
        headers = {"user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"}
        url = f'https://api.nike.com/product_feed/threads/v2/?anchor={anchor}&count=60&filter=marketplace%28{CONFIG["LOC"]}%29&filter=language%28{CONFIG["LAN"]}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'
        html = rq.get(url=url, timeout=20, verify=False, headers=headers, proxies=proxy)
        output = json.loads(html.text)

        # Stores details in array
        for item in output['objects']:
            items.append(item)

        anchor += 60
        print(f'Anchor {anchor}')
    
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
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these montiors!",
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

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
        'username': CONFIG['USERNAME'],
        'avatar_url':  CONFIG['AVATAR_URL'],
        'embeds': [{
            'title': title,
            'description': description,
            'url': url,
            'thumbnail': {'url': thumbnail},
            'color': int(CONFIG['COLOUR']),
            'footer': {'text': 'Made by Yasser'},
            'timestamp': str(datetime.utcnow()),
            'fields': [
                {'name': 'Price', 'value': price},
                {'name': 'Style Code', 'value': style_code},
                {'name': 'Sizes', 'value': sizes}
            ]
        }]
    }
    
    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

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
    for k in j['availableSkus']:
        item = [j['merchProduct']['labelName'], j['productContent']['colorDescription'], k['id']]
        if k['available'] == True:
            if checker(item):
                pass
            else:
                INSTOCK.append(item)
                
                for s in j['skus']:
                    if first == 0:
                        if s['id'] == k['id']:
                            sizes = str(s['nikeSize']) + ': ' + str(k['level'])
                            first = 1
                            break
                    else:
                        if s['id'] == k['id']:
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
            url='https://www.nike.com/' + CONFIG['LOC'] + '/launch/t/' + j['productContent']['slug'],
            thumbnail=j['imageUrls']['productImageUrl'],
            price=str(j['merchPrice']['currentPrice']),
            style_code=str(j['merchProduct']['styleColor']),
            sizes=sizes)



def monitor():
    """
    Initiates the monitor
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')

    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    proxy_no = 0
    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        # Makes request to site and stores products 
        items = scrape_site(proxy=proxy, headers=headers)
        for item in items:
            try:
                for j in item['productInfo']:
                    if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                        
                        if keywords == "":
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
                headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

                if CONFIG['PROXY'] != "":
                    # If optional proxy set, rotates if there are multiple proxies
                    proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                    proxy = {"http": f"http://{proxy_list[proxy_no]}"}
            
            except Exception as e:
                print(f"Exception found: {traceback.format_exc()}")
                pass

        # Allows changes to be notified
        start = 0

        # User set delay
        time.sleep(float(CONFIG['DELAY']))


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
