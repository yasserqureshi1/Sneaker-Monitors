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

logging.basicConfig(filename='suplog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)


INSTOCK = []


def get_stock(proxy, headers):
    """
    Makes a request to Supreme's mobile_stock endpoint.
    """
    url = "https://www.supremenewyork.com/mobile_stock.json"
    stock = rq.get(url=url, headers=headers, proxies=proxy, timeout=10).json()['products_and_categories']
    return stock


def get_item_variants(item_id, item_name, start, proxy, headers):
    """
    Scrapes each item on the webstore and checks whether the product is in-stock or not. If in-stock
    it will send a Discord notification
    """
    try:
        item_url = f"https://www.supremenewyork.com/shop/{item_id}.json"

        item_variants = rq.get(item_url, headers=headers, proxies=proxy).json()

        for stylename in item_variants["styles"]:
            for itemsize in stylename["sizes"]:
                item = [item_name, stylename["name"], itemsize['name'], item_variants["description"], 'https:' + stylename["image_url"], item_url.split('.json')[0]]
                if itemsize["stock_level"] != 0:
                    # Checks if it already exists in our instock
                    if checker(item):
                        pass
                    else:
                        # Add to instock array
                        INSTOCK.append(item)

                        # Send a notification to the discord webhook with the in-stock product
                        if start == 0:
                            print(item)
                            discord_webhook(
                                title=f'{item_name} - {stylename["name"]} - {itemsize["name"]}',
                                description=item_variants["description"],
                                thumbnail='https:' + stylename["image_url"],
                                url=item_url.split('.json')[0]
                            )
                            logging.info(msg='Successfully sent Discord notification')

                else:
                    if checker(item):
                        INSTOCK.remove(item)
    
    except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {
                'User-Agent': user_agent_rotator.get_random_user_agent(),
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list)-1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


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
            "color": CONFIG['COLOUR'],
            "footer": {'text': 'Made by Yasser & Bogdan'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(title, description, thumbnail, url):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "description": description,
            "thumbnail": {"url": thumbnail},
            "url": url,
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Yasser & Bogdan'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def checker(product):
    """
    Determines whether the product status has changed
    """
    return product in INSTOCK


def monitor():
    """
    Initiates the monitor
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
    headers = {
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            # Makes request to site and stores products 
            stock = get_stock(proxy, headers)
            time.sleep(float(CONFIG["DELAY"]))
            for cat in stock:
                for product_item in stock[cat]:

                    if keywords == "":
                        # If no keywords set, checks whether item status has changed
                        get_item_variants(product_item['id'], product_item['name'], start, proxy, headers)
                    
                    else:
                        # For each keyword, checks whether particular item status has changed
                        for key in keywords:
                            if key.lower() in product_item['name'].lower():
                                get_item_variants(product_item['id'], product_item['name'], start, proxy, headers)
            
            # Allows changes to be notified
            start = 0

            # Logging
            logging.info(msg='Supreme scrape successful')
            
        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {
                'User-Agent': user_agent_rotator.get_random_user_agent(),
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list)-1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
