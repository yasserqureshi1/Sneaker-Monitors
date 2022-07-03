<figcaption>Logo developed by <a href="https://www.instagram.com/bri.illustratesz/">@bri.illustratesz</a></figcaption>
<p align="center">
  <a href="https://github.com/yasserqureshi1/Sneaker-Monitors/">
    <img src="https://raw.githubusercontent.com/yasserqureshi1/Sneaker-Monitors/master/static/logo.png" alt="Logo" width="auto" height="128">
  </a>
  
  <h3 align="center">Sneaker Monitors</h3>

  <p align="center">
    A collection of web monitors that notify of restocks or updates on sneaker related sites through Discord Webhook
    <br />
    <a href="https://github.com/yasserqureshi1/Sneaker-Monitors/">Report Bug</a>
    ·
    <a href="https://github.com/yasserqureshi1/Sneaker-Monitors/">Request Feature</a>
  </p>

  <p align="center">
    <a href="https://www.paypal.com/donate?hosted_button_id=SKRAD2YFGZC5C">
    <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Logo" width="auto" height="50" >
  </a>
  </p> 
</p>
<br />

Please **star** this repository to increase the awareness of the project for others to use or add to. 

Check out the docs [here](https://yasserqureshi1.github.io/Sneaker-Monitors/)

Join my Discord Server for code, sneakers and everything in-between! Join [here](https://discord.gg/kWmAqpUtrf)


## About the Project
This project is aimed at providing web-monitors for various sites to the sneaker community for free. 
The monitors currently notify if a restock or release occurs via Discord Webhook.
Today, competition to purchase sneakers is getting increasingly difficult with resellers using paid automated tools to give them a massive advantage over everyone else.
As such, I have and will continue to develop monitors that will help those members that struggle to finally get the sneakers they want.

This project is continually expanding, and I would greatly appreciate any contributions. 
When contributing please fork the project and open a Pull Request.

However, due to popular demand, I am developing a paid (but competitively priced) set of hosted monitors. These will be released on my Discord Server that you can join in [#Contact](#Contact).

*Below is a screenshot of the SNKRS monitor in action...*

<p align="center">
  <img width="300" src="https://github.com/yasserqureshi1/Sneaker-Monitors/blob/master/static/SNKRS_example.png?raw=true">
</p>

## Contents
* [About the Project](#about-the-project)
* [Monitors](#monitors)
* [Set Up](#set-up)
* [Issues](#issues)
* [License](#license)
* [Contact](#contact)

## Monitors 

Currently the sites that have monitors are:
- All Shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS (Supports 42 countries - see the associated README file)
- Footsites (Footlocker UK, US, CA and AU)
- Ssense
- Zalando (UK)
- Off-Spring (UK)
- Snipes

## Basic Steps

Click on the image below to watch a YouTube tutorial on setting up the monitors...

[![Watch the video](https://img.youtube.com/vi/BECxMuBFnQA/mqdefault.jpg)](https://youtu.be/BECxMuBFnQA)

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

3. Run the Python file. You can use the following command:
  ```
  python sneaker-monitors.py
  ```

4. Configure the monitors before attempting to run them by navigating through the CLI

5. Run the monitors using the CLI

**NOTE:** The script needs to be running continuously for it to keep monitoring websites. As such, you should host it on a server. I have a YouTube tutorial on this [here](https://youtu.be/nmUSSlt4JKk). However, I suggest testing this out on your PC before using a server.


## Issues

If you find an issue, please open an issue [here](https://github.com/yasserqureshi1/Sneaker-Monitors/issues/new). 
I will try to respond fairly quickly and try to come up with solution.

I may ask you to provide the log file that is produced by the monitor.
It contains no personal data but may help me diagnose where the issue arises.


## License

Distributed under the MIT License. See ```LICENSE``` for more information.

## Contact

For help join my Discord server [here](https://discord.gg/kWmAqpUtrf), get the 'open source sneaker monitor' role and post an issue in the #issues channel.

