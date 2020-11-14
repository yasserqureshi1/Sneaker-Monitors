import requests as rq
import json
import time
import datetime
import urllib3
import logging
import dotenv

logging.basicConfig(filename='SNKRSlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class SNKRSMonitor:
    def __init__(self, webhook, loc, lan, proxy):
        self.url = ['https://api.nike.com/product_feed/threads/v2/?anchor=', f'&count=&filter=marketplace%28{loc}%29&filter=language%28{lan}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title']
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.items = []
        self.number_of_items = 50
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"http": f"http://{proxy}"}

    def scrape_site(self):
        """
        Scrapes SNKRS site and adds items to array
        :return: None
        """
        no_of_pages = self.number_of_items//50
        anchor = 0
        while no_of_pages != 0:
            try:
                html = rq.get(url=self.url[0] + str(anchor) + self.url[1], timeout=5, verify=False, headers=self.headers, proxies=self.proxy)
                output = json.loads(html.text)
                for item in output['objects']:
                    self.items.append(item)
                    logging.info(msg='Successfully scraped SNKRS site')
            except Exception as e:
                print('Error - ', e)
                logging.error(msg=e)
            anchor += 50
            no_of_pages -= 1

    def checker(self, product, colour):
        """
        Determines whether the product status has changed
        :param product: Shoe name
        :param colour: Shoe colour
        :return: None
        """
        for item in self.instock_copy:
            if item == [product, colour]:
                self.instock_copy.remove([product, colour])
                return True
        return

    def discord_webhook(self, title, colour, slug, thumbnail):
        """
        Sends a Discord webhook notification to the specified webhook URL
        :param title: Shoe name
        :param colour: Shoe Colour
        :param slug: Shoe URL
        :param thumbnail: URL to shoe image
        :return: None
        """
        data = {}
        data["username"] = CONFIG['USERNAME']
        data["avatar_url"] = CONFIG['AVATAR_URL']
        data["embeds"] = []
        embed = {}
        embed["title"] = title
        embed["description"] = '*Item restock*\n Colour: ' + str(colour)
        embed["url"] = 'https://www.nike.com/gb/launch/t/' + slug
        embed["thumbnail"] = {'url': thumbnail}
        embed["color"] = int(CONFIG['COLOUR'])
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            logging.error(msg=err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))

    def monitor(self):
        """
        Initiates the monitor
        :return: None
        """
        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        start = 1
        while True:
            self.scrape_site()
            self.instock_copy = self.instock.copy()
            for item in self.items:
                try:
                    for j in item['productInfo']:
                        if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                            if self.checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                                pass
                            else:
                                self.instock.append([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
                                if start == 0:
                                    self.discord_webhook(j['merchProduct']['labelName'], j['productContent']['colorDescription'], j['productContent']['slug'], j['imageUrls']['productImageUrl'])
                                    logging.info(msg='Sending new notification')
                                    time.sleep(1)

                        else:
                            if self.checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                                self.instock.remove([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
                except:
                    pass
                self.items.remove(item)
            start = 0
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings()
    test = SNKRSMonitor(webhook=CONFIG['WEBHOOK'], loc=CONFIG['LOCATION'], lan=CONFIG['LANGUAGE'], proxy=CONFIG['PROXY'])
    test.monitor()
