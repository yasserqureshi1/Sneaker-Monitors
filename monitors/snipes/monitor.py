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

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='snipes-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []


def discord_webhook(title, url, id, price, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": url,
            "color": int(COLOUR),
            "footer": {'text': 'Developed by GitHub:yasserqureshi1'},
            "thumbnail": {"url": thumbnail},
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


def scrape_main_site(headers, proxy):
    """
    Scrape the Snipes site and adds each item to an array
    """
    items = []

    # Makes request to site
    s = requests.Session()
    html = s.get('https://www.snipes.com/de-de/c/schuhe--3?sort=new', headers=headers, proxies=proxy, verify=False, timeout=50)
    soup = BeautifulSoup(html.text, 'html.parser')
    tiles = soup.find_all('sni-lib-product-search-item')

    # Stores particular details in array
    for tile in tiles:
        try:
            link = tile.find('a', {'class': 'product-item'})
            brand = tile.find(class_='product-brand')
            name = tile.find(class_='product-name')
            price = tile.find(class_='sale-price') or tile.find(class_='product-price')
            image = tile.find('img')
            href = link['href']
            item = [
                brand.get_text(strip=True),
                name.get_text(strip=True),
                'https://www.snipes.com' + href,
                href.rstrip('/').split('-')[-1],
                price.get_text(' ', strip=True),
                image['src'] if image else ''
            ]
            items.append(item)
        except (AttributeError, TypeError, KeyError):
            continue

    logging.info(msg='Successfully scraped site')
    s.close()
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
                title=f'{item[0]}: {item[1]}',
                url=item[2],
                id=item[3],
                price=item[4],
                thumbnail=item[5]
            )
            print(item)


def monitor():
    """
    Initiates monitor
    """
    print('''\n----------------------------------
--- SNIPES MONITOR HAS STARTED ---
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
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'user-agent': user_agent_rotator.get_random_user_agent(),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

    # Collecting all keywords (if any)
    while True:
        try:
            # Makes request to site and stores products 
            items = remove_duplicates(scrape_main_site(headers, proxy))
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
            headers['user-agent'] = user_agent_rotator.get_random_user_agent()
            
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
