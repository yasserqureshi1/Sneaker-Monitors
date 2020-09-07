# Sneaker Monitors
A collection of web monitors that notify of restocks or updates on sneaker related sites through Discord Webhook.

If you have any requests for sites, please let me know via Discord at @TheBrownPanther2#3801

## Installation
The following modules are required:
```
requests
json
time
datetime
```

## Introduction

This repo contains different monitors to various sites to notify if a restock or update occurs via Discord Webhook. A list of all the sites are detailed below:
- All shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS

## How to Use

These scripts should be running continuously for the monitor to work. As such you will need to host it on a server. Personally, I use AWS, but nevertheless, there are tonnes out there. 

Below are details on how to use each of the monitors:

### Shopify Monitor
The following steps are needed:
1. Insert a name for your bot on line 64
2. Insert an image url for your bots avatar on line 65 (optional)
3. Insert the Discord Server's webhook url on line 119
4. Inset the url of the website you want to scrape. Note that the url should point to a .json file in a given category (e.g. myshop.com/collections/whats-new/products.json)

### Supreme
The following steps are needed:
1. Insert a name for your bot on line 25 (default is 'Supreme Monitor')
2. Insert an image url for your bots avater on line 26 (default is the Supreme logo)
3. Insert the Discord Server's webhook url on line 107

### Nike SNKRS
*Work in progress*

## Need to Do

The SNKRS monitor still needs some work with the Discord webhook. 