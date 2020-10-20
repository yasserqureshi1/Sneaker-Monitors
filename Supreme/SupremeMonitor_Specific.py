import requests as rq
import json
import time


class SupremeMonitor:
    def __init__(self, item_id, colour, size):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.instock = []
        self.instock_copy = []
        self.id = item_id
        self.colour = colour
        self.size = size

    def scrape_main_site(self):
        s = rq.Session()
        try:
            html = s.get('https://www.supremenewyork.com/shop/' + str(self.id) + '.json', headers=self.headers, verify=False, timeout=1)
            output = json.loads(html.text)['styles']
            return output
        except:
            print('There was an Error')

    def checker(self, colour, size):
        # check if item is in list
        for item in self.instock_copy:
            if item == [colour, size]:
                self.instock_copy.remove([colour, size])
                return True
        return False

    def monitor(self):
        while True:
            output = self.scrape_main_site()
            self.instock_copy = self.instock.copy()
            for colour in output:
                if colour['name'] == self.colour or self.colour == 'NA':
                    for size in colour['sizes']:
                        if size['name'] == self.size or self.size =='NA':
                            if size['stock_level'] == 1:
                                if self.checker(colour['name'], size['name']):
                                    pass
                                else:
                                    self.instock.append([colour['name'], size['name']])
                                    restock = 'RESTOCK: ' + str(self.id) + ' in ' + str(colour['name']) + ' in size ' + str(
                                        size['name'])
                                    print(restock)
                            else:
                                if self.checker(colour['name'], size['name']):
                                    self.instock.remove([colour['name'], size['name']])


if __name__ == '__main__':
    test = SupremeMonitor(305180, 'Black', 'NA')
    test.monitor()
