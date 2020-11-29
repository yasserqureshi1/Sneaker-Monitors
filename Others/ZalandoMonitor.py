import requests
from bs4 import BeautifulSoup
import logging
import dotenv
import datetime
import json
import time
import urllib3

logging.basicConfig(filename='Zalandolog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)
CONFIG = dotenv.dotenv_values(dotenv_path='.env')


class ZalandoMonitor:
    def __init__(self, webhook, proxy):
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {'https': f'https://{proxy}'}
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                      'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
        self.all_items = []
        self.instock = []
        self.instock_copy = []

    def scrape_main_site(self):
        """
        Scrape the Zalando site and adds each item to an array
        :return:
        """
        url = 'https://m.zalando.co.uk/mens-shoes-trainers/?order=activation_date'
        s = requests.Session()
        html = s.get(url=url, headers=self.headers, proxies=self.proxy, verify=False, timeout=10)
        soup = BeautifulSoup(html.text, 'html.parser')
        products = soup.find_all('div',  {'class': 'qMZa55 SQGpu8 iOzucJ JT3_zV DvypSJ'})
        for product in products:
            item = [product.find('span', {'class': 'u-6V88 ka2E9k uMhVZi FxZV-M uc9Eq5 pVrzNP ZkIJC- r9BRio qXofat EKabf7'}).text,
                    product.find('h3', {'class': 'u-6V88 ka2E9k uMhVZi FxZV-M z-oVg8 pVrzNP ZkIJC- r9BRio qXofat EKabf7'}).text,
                    product.find('a', {'class': 'g88eG_ oHRBzn LyRfpJ JT3_zV g88eG_ ONArL- _2dqvZS lfPP-F'})['href'],
                    product.find('img', {'class': '_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw'})['src']]
            self.all_items.append(item)


    def discord_webhook(self, product_item):
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
        embed["title"] = product_item[0]  # Item Name
        embed["description"] = product_item[1]
        embed['url'] = f'https://m.zalando.co.uk{product_item[2]}'  # Item link
        embed["color"] = int(CONFIG['COLOUR'])
        embed["thumbnail"] = {'url': product_item[3]}  # Item image
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            logging.error(msg=err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info("Payload delivered successfully, code {}.".format(result.status_code))

    def checker(self, item):
        """
        Determines whether the product status has changed
        :param item: list of item details
        :return: Boolean whether the status has changed or not
        """
        for product in self.instock_copy:
            if product == item:
                self.instock_copy.remove(product)
                return True
        return False

    def remove_duplicates(self, mylist):
        """
        Removes duplicate values from a list
        :param mylist: list
        :return: list
        """
        return [list(t) for t in set(tuple(element) for element in mylist)]

    def monitor(self):
        """
        Initiates monitor
        :return:
        """
        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        start = 1
        while True:
            self.scrape_main_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_copy = self.instock.copy()
            for item in self.all_items:
                if not self.checker(item):
                    self.instock.append(item)
                    if start == 0:
                        self.discord_webhook(item)
                        print(item)
            time.sleep(1)
            start = 0


if __name__ == '__main__':
    urllib3.disable_warnings()
    ZalandoMonitor(CONFIG['WEBHOOK'], CONFIG['PROXY']).monitor()
