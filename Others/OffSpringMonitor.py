import requests
import json
import logging
import dotenv
import datetime
import time
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy

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
    url = 'https://www.offspring.co.uk/view/category/offspring_catalog/1.json?sort=-releasedate'
    s = requests.Session()
    html = s.get(url=url, headers=headers, proxies=proxy)
    output = json.loads(html.text)
    for product in output["searchResults"]["results"]:
        item = [product['brand']['name'], product['name'], product['picture']['thumbnail']['url'], product['productPageUrl'], product['shoeColour']['name']]
        items.append(item)
    return items


def checker(product):
    """
    Determines whether the product status has changed
    """
    for item in INSTOCK:
        if item == product:
            return True
    return


def discord_webhook(product_item):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if product_item == 'initial':
        embed["description"] = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know " \
                               "that everything is working fine! You can find more monitoring solutions at " \
                               "https://github.com/yasserqureshi1/Sneaker-Monitors "
    else:
        embed["title"] = f'{product_item[0]} {product_item[1]}'
        embed["thumbnail"] = {'url': product_item[2]}
        embed['url'] = f'https://www.offspring.co.uk{product_item[3]}'
        embed["fields"] = [{'name': 'Colour:', 'value': product_item[4]}]
    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Made by Yasser Qureshi'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

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
        INSTOCK.append(product)
        if start == 0:
            discord_webhook(product)
            print(product)


def monitor():
    """
    Initiates monitor for the Off-Spring site
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook('initial')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for product in items:
                if keywords == '':
                    comparitor(product, start)
                else:
                    check = False
                    for key in keywords:
                        if key.lower() in product[0].lower():
                            check = True
                    if check:
                        comparitor(product, start)
            start = 0
            time.sleep(float(CONFIG['DELAY']))
        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
                       'accept-encoding': 'gzip, deflate, br',
                       'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
            if CONFIG['PROXY'] == "":
                proxy = {"http": f"http://{proxyObject.get()}"}
            else:
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    monitor()
