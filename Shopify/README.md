# Sneaker Monitors: Shopify 

There are three scripts in this directory:
1. ShopifyMonitor.py    - this monitors an entire page
2. ShopifyMonitor_Specific.py - this monitors a specific product (still in-progress)
3. PalaceMonitor.py - an example of a Shopify store set-up

### Using the Shopify Monitors

These monitors require you to find the json webpage with all the products listed.
We would start by locating the path we want to monitor.

For example, for the Hanon Shop, if we want to monitor new items, we would go to the following address: ```https://www.hanon-shop/collections/whats-new```.
To get all the items on this page in a json format, we add ```/products.json``` at the end.
This gives us the following address: ```https://www.hanon-shop/collections/whats-new/products.json```.

Change and add that as the url at the bottom of the script for any path on a Shopify store.

