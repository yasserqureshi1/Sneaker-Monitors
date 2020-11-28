import requests
from bs4 import BeautifulSoup
import logging
import dotenv
import datetime
import time
import json

logging.basicConfig(filename='OffSpringlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class SoleboxMonitor:
    def __init__(self, webhook, proxy, loc):
        self.webhook = webhook
        self.loc = loc
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {'http': f'http://{proxy}'}
        self.all_items = []
        self.instock = []
        self.instock_copy = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}

    def scrape_main_site(self):
        """
        Scrapes Solebox site
        """
        url = f'https://www.solebox.com/{self.loc}/c/footwear?srule=standard&openCategory=true&sz=96'
        html = requests.get(url=url, headers=self.headers, timeout=10, proxies=self.proxy)
        output = BeautifulSoup(html.text, 'html.parser')

        array = output.find_all('div', {'class': 'b-product-grid-tile js-tile-container'})
        for ele in array:
            item = [ele.find('span', {'class': 'b-product-tile-brand b-product-tile-text js-product-tile-link'}).text.replace(' ','').replace('\n',''),
                    ele.find('div', {'class': 't-heading-main b-product-tile-title b-product-tile-text'}).text.replace('\n',''),
                    ele.find('span', {'class': 'b-product-tile-link js-product-tile-link'})['href'],
                    ele.find('source', {'media': "(min-width: 1024px)"})['data-srcset'].split(',')[0]]
            self.all_items.append(item)

    def checker(self, product):
        """
        Determines whether the product status has changed
        """
        for item in self.instock_copy:
            if item == product:
                self.instock_copy.remove(product)
                return True
        return

    def discord_webhook(self, product_item):
        """
        Sends a Discord webhook notification to the specified webhook URL
        """
        data = {}
        data["username"] = CONFIG['USERNAME']
        data["avatar_url"] = CONFIG['AVATAR_URL']
        data["embeds"] = []
        embed = {}
        embed["title"] = f'{product_item[0]} {product_item[1]}'
        embed['url'] = f'https://www.solebox.com{product_item[2]}'
        embed["color"] = int(CONFIG['COLOUR'])
        embed["thumbnail"] = {'url': product_item[3]}
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))

    def remove_duplicates(self, mylist):
        """
        Removes duplicate values from a list
        """
        return [list(t) for t in set(tuple(element) for element in mylist)]

    def monitor(self):
        """
        Initiates monitor for Solebox site
        """

        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')

        start = 1
        while True:
            self.scrape_main_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_copy = self.instock.copy()
            for product in self.all_items:
                if not self.checker(product):
                    self.instock.append(product)
                    if start == 0:
                        self.discord_webhook(product)
                        print(product)

            start = 0
            time.sleep(1)


if __name__ == '__main__':
    SoleboxMonitor(CONFIG['WEBHOOK'], CONFIG['PROXY'], CONFIG['LOC']).monitor()
