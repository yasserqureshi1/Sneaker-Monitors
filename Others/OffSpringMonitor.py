import requests
import json
import logging
import dotenv
import datetime
import time

logging.basicConfig(filename='OffSpringlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class OffSpringMonitor:
    def __init__(self, webhook, proxy):
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"http": f"http://{proxy}"}
        self.all_items = []
        self.instock = []
        self.instock_copy = []
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

    def scrape_main_site(self):
        """
        Scrapes Off-Spring API
        """
        url = 'https://www.offspring.co.uk/view/category/offspring_catalog/1.json?sort=-releasedate'
        s = requests.Session()
        html = s.get(url=url, headers=self.headers, proxies=self.proxy)
        output = json.loads(html.text)
        for product in output["searchResults"]["results"]:
            item = [product['brand']['name'], product['name'], product['picture']['thumbnail']['url'], product['productPageUrl'], product['shoeColour']['name']]
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
        if product_item == 'initial':
            embed["description"] = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know " \
                                   "that everything is working fine! You can find more monitoring solutions at " \
                                   "https://github.com/yasserqureshi1/Sneaker-Monitors "
        else:
            embed["title"] = f'{product_item[0]} {product_item[1]}'
            embed["thumbnail"] = {'url': product_item[2]}
            embed['url'] = f'https://www.offspring.co.uk{product_item[3]}'
            embed["description"] = f'*Colour:* {product_item[4]}'
        embed["color"] = int(CONFIG['COLOUR'])
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.datetime.utcnow())
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
        Initiates monitor for the Off-Spring site
        """

        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        self.discord_webhook('initial')
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
    OffSpringMonitor(CONFIG['WEBHOOK'], CONFIG['PROXY']).monitor()
