import requests as rq
import json
import time
from datetime import datetime
import urllib3
import logging
import dotenv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy

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
    Return its content.
    """

    url = "https://www.supremenewyork.com/mobile_stock.json"
    stock = rq.get(url=url, headers=headers, proxies=proxy, timeout=10).json()['products_and_categories']
    return stock


def get_item_variants(item_id, item_name, start, proxy, headers):
    """
    Scrapes each item on the webstore and checks whether the product is in-stock or not. If in-stock
    it will send a Discord notification
    """

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
                    # Add to instock dict
                    INSTOCK.append(item)

                    # Send a notification to the discord webhook with the in-stock product
                    if start == 0:
                        print('Sending new Notification')
                        print(item)
                        discord_webhook(item)
                        logging.info(msg='Successfully sent Discord notification')

            else:
                if checker(item):
                    INSTOCK.remove(item)


def discord_webhook(product_item):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param product_item: A list of the product's details
    :return: None
    """

    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []

    embed = {}

    if product_item != 'initial':
        embed["title"] = product_item[0] + ' - ' + product_item[1] + ' - ' + product_item[2]
        embed["description"] = product_item[3]
        embed["thumbnail"] = {'url': product_item[4]}
        embed['url'] = product_item[5]
    else:
        embed["title"] = ''
        embed["description"] = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know " \
                               "that everything is working fine! You can find more monitoring solutions at " \
                               "https://github.com/yasserqureshi1/Sneaker-Monitors "

    embed["color"] = CONFIG['COLOUR']
    embed["footer"] = {'text': 'Made by Yasser & Bogdan'}
    embed["timestamp"] = str(datetime.utcnow())
    data["embeds"].append(embed)

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
    :return: Boolean whether the status has changed or not
    """
    for item in INSTOCK:
        if item == product:
            return True
    return False


def monitor():
    """
    Initiates the monitor
    :return: None
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook('initial')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": proxyObject.get()} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            stock = get_stock(proxy, headers)
            time.sleep(float(CONFIG["DELAY"]))
            for cat in stock:
                for product_item in stock[cat]:
                    check = False
                    if keywords == "":
                        get_item_variants(product_item['id'], product_item['name'], start, proxy, headers)
                    else:
                        for key in keywords:
                            if key.lower() in product_item['name'].lower():
                                check = True
                                break
                        if check:
                            get_item_variants(product_item['id'], product_item['name'], start, proxy, headers)
                    time.sleep(0.5)
            start = 0
            logging.info(msg='Successfully monitored site')
        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            if CONFIG['PROXY'] == "":
                proxy = {"http": proxyObject.get()}
            else:
                proxy_no = 0 if proxy_no == (len(proxy_list)-1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
