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

logging.basicConfig(filename='Shopifylog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

INSTOCK = []


def check_url(url):
    """
    Checks whether the supplied URL is valid
    :return: Boolean - True if valid
    """
    return 'products.json' in url


def scrape_site(url, headers, proxy):
    """
    Scrapes the specified Shopify site and adds items to array
    :return: None
    """
    items = []
    s = rq.Session()
    page = 1
    while True:
        html = s.get(url + f'?page={page}&limit=250', headers=headers, proxies=proxy, verify=False, timeout=20)
        output = json.loads(html.text)['products']
        if output == []:
            break
        else:
            for product in output:
                product_item = [
                    {'title': product['title'], 'image': product['images'][0]['src'], 'handle': product['handle'],
                     'variants': product['variants']}]
                items.append(product_item)
            logging.info(msg='Successfully scraped site')
            page += 1
    
    time.sleep(float(CONFIG['DELAY']))
    s.close()
    return items


def checker(handle):
    """
    Determines whether the product status has changed
    """
    for item in INSTOCK:
        if item == handle:
            return True
    return False


def discord_webhook(product_item):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param product_item: An array containing the product name, product sizes in-stock ans the thumbnail URL
    :return: None
    """
    description = ''
    if product_item[0] == 'initial':
        description = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know that " \
                      "everything is working fine! You can find more monitoring solutions at " \
                      "https://github.com/yasserqureshi1/Sneaker-Monitors "
    else:
        fields = []
        for size in product_item[1][0]:
            fields.append({'name': size, 'value': 'Available', 'inline': True})

        link = CONFIG['URL'].replace('.json', '/') + product_item[3]

    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if product_item[0] != 'initial':
        embed["title"] = product_item[0]
        embed['url'] = link
        embed["thumbnail"] = {'url': product_item[2]}
        embed["fields"] = fields
    else:
        embed["description"] = description
    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Made by Yasser Qureshi'}
    embed["timestamp"] = str(datetime.utcnow())
    data["embeds"].append(embed)
    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    :param mylist: list
    :return: list
    """
    return list(set(mylist))


def comparitor(product, start):
    product_item = [product[0]['title'], [], product[0]['image'], product[0]['handle']]
    available_sizes = []
    for size in product[0]['variants']:
        if size['available']:
            available_sizes.append(size['title'])

    if available_sizes:
        if checker(product[0]['handle']):
            pass
        else:
            INSTOCK.append(product[0]['handle'])
            product_item[1].append(available_sizes)
    else:
        if checker(product[0]['handle']):
            INSTOCK.remove(product[0]['handle'])
    if not product_item[1]:
        pass
    else:
        if start == 0:
            print(product_item)
            discord_webhook(product_item)
            logging.info(msg='Successfully sent Discord notification')


def monitor():
    """
    Initiates the monitor
    :return: None
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    if not check_url(CONFIG['URL']):
        print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
        logging.error(msg='Store URL formatting incorrect for: ' + str(CONFIG['URL']))
        return

    discord_webhook(['initial'])
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            items = scrape_site(CONFIG['URL'], proxy, headers)
            for product in items:
                check = False
                if keywords == "":
                    comparitor(product, start)
                else:
                    for key in keywords:
                        if key.lower() in product[0]['title'].lower():
                            check = True
                            break
                    if check:
                        comparitor(product, start)
        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            if CONFIG['PROXY'] == "":
                proxy = {"http": f"http://{proxyObject.get()}"}
            else:
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}
        start = 0
        time.sleep(float(CONFIG['DELAY']))


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
