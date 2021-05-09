from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from fp.fp import FreeProxy

import requests as rq
import urllib3

from datetime import datetime
import time

import json
import logging
import dotenv

logging.basicConfig(filename='Shopifylog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

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
                product_item = {
                    'title': product['title'], 
                    'image': product['images'][0]['src'], 
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


def test_webhook():
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these monitors!",
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))



def discord_webhook(title, url, thumbnail, sizes):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    fields = []
    for size in sizes:
        fields.append({"name": size, "value": "Available", "inline": True})

    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "url": CONFIG['URL'].replace('.json', '/') + url, 
            "thumbnail": {"url": thumbnail},
            "fields": fields,
            "color": int(CONFIG['COLOUR']),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
        }]
    }

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

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
        if size['available']:
            available_sizes.append(size['title'])
    
    product_item.append(available_sizes)
    
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
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')

    # Checks URL
    if not check_url(CONFIG['URL']):
        print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
        logging.error(msg='Store URL formatting incorrect for: ' + str(CONFIG['URL']))
        return

    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    proxy_no = 0
    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": proxyObject.get()} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            # Makes request to site and stores products 
            items = scrape_site(CONFIG['URL'], proxy, headers)
            for product in items:

                if keywords == "":
                    # If no keywords set, checks whether item status has changed
                    comparitor(product, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in keywords:
                        if key.lower() in product['title'].lower():
                            comparitor(product, start)

            # Allows changes to be notified
            start = 0

            # User set delay
            time.sleep(float(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            
            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
