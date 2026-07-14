from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import urllib3
import requests
from curl_cffi import requests as cf
from fp.fp import FreeProxy

from datetime import datetime, timezone
import time

import json
import logging
import traceback

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='sivasdescalzo-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []

def scrape_main_site(headers, proxy):
    """
    Scrape the Zalando site and adds each item to an array
    """
    items = []

    # sivasdescalzo is a headless Magento store behind Cloudflare. We call the
    # same /rest/ JSON API the site uses, via curl_cffi (TLS impersonation) so
    # the request looks like a real browser. Newest-first footwear listing.
    url = ('https://www.sivasdescalzo.com/rest/en/V2/category?urlPath=footwear'
           '&pageSize=96&currentPage=1&filters=%7B%7D&sort=%7B%22sorting_date%22%3A%22DESC%22%7D')
    html = cf.get(url, impersonate='chrome', proxies=proxy if proxy else None, timeout=20)
    products = html.json().get('data', {}).get('products', {}).get('items', [])

    # Stores particular details in array
    for product in products:
        try:
            item = [
                product['brand_name'],                                                       # brand
                product['name'],                                                             # name
                product['url'],                                                              # url
                product.get('final_price_formatted') or str(product.get('final_price', '')),  # price
                product.get('small_image', '')                                               # image
            ]
            items.append(item)
        except (KeyError, TypeError):
            logging.debug(traceback.format_exc())

    return items


def discord_webhook(title, url, thumbnail, price):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": url,
            "thumbnail": {"url": thumbnail},
            "footer": {"text": "Developed by GitHub:yasserqureshi1"},
            "color": int(COLOUR),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fields": [
                {"name": "Price", "value": price}
            ]
        }]
    }

    result = requests.post(WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(result.status_code))


def comparitor(item, start):
    if item not in INSTOCK:
        INSTOCK.append(item)
        if start == 0:
            print(item)
            discord_webhook(
                title=f"{item[0]} {item[1]}",
                url=item[2],
                price=item[3],
                thumbnail=item[4]
            )


def monitor():
    """
    Initiates monitor
    """
    print('''\n-----------------------------------------
--- SIVASDESCALZO MONITOR HAS STARTED ---
-----------------------------------------\n''')
    logging.info(msg='Successfully started monitor')
    

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
            items = scrape_main_site(headers, proxy)
            for item in items:
                
                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)
                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if (key.lower() in item[0].lower()) or (key.lower() in item[1].lower()):
                            comparitor(item, start)
            
            # Allows changes to be notified
            start = 0

        except requests.exceptions.RequestException as e:
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
