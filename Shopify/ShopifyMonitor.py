import requests as rq
import json
import time
import datetime
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
        self.pages = []
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
        self.pages.clear()
        s = rq.Session()
        page = 1
        while page > 0:
            try:
                html = s.get(self.url + '?page=' + str(page) + '&limit=250', headers=self.headers, proxies=self.proxy, verify=False, timeout=5)
                output = json.loads(html.text)['products']
                if output == []:
                    page = 0
                else:
                    self.pages.append(output)
                    logging.info(msg='Successfully scraped site')
                    page += 1
            except Exception as e:
                logging.error(e)
                page = 0
            time.sleep(0.2)
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
        return

    def discord_webhook(self, product_item):
        """
        Sends a Discord webhook notification to the specified webhook URL
        :param product_item: An array containing the product name, product sizes in-stock ans the thumbnail URL
        :return: None
        """
        description = ''
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
        embed["title"] = product_item[0]
        embed["description"] = "**SHOP: **" + self.url.split('.com/')[0] + '.com/ \n\n' + '**SIZES:** \n' + description
        embed['url'] = link
        embed["color"] = int(CONFIG['COLOUR'])
        embed["thumbnail"] = {'url': product_item[2]}
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.datetime.now())
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
        return [list(t) for t in set(tuple(element) for element in mylist)]

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

        start = 1
        while True:
            self.scrape_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_products_copy = self.instock_products.copy()
            for page in self.pages:
                for product in page:
                    product_item = [product['title'], [], product['images'][0]['src'], product['handle']]
                    for size in product['variants']:
                        if size['available'] == True:
                            if self.checker(product['handle']):
                                pass
                            else:
                                self.instock_products.append(product['handle'])
                                product_item[1].append(size['title'])
                        else:
                            if self.checker(product['handle']):
                                self.instock_products.remove(product['handle'])
                    if product_item[1] == []:
                        pass
                    else:
                        if start == 0:
                            print(product_item)
                            self.discord_webhook(product_item)
                            logging.info(msg='Successfully sent Discord notification')
                self.pages.remove(page)
            start = 0
            time.sleep(0.1)


if __name__ == '__main__':
    urllib3.disable_warnings()
    ShopifyMonitor(url=CONFIG['URL'], webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY']).monitor()
