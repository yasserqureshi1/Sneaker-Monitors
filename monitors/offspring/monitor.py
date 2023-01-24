from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import requests
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='offspring-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []

def scrape_main_site(headers, proxy):
    """
    Scrapes Off-Spring API
    """
    items = []

    # Makes request to site
    url = 'https://www.offspring.co.uk/view/category/offspring_catalog/1.json?sort=-releasedate'
    s = requests.Session()
    html = s.get(url=url, headers=headers, proxies=proxy)

    output = json.loads(str(html.text))

    # Stores particular details in array
    for product in output["searchResults"]["results"]:
        item = [
            product['brand']['name'], 
            product['name'], 
            product['picture']['thumbnail']['url'], 
            product['productPageUrl'], 
            product['shoeColour']['name']
        ]
        items.append(item)

    logging.info(msg='Successfully scraped site')
    s.close()
    return items


def checker(product):
    """
    Determines whether the product status has changed
    """
    return product in INSTOCK


def discord_webhook(title, url, thumbnail, colour):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": 'https://www.offspring.co.uk/'+url,
            "thumbnail": {"url": thumbnail},
            "footer": {"text": "Developed by GitHub:yasserqureshi1"},
            "timestamp": str(datetime.utcnow()),
            "color": int(COLOUR),
            "fields": [
                {"name": "Colour", "value": colour}
            ]
        }]
    }

    result = requests.post(WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(product, start):
    if not checker(product):
        # If product is available but not stored - sends notification and stores
        INSTOCK.append(product)
        if start == 0:
            discord_webhook(
                title=f'{product[0]} - {product[1]}',
                thumbnail=product[2],
                url=product[3],
                colour=product[4],
            )
            print(product)


def monitor():
    """
    Initiates monitor for the Off-Spring site
    """
    print('''\n-------------------------------------
--- OFFSPRING MONITOR HAS STARTED ---
-------------------------------------\n''')
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent_rotator.get_random_user_agent(),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    while True:
        try:
            # Makes request to site and stores products 
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for product in items:

                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(product, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if key.lower() in product[0].lower():
                            comparitor(product, start)
            
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
    monitor()
