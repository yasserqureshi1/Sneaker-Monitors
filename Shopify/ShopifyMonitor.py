import requests as rq
import json
import time
from datetime import datetime
import urllib3
import logging
import dotenv

logging.basicConfig(filename='Shopifylog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class ShopifyMonitor:
    def __init__(self, url, webhook, proxy):
        self.url = url
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.items = []
        self.instock_products = []
        self.instock_products_copy = []
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"http": f"http://{proxy}"}

    def check_url(self):
        """
        Checks whether the supplied URL is valid
        :return: Boolean - True if valid
        """
        return 'products.json' in self.url

    def scrape_site(self):
        """
        Scrapes the specified Shopify site and adds items to array
        :return: None
        """
        self.items = []
        s = rq.Session()
        page = 1
        while page > 0:
            try:
                html = s.get(self.url + '?page=' + str(page) + '&limit=250', headers=self.headers, proxies=self.proxy, verify=False, timeout=20)
                output = json.loads(html.text)['products']
                if output == []:
                    page = 0
                else:
                    for product in output:
                        product_item = [{'title': product['title'], 'image': product['images'][0]['src'], 'handle': product['handle'], 'variants':product['variants']}]
                        self.items.append(product_item)
                    logging.info(msg='Successfully scraped site')
                    page += 1
            except Exception as e:
                logging.error(e)
                page = 0
            time.sleep(0.5)
        s.close()

    def checker(self, handle):
        """
        Determines whether the product status has changed
        :param product: Product name
        :param size: Product size
        :return:
        """
        for item in self.instock_products_copy:
            if item == handle:
                self.instock_products_copy.remove(handle)
                return True
        return False

    def discord_webhook(self, product_item):
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
            for i in range(len(product_item[1])):
                if i % 2 == 1:
                    description = description + str(product_item[1][i].replace(' : ', '/')) + '\n'
                else:
                    description = description + str(product_item[1][i].replace(' : ', '/')) + '\t\t'

            link = self.url.replace('.json', '/') + product_item[3]

        data = {}
        data["username"] = CONFIG['USERNAME']
        data["avatar_url"] = CONFIG['AVATAR_URL']
        data["embeds"] = []
        embed = {}
        if product_item[0] != 'initial':
            embed["title"] = product_item[0]
            embed['url'] = link
            embed["thumbnail"] = {'url': product_item[2]}
            embed["description"] = "**SHOP: **" + self.url.split('.com/')[0] + '.com/ \n\n' + '**SIZES:** \n' + description
        else:
            embed["description"] = description
        embed["color"] = int(CONFIG['COLOUR'])
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.utcnow())
        data["embeds"].append(embed)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            logging.error(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))

    def remove_duplicates(self, mylist):
        """
        Removes duplicate values from a list
        :param mylist: list
        :return: list
        """
        return list(set(mylist))

    def monitor(self):
        """
        Initiates the monitor
        :return: None
        """
        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        if self.check_url() == False:
            print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
            logging.error(msg='Store URL formatting incorrect for: ' + str(self.url))
            return

        self.discord_webhook(['initial'])
        start = 1
        while True:
            self.scrape_site()
            self.instock_products_copy = self.instock_products.copy()
            for product in self.items:
                product_item = [product[0]['title'], [], product[0]['image'], product[0]['handle']]
                available_sizes = []
                for size in product[0]['variants']:
                    if size['available'] == True:
                        available_sizes.append(size['title'])

                if available_sizes:
                    if self.checker(product[0]['handle']):
                        pass
                    else:
                        self.instock_products.append(product[0]['handle'])
                        product_item[1].append(available_sizes)
                else:
                    if self.checker(product[0]['handle']):
                        self.instock_products.remove(product[0]['handle'])
                if not product_item[1]:
                    pass
                else:
                    if start == 0:
                        print(product_item)
                        self.discord_webhook(product_item)
                        logging.info(msg='Successfully sent Discord notification')
            start = 0
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings()
    ShopifyMonitor(url=CONFIG['URL'], webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY']).monitor()
