from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import urllib3
import requests

from datetime import datetime
import time

import json
import logging
import dotenv
import traceback

logging.basicConfig(filename='Sivasdescalzolog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

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


def test_webhook():
    """
    Sends a test Discord webhook notification
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these monitors!",
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Eznir'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(title, url, thumbnail, price):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "url": url,
            "thumbnail": {"url": thumbnail},
            "footer": {"text": "Created by Eznir"},
            "color": int(CONFIG['COLOUR']),
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "Price", "value": price}
            ]
        }]
    }

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

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
        try:
            # Makes request to site and stores products
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for item in items:
                
                if keywords == '':
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)
                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in keywords:
                        if key.lower() in item[0].lower():
                            comparitor(item, start)
            
            # Allows changes to be notified
            start = 0

            # User set delay
            time.sleep(float(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            
            if CONFIG['PROXY'] != "":
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
