# may need to use beautifulsoup instead

import requests as rq
import json
import time


class SupremeMonitor:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock = []
        self.instock_copy = []

    def scrape_main_site(self):
        self.pages.clear()
        s = rq.Session()
        try:
            html = s.get('https://www.supremenewyork.com/mobile_stock.json', headers=self.headers, verify=False,
                         timeout=1)
            output = json.loads(html.text)['products_and_categories']
            self.pages.append(output)
        except:
            print('There was an Error')

    def scrape_item_site(self, name, id):
        try:
            url = 'https://www.supremenewyork.com/shop/' + str(id) + '.json'
            html = rq.get(url, headers=self.headers, verify=False, timeout=0.3)
            output = json.loads(html.text)['styles']

            for colour in output:
                for size in colour['sizes']:
                    if size['stock_level'] == 1:
                        if self.checker(name, colour['name'], size['name']):
                            pass
                        else:
                            self.instock.append([name, colour['name'], size['name']])
                            restock = 'RESTOCK: ' + str(name) + ' in ' + str(colour['name']) + ' in size ' + str(
                                size['name'])
                            print(restock)
                            message = {"content": restock}
                            #rq.post(discord_webhook_url, data=message)
                    else:
                        if self.checker(name, colour['name'], size['name']):
                            self.instock.remove([name, colour['name'], size['name']])
        except:
            print('There was an Error')

    def checker(self, product, colour, size):
        # check if item is in list
        for item in self.instock_copy:
            if item == [product, colour, size]:
                self.instock_copy.remove([product, colour, size])
                return True
        return False

    def monitor(self):
        while True:
            self.scrape_main_site()
            self.instock_copy = self.instock.copy()
            for cat in self.pages:
                for i in cat:
                    for j in cat[i]:
                        self.scrape_item_site(j['name'], j['id'])


if __name__ == '__main__':
    t0 = time.time()
    discord_webhook_url = ''
    test = SupremeMonitor()
    test.monitor()
    t1 = time.time()
    print('Time Taken: ', t1 - t0)

