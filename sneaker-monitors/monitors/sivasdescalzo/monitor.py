from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import urllib3
import requests
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback

import sqlite3
import os

con = sqlite3.connect(os.path.abspath('config.db'))
cur = con.cursor()
item = cur.execute(f"SELECT * FROM monitors WHERE name = 'sivasdescalzo'")
for i in item:
    WEBHOOK = i[1]
    USERNAME = i[2]
    AVATAR_URL = i[3]
    COLOUR = i[4]
    DELAY = i[5]
    KEYWORDS = None if i[6] is None else i[6]
    PROXIES = [] if i[7] is None else i[7]
    FREE_PROXY = i[8]   #location
    DETAILS = i[9]

logging.basicConfig(filename='sivasdescalzo-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY, rand=True)

INSTOCK = []


def scrape_main_site(headers, proxy):
    """
    Scrape the Zalando site and adds each item to an array
    """
    items = []

    # Makes request to site
    url = 'https://www.sivasdescalzo.com/en/footwear'
    s = requests.Session()
    html = s.get(url=url, headers=headers, proxies=proxy, verify=False, timeout=15)
    soup = BeautifulSoup(html.text, 'html.parser')
    products = soup.find_all('li',  {'class': 'item product product-item grid-col'})
    
    # Stores particular details in array
    for product in products:
        item = [f"{product.find('h3', {'class': 'product-card__title'}).text} {product.find('h3', {'class': 'product name product-item-name product-card__short-desc'}).text}",  
                product.find('a')['href'], 
                product.find('div', {'class': 'price-box price-final_price'}).text, 
                f"{product.find('img')['src'].split('?')[0]}?quality=50&fit=bounds&width=210"] 
        items.append(item)
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
            "timestamp": str(datetime.utcnow()),
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


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        INSTOCK.append(item)
        if start == 0:
            print(item)
            discord_webhook(
                title=item[0],
                url=item[1],
                price=item[2],
                thumbnail=item[3]
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
    if FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    elif PROXIES != []:
        proxy_no = 0
        proxy = {} if PROXIES == [] else {"http": f"http://{PROXIES[proxy_no]}"}
    else:
        proxy = {}

    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    
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

            # User set delay
            time.sleep(float(DELAY))

        except requests.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            headers['User-Agent'] = user_agent_rotator.get_random_user_agent()
            
            if FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif PROXIES != []:
                proxy_no = 0 if proxy_no == (len(PROXIES)-1) else proxy_no + 1
                proxy = {"http": f"http://{PROXIES[proxy_no]}"}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)


urllib3.disable_warnings()
monitor()
