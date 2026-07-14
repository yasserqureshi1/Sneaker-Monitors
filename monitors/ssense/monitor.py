# No restocks, only releases
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import requests
import urllib3
from fp.fp import FreeProxy

from datetime import datetime, timezone
import time

import json
import logging
import traceback

from curl_cffi import requests as cf

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='ssense-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []



def discord_webhook(title, id, price, url, thumbnail):
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
            "colour": int(COLOUR),
            "footer": {"text": "Developed by GitHub:yasserqureshi1"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fields": [
                {"name": "ID", "value": id},
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


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def scrape_main_site(user_agent, proxy):
    """
    Scrape the Ssense men's shoes listing.
    Ssense sits behind Cloudflare; curl_cffi (TLS impersonation) reaches the
    server-rendered page without a headless browser. Each product is embedded as
    its own ld+json block, which we parse directly.
    """
    items = []

    r = cf.get('https://www.ssense.com/en-us/men/shoes', impersonate='chrome124',
               proxies=proxy if proxy else None, timeout=25,
               headers={'accept-language': 'en-US,en;q=0.9'})
    soup = BeautifulSoup(r.text, 'html.parser')

    for block in soup.find_all('script', {'type': 'application/ld+json'}):
        try:
            prod = json.loads(block.string or block.text)
        except (ValueError, TypeError):
            continue
        if prod.get('@type') != 'Product':
            continue
        offers = prod.get('offers') or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        item = [
            prod['name'],
            prod['productID'],
            str(offers.get('price', '')),
            prod.get('image', ''),
            'https://www.ssense.com/en-us' + prod['url']
        ]
        items.append(item)

    logging.info(msg='Successfully scraped site')
    return items


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        # If product is available but not stored - sends notification and stores
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(
                title=item[0],
                id=item[1],
                price=item[2],
                thumbnail=item[3],
                url=item[4]
            )
            print(item)


def monitor():
    """
    Initiates monitor
    """
    print('''\n----------------------------------
--- SSENSE MONITOR HAS STARTED ---
----------------------------------\n''')
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

    user_agent = user_agent_rotator.get_random_user_agent()

    while True:
        try:
            # Makes request to site and stores products
            items = remove_duplicates(scrape_main_site(user_agent, proxy))
            for item in items:

                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if key.lower() in item[0].lower():
                            comparitor(item, start)

            # Allows changes to be notified
            start = 0

        except requests.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            user_agent = user_agent_rotator.get_random_user_agent()
            
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
