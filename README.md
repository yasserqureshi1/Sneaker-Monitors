# Sneaker Monitors

*A collection of web monitors that notify of restocks or releases on sneaker related sites through Discord Webhook*

> [!NOTE]  
> No longer updated or supported. Should still work - join my Discord for support [here](https://discord.gg/b6zyJyCQUu).

## About the Project
This project is aimed at providing web-monitors for various sites to the sneaker community for free. 
A monitor is a tool that tracks and alerts about changes on website.
These monitors currently notify if a restock or release occurs via Discord Webhook on popular sneaker releated websites.

Today, competition to purchase sneakers is getting increasingly difficult with resellers using paid automated tools to give them a massive advantage over everyone else.
As such, I have and will continue to develop monitors that will help those members that struggle to finally get the sneakers they want.

*Below is a screenshot of the SNKRS monitor in action...*

<p align="center">
  <img width="300" src="https://github.com/yasserqureshi1/Sneaker-Monitors/blob/master/static/SNKRS_example.png?raw=true">
</p>

## Monitors 

Currently the sites that have monitors are:
- All Shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS (Supports 42 countries - see the associated README file)
- Nike
- Footsites (Footlocker UK, US and AU)
- Ssense
- Zalando (UK)
- Off-Spring (UK)
- Snipes
- Sivasdescalzo

## Basic Steps

Youtube Link [here](https://youtu.be/wlhAtpUxLF4).

1. Clone or Download the repository
    - Clone:
    ```
    git clone https://github.com/yasserqureshi1/Sneaker-Monitors.git
    ```
    - Download: Click on the green `Code` button and click on `Download ZIP`. Then unzip this folder
    

2. Install Dependencies
    - Ensure you have [Python 3+](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/) installed. 
    - To install the dependencies, navigate to the cloned directory in Terminal or Command Prompt and use the command:
```
pip install -r requirements.txt
```

3. Configure the monitor you want to run by editting the `config.py` file within that folder.

4. To start the monitor, you should run the `monitor.py`file. You can use the following command:
  ```
  python monitor.py
  ```
**NOTE:** The script needs to be running continuously for it to keep monitoring websites. As such, you should host it on a server. I have a YouTube tutorial on this [here](https://youtu.be/nmUSSlt4JKk). However, I suggest testing this out on your PC before using a server.


## License

Distributed under the GNU General Public License v3.0 License. See ```LICENSE``` for more information. Selling this code without my consent is strictly prohibited. If sharing this or an updated copy of this repo requires this repo to be made freely available.
