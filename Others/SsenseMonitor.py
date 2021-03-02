# No restocks, only releases
import requests
import datetime
import json
from bs4 import BeautifulSoup
import urllib3
import time
import logging
import dotenv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy

logging.basicConfig(filename='Ssenselog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

INSTOCK = []


def discord_webhook(product_item):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param product_item: An array of the product's details
    :return: None
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
        embed["title"] = product_item[0]  # Item Name
        embed["description"] = product_item[1]
        embed['url'] = f'https://www.ssense.com{product_item[2]}'  # Item link
        embed["thumbnail"] = {'url': product_item[3]}  # Item image
    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Made by Yasser'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

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
    :param item: list of item details
    :return: Boolean whether the status has changed or not
    """
    for product in INSTOCK:
        if product == item:
            return True
    return False


def scrape_main_site(headers, proxy):
    """
    Scrape the Ssense site and adds each item to an array
    :return: None
    """
    s = requests.Session()
    items = []
    url = 'https://www.ssense.com/en-gb/men/shoes/'
    html = s.get(url=url, headers=headers, verify=False, timeout=15, proxies=proxy)
    soup = BeautifulSoup(html.text, 'html.parser')
    array = soup.find_all('div', {'class': 'plp-products__column'})
    for i in array:
        item = [i.find('span', {'class': 's-text s-text--uppercase'}).text,
                i.find('div', {'class': 'product-tile__description'}).text.replace(
                    i.find('span', {'class': 's-text'}).text, '').split('£')[0], i.find('a')['href'],
                i.find('img')['data-srcset']]
        items.append(item)
    logging.info(msg='Successfully scraped site')

    s.close()
    return items


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    :param mylist: list
    :return: list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(item)
            print(item)


def monitor():
    """
    Initiates monitor
    :return: None
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook('initial')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                         'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for item in items:
                check = False
                if keywords == "":
                    comparitor(item, start)
                else:
                    for key in keywords:
                        if key.lower() in item[0].lower():
                            check = True
                            break
                    if check:
                        comparitor(item, start)

            start = 0
            time.sleep(float(CONFIG['DELAY']))
        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
                       'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                                 'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
            if CONFIG['PROXY'] == "":
                proxy = {"http": f"http://{proxyObject.get()}"}
            else:
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
