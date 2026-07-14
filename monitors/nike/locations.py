import requests
import json

___standard_api___ = [
    'GB', 'US', 'AU', 'AT', 'BE', 'BG', 'CA', 'CN', 'HR', 'CZ', 'DK', 'EG',
    'FI', 'FR', 'DE', 'HU', 'IN', 'ID', 'IE', 'IT', 'MY', 'MX', 'MA', 'NL',
    'NZ', 'NO', 'PH', 'PL', 'PT', 'PR', 'RO', 'RU', 'SA', 'SG', 'SI', 'ZA',
    'ES', 'SE', 'CH', 'TR', 'AE', 'VN', 'JP'
]

# The old cic/browse/v2 endpoint now returns 404. Nike serves the same browse
# data from the product wall API. This is a "new arrivals" feed (men's shoes),
# so we notify when a product first appears (dedupe on style code / productCode).
CONSUMER_CHANNEL_ID = 'd9a5bc42-4b9c-4976-858a-f159cf99c647'
WALL_PATH = '/w/mens-shoes-nik1zy7ok'  # Nike men's shoes; change to watch a different category
MAX_PAGES = 5


def standard_api(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9',
        'nike-api-caller-id': 'nike:snkrs:web:1.0',
        'origin': 'https://www.nike.com',
        'referer': 'https://www.nike.com/',
        'user-agent': user_agent,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

    to_discord = []

    next_url = (f'https://api.nike.com/discover/product_wall/v1/marketplace/{LOCATION}'
                f'/language/{LANGUAGE}/consumerChannelId/{CONSUMER_CHANNEL_ID}'
                f'?path={WALL_PATH}&anchor=0&count=24')

    pages = 0
    while next_url and pages < MAX_PAGES:
        html = requests.get(url=next_url, timeout=20, headers=headers, proxies=proxy)
        output = json.loads(html.text)

        for grouping in output.get('productGroupings', []):
            for product in (grouping.get('products') or []):
                try:
                    title = product['copy']['title']
                    code = product['productCode']
                except (KeyError, TypeError):
                    continue

                if KEYWORDS != [] and not any(key.lower() in title.lower() for key in KEYWORDS):
                    continue

                if code in ITEMS:
                    continue

                # New product - store it, and notify unless this is the first scrape
                ITEMS.append(code)
                if start == 0:
                    to_discord.append(dict(
                        title=title,
                        colour=product.get('displayColors', {}).get('colorDescription', ''),
                        url=product['pdpUrl']['url'],
                        thumbnail=product.get('colorwayImages', {}).get('squarishURL', ''),
                        price=str(product.get('prices', {}).get('currentPrice', '')),
                        style_code=code
                    ))

        nxt = (output.get('pages') or {}).get('next')
        next_url = ('https://api.nike.com' + nxt) if nxt else None
        pages += 1

    return to_discord
