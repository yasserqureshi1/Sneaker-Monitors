# SHOPIFY NOTES 

The Shopify monitor is able to work when given a particular site. The URL that you provide must be a `products.json` file.


To find the `products.json` file, start by locating the path we want to monitor.

For example, for the Hanon Shop, if we want to monitor new items, we would go to the following address: ```https://www.hanon-shop/collections/whats-new```.
To get all the items on this page in a JSON format, we add ```/products.json``` at the end.
This gives us the following address: ```https://www.hanon-shop/collections/whats-new/products.json```.

Place this URL within the `DETAILS` section when configuring the monitors.

