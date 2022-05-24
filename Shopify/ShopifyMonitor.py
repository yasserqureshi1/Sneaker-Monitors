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

logging.basicConfig(filename='shopifylog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

proxy_obj = FreeProxy(country_id=config.FREE_PROXY_LOCATION)

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
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these monitors!",
            "color": int(config.COLOUR),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

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
        fields.append({"name": size['title'], "value": size['url'], "inline": True})

    data = {
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": config.URL.replace('.json', '/') + url, 
            "thumbnail": {"url": thumbnail},
            "fields": fields,
            "color": int(config.COLOUR),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
        }]
    }

    result = rq.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

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
            available_sizes.append({'title': size['title'], 'url': '[ATC](' + config.URL[:config.URL.find('/', 10)] + '/cart/' + str(size['id']) + ':1)'})

    
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
    print('''\n---------------------------
--- MONITOR HAS STARTED ---
---------------------------\n''')
    print(''' ** Now you will recieve notifications when an item drops or restocks **
This may take some time so you have to leave this script running. It's best to do this on a server (you can get a free one via AWS)!
    
Check out the docs at https://yasserqureshi1.github.io/Sneaker-Monitors/ for more info.
    
Join the Sneakers & Code family via Discord and subscribe to my YouTube channel https://www.youtube.com/c/YasCode\n\n''')
    logging.info(msg='Successfully started monitor')

    # Checks URL
    if not check_url(config.URL):
        print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
        logging.error(msg='Store URL formatting incorrect for: ' + str(config.URL))
        return

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
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

    # Collecting all keywords (if any)
    keywords = config.KEYWORDS
    while True:
        try:
            # Makes request to site and stores products 
            items = scrape_site(config.URL, proxy, headers)
            for product in items:

                if keywords == []:
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
            time.sleep(float(config.DELAY))

        except (
            rq.exceptions.ConnectionError,
            rq.exceptions.ChunkedEncodingError,
            rq.exceptions.ConnectTimeout,
            rq.exceptions.HTTPError,
            rq.exceptions.ProxyError,
            rq.exceptions.Timeout,
            rq.exceptions.ReadTimeout,
            rq.exceptions.RetryError,
            rq.exceptions.SSLError,
            rq.exceptions.TooManyRedirects
        ) as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            headers['User-Agent'] = user_agent_rotator.get_random_user_agent()
            
            if config.ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif config.PROXY != []:
                proxy_no = 0 if proxy_no == (len(config.PROXY)-1) else proxy_no + 1
                proxy = {"http": f"http://{config.PROXY[proxy_no]}"}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)   


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()