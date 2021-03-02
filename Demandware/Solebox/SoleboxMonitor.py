import requests
from bs4 import BeautifulSoup
import logging
import dotenv
import datetime
import time
import json
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy

logging.basicConfig(filename='Solebox.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

INSTOCK = []


def scrape_main_site(headers, proxy):
    """
    Scrapes Solebox site
    """
    items = []
    url = f'https://www.solebox.com/{CONFIG["LOC"]}/c/footwear?srule=standard&openCategory=true&sz=96'
    html = requests.get(url=url, headers=headers, timeout=15, proxies=proxy)
    output = BeautifulSoup(html.text, 'html.parser')

    array = output.find_all('div', {'class': 'b-product-grid-tile js-tile-container'})
    for ele in array:
        item = [ele.find('span', {'class': 'b-product-tile-brand b-product-tile-text js-product-tile-link'}).text.replace(' ','').replace('\n',''),
                ele.find('div', {'class': 't-heading-main b-product-tile-title b-product-tile-text'}).text.replace('\n',''),
                ele.find('span', {'class': 'b-product-tile-link js-product-tile-link'})['href'],
                ele.find('source', {'media': "(min-width: 1024px)"})['data-srcset'].split(',')[0]]
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
        embed['url'] = f'https://www.solebox.com{product_item[2]}'
        embed["thumbnail"] = {'url': product_item[3]}
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
    Initiates monitor for Solebox site
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook('initial')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else {'http': f'http://{proxy_list[proxy_no]}'}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
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
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            if CONFIG['PROXY'] == "":
                proxy = {"http": f"http://{proxyObject.get()}"}
            else:
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    monitor()
