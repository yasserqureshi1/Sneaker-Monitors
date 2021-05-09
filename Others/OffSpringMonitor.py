from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from fp.fp import FreeProxy

import requests

from datetime import datetime
import time

import json
import logging
import dotenv

logging.basicConfig(filename='OffSpringlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

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
            "footer": {'text': 'Made by Yasser'},
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


def discord_webhook(title, url, thumbnail, colour):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "url": 'https://www.offspring.co.uk/'+url,
            "thumbnail": {"url": thumbnail},
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "color": int(CONFIG['COLOUR']),
            "fields": [
                {"name": "Colour", "value": colour}
            ]
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
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    
    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    proxy_no = 0
    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": proxyObject.get()} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
    
    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            # Makes request to site and stores products 
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for product in items:

                if keywords == '':
                    # If no keywords set, checks whether item status has changed
                    comparitor(product, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in keywords:
                        if key.lower() in product[0].lower():
                            comparitor(product, start)
            
            # Allows changes to be notified
            start = 0

            # User set delay
            time.sleep(float(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
                       'accept-encoding': 'gzip, deflate, br',
                       'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    monitor()
