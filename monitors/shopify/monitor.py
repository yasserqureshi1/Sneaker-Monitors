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

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR, URL

logging.basicConfig(filename='shopify-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []


def check_url(url):
    """
    Checks whether the supplied URL is valid
    """
    return 'products.json' in url


def scrape_site(url, headers, proxy):
    """
    Scrapes the specified Shopify site and adds items to array
    """
    items = []

    # Makes request to site
    s = rq.Session()
    page = 1
    while True:
        html = s.get(url + f'?page={page}&limit=250', headers=headers, proxies=proxy, verify=False, timeout=20)
        output = json.loads(html.text)['products']
        if output == []:
            break
        else:
            # Stores particular details in array
            for product in output:
                try:
                    product_item = {
                        'title': product['title'], 
                        'image': product['images'][0]['src'], 
                        'handle': product['handle'],
                        'variants': product['variants']}
                except:
                    product_item = {
                        'title': product['title'], 
                        'image': None, 
                        'handle': product['handle'],
                        'variants': product['variants']}
                items.append(product_item)
            page += 1
    
    logging.info(msg='Successfully scraped site')
    s.close()
    return items


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def discord_webhook(title, url, thumbnail, sizes):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    fields = []
    for size in sizes:
        fields.append({"name": size['title'], "value": size['url'], "inline": True})

    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": URL.replace('.json', '/') + url, 
            "thumbnail": {"url": thumbnail},
            "fields": fields,
            "color": int(COLOUR),
            "footer": {"text": "Developed by GitHub:yasserqureshi1"},
            "timestamp": str(datetime.utcnow()),
        }]
    }

    result = rq.post(WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return list(set(mylist))


def comparitor(product, start):
    product_item = [product['title'], product['image'], product['handle']]
    # Collect all available sizes
    available_sizes = []
    for size in product['variants']:
        if size['available']: # Makes an ATC link from the variant ID
            available_sizes.append({'title': size['title'], 'url': '[ATC](' + URL[:URL.find('/', 10)] + '/cart/' + str(size['id']) + ':1)'})

    
    product_item.append(available_sizes) # Appends in field
    
    if available_sizes:
        if not checker(product_item):
            # If product is available but not stored - sends notification and stores
            
            INSTOCK.append(product_item)
            
            if start == 0:
                print(product_item)
                discord_webhook(
                    title=product['title'],
                    url=product['handle'],
                    thumbnail=product['image'],
                    sizes=available_sizes
                )
                logging.info(msg='Successfully sent Discord notification')

    else:
        if checker(product_item):
            # If product is not available but stored - removes from store
            INSTOCK.remove(product_item)


def monitor():
    """
    Initiates the monitor
    """
    print('''\n-----------------------------------
--- SHOPIFY MONITOR HAS STARTED ---
-----------------------------------\n''')
    logging.info(msg='Successfully started monitor')

    # Checks URL
    if not check_url(URL):
        print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
        logging.error(msg='Store URL formatting incorrect for: ' + str(URL))
        return

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    if ENABLE_FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    elif PROXY != []:
        proxy_no = 0
        proxy = {} if PROXY == [] else {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}
    else:
        proxy = {}

    headers = {
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

    while True:
        try:
            # Makes request to site and stores products 
            items = scrape_site(URL, proxy, headers)
            for product in items:

                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(product, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if key.lower() in product['title'].lower():
                            comparitor(product, start)

            # Allows changes to be notified
            start = 0

        except rq.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            headers['User-Agent'] = user_agent_rotator.get_random_user_agent()
            
            if ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif PROXY != []:
                proxy_no = 0 if proxy_no == (len(PROXY)-1) else proxy_no + 1
                proxy = {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)   
        
        # User set delay
        time.sleep(float(DELAY))


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()