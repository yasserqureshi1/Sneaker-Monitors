# For the Palace Site Site (Type of Shopify Store)
import requests as rq
import json
import time
import datetime
import urllib3


class PalaceMonitor:
    def __init__(self, webhook, proxy):
        self.url = 'https://shop.palaceskateboards.com/collections/all/products.json'
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock_products = []
        self.instock_products_copy = []
        self.webhook = webhook
        self.proxy = proxy

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
                    page += 1
            except Exception as e:
                print('Error - ', e)
                page = 0
        s.close()

    def checker(self, product, size):
        """
        Determines whether the product status has changed
        :param product: Product name
        :param size: Product size
        :return:
        """
        for item in self.instock_products_copy:
            if item == [product, size]:
                self.instock_products_copy.remove([product, size])
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
        data["username"] = "Palace Monitor"
        #data["avatar_url"] = '[insert image url]'
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0]
        embed["description"] = "**SHOP: **" + self.url.split('.com/')[0] + '.com/ \n\n' + '**SIZES:** \n' + description
        embed['url'] = link
        embed["color"] = 15258703
        embed["thumbnail"] = {'url': product_item[2]}
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def monitor(self):
        """
        Initiates the monitor
        :return: None
        """
        if self.check_url() == False:
            print('Store URL not in correct format. Please ensure that it is a path pointing to a /products.json file')
            return

        print('STARTING MONITOR')
        start = 1
        while True:
            self.scrape_site()
            self.instock_products_copy = self.instock_products.copy()
            for page in self.pages:
                for product in page:
                    product_item = [product['title'], [], product['images'][0]['src'], product['handle']]
                    for size in product['variants']:
                        if size['available'] == True:
                            if self.checker(product['title'], size['title']):
                                pass
                            else:
                                self.instock_products.append([product['title'], size['title']])
                                product_item[1].append(size['title'])
                        else:
                            if self.checker(product['title'], size['title']):
                                self.instock_products.remove([product['title'], size['title']])

                    if product_item[1] == []:
                        pass
                    else:
                        if start == 0:
                            print(product_item)
                            self.discord_webhook(product_item)
            start = 0
            time.sleep(3)


if __name__ == '__main__':
    urllib3.disable_warnings()
    webhook = ''
    # proxy = {"http": f"http://{proxy}"}
    proxy = {}
    Monitor = PalaceMonitor(webhook, proxy)
    Monitor.monitor()

