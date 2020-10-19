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
urllib3
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
Take the following steps to work the monitor:
1. Insert a name for your bot on line 64
2. Insert an image url for your bots avatar on line 65 (optional)
3. Insert the Discord Server's webhook url on line 119
4. Inset the url of the website you want to scrape. Note that the url should point to a .json file in a given category (e.g. myshop.com/collections/whats-new/products.json)

### Supreme
Take the following steps to work the monitor:
1. Insert a name for your bot on line 25 (default is 'Supreme Monitor')
2. Insert an image url for your bots avatar on line 26 (default is the Supreme logo)
3. Insert the Discord Server's webhook url on line 107

### Nike SNKRS (EU)
Take the following steps to work the monitor:
1. Insert a name for your bot on line 50 (default is 'Nike SNKRS EU Bot')
2. Insert an image url for your bots avatar on line 51 (default is Nike Logo)
3. Insert the Discord Server's webhook url on line 98

## Example Set-Up with AWS 

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html

This requires you to have an account with AWS. Navigate to the `Console`, and click on the `Services` menu.
Under the `Compute` heading, select `EC2`.
From here, we will create our instance. 
Select the `Launch Instance` button. 
You will be taken to a page with a list of instances to choose from.
We will be focusing on the 'free Tier'. 
Lets choose the `Ubuntu Server 18.04 LTS (HVM), SSD Volume Type`. 
The next page will ask you to choose an instance type - it should already have the Free Tier option selected which is what we will use.
The next page will ask you to Review - click `Launch`. 

We then need to create a Key Pair for our instance. 
So for the first dropdown menu select `Create a new key pair`. 
Then name it anything you want. 
Then you should download this key pair and store it somewhere safe and accessible.
This will be used to access your virtual machine.

Now depending on your OS, there are different ways of accessing this instance.
Below are a few ways

**Windows:**

There are a few options:
- Use PuTTY
- SSH Client

**Mac/Linux:**

The options include:
- SSH Client
- EC2 Instance Connect

I use PuTTY. 
We also need a file transfer system, to upload your code to the instance.
I use FileZilla.

Upload your files to your instance using FileZilla. 
Then using PuTTY, type the following command to install Python:
```
$ sudo apt install python3-pip
```

Then using pip, install the packages needed:
```
$ pip3 install [package name]
```

Once everything is done, we can run our code. 
Firstly, we want it to run continuously. 
As such, we type in the command, where we can have multiple sessions on a single screen instance:
```
$ screen
``` 

Then run the code:
```
$ python3 [name of script].py
```

To disconnect from the screen, but leave it running, press ``CTRL A + D``.
Now you can close the window, and the code should be running!


## Need to Do

- The ShopifyMonitor_Specific.py is a work in progress. This will be a more accessible Shopify monitor which will work on more shopify sites.
- SupremeMonitor_Specific.py needs to be fully tested
