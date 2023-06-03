from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import requests
import urllib3
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='supreme-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []


def discord_webhook(title, price, variant, sku, thumbnail, url):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "thumbnail": {"url": thumbnail},
            "url": url,
            "color": int(COLOUR),
            "footer": {'text': 'Developed by GitHub:yasserqureshi1'},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "SKU", "value": sku},
                {"name": "Variant", "value": variant},
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
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def scrape_main_site(headers, proxy):
    url = 'https://uk.supreme.com/collections/all'

    html = requests.get(url, headers=headers, proxies=proxy)
    soup = BeautifulSoup(html.text, 'html.parser')

    products = soup.find('script',{'class':'js-first-all-products-json'})
    output = json.loads(products.text)['products']

    return output


def comparitor(item, start):
    for variant in item["variants"]:
        variant_id = variant['id']
        if variant["available"] == True:
            # Checks if it already exists in our instock
            if variant_id not in INSTOCK:
                # Add to instock array
                INSTOCK.append(variant_id)

                # Send a notification to the discord webhook with the in-stock product
                if start == 0:
                    print(variant["name"])
                    discord_webhook(
                        title=variant["name"],
                        price=str(variant['price']/100),
                        variant=variant['title'],
                        sku=variant["sku"],
                        thumbnail='https:' + item["image"],
                        url='https://uk.supremenewyork.com' + item['url']
                    )
                    logging.info(msg='Successfully sent Discord notification')

        else:
            if variant_id in INSTOCK:
                INSTOCK.remove(variant_id)


def monitor():
    """
    Initiates the monitor
    """
    print('''\n-----------------------------------
--- SUPREME MONITOR HAS STARTED ---
-----------------------------------\n''')
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
        'user-agent': user_agent_rotator.get_random_user_agent(),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

    while True:
        try:
            # Makes request to site and stores products 
            stock = scrape_main_site(proxy, headers)
            for item in stock:
                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)
                
                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if key.lower() in item['title'].lower():
                            comparitor(item, start)
            
            # Allows changes to be notified
            start = 0

        except requests.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            headers["User-Agent"] = user_agent_rotator.get_random_user_agent()

            if ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif PROXY != []:
                proxy_no = 0 if proxy_no == (len(PROXY)-1) else proxy_no + 1
                proxy = {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

        time.sleep(float(DELAY))

if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
