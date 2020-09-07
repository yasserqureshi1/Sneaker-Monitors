import requests as rq
import json
import time
import datetime


class ShopifyMonitor:
    def __init__(self, url, webhook):
        self.url = url
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock_products = []
        self.instock_products_copy = []
        self.webhook = webhook

    def check_url(self):
        split = self.url.split('.com', 1)
        self.url = split[0] + '.com/' + 'collections/new-arrivals-1/' + 'products.json?page='

    def scrape_site(self):
        self.pages.clear()
        s = rq.Session()
        num = 1
        # scrape each product page
        while num > 0:
            try:
                # html = s.get(self.url + str(num) + '&limit=250', headers=self.headers, verify=False, timeout=1)
                html = s.get(self.url, headers=self.headers, verify=False, timeout=1)
                output = json.loads(html.text)['products']
                if output == []:
                    # once there are no more products - exit loop
                    num = 0
                else:
                    # add product page to list
                    self.pages.append(output)
                    num = num + 1
                    num = 0
            except:
                print('There was an Error')
                num = 0

        s.close()

    def checker(self, product, size):
        # check if item is in list
        for item in self.instock_products_copy:
            if item == [product, size]:
                self.instock_products_copy.remove([product, size])
                return True
        return

    def discord_webhook(self, product_item):
        description = ''
        for i in range(len(product_item[1])):
            if i % 2 == 1:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '\n'
            else:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '\t\t'

        link = self.url.replace('.json', '/') + product_item[3]

        data = {}
        data["username"] = "[insert name]"
        data["avatar_url"] = '[insert image url]'
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
        while True:
            self.scrape_site()
            self.instock_products_copy = self.instock_products.copy()
            for page in self.pages:
                for product in page:
                    product_item = [product['title'], [], product['images'][0]['src'], product['handle']]
                    for size in product['variants']:
                        # if the product is available....
                        if size['available'] == True:
                            # check if product is already stored ...
                            if self.checker(product['title'], size['title']):
                                # nothing
                                pass
                            # if not, means its a restock or a newly added item ...
                            else:
                                self.instock_products.append([product['title'], size['title']])
                                product_item[1].append(size['title'])

                        # if not available, but stored, remove it
                        else:
                            if self.checker(product['title'], size['title']):
                                self.instock_products.remove([product['title'], size['title']])

                    if product_item[1] == []:
                        pass
                    else:
                        self.discord_webhook(product_item)
                        print(product_item)
            time.sleep(3)


if __name__ == '__main__':
    webhook = 'https://discordapp.com/api/webhooks/738175021083787305/XTJeMY_-vThNzoUDVcfdAegUopm3TRbTTdZgydtcYj_4FB2CK1MjIRXlWgAozoyBnRKX'
    #url = 'https://www.hanon-shop.com/collections/whats-new/products.json'
    url = 'https://uj-iv.com/collections/all/products.json'
    Monitor = ShopifyMonitor(url, webhook)
    Monitor.monitor()
