# FAQs for Sneaker Monitors

## 1. Can I monitor multiple Shopify sites in the same Python file?
No. You will need to duplicate the Shopify folder and have seperate links in each .env file. 
This is a better monitoring solution than iterating through a list of URLs because iterating through a list introduces new delays that will reduce the speed of the monitor dramatically.

## 2. I get a red error saying "ERROR: Could not build wheels for multidict which use PEP 517 and cannot be installed directly". What do I do?
You need to install the visual c++ build tools. You can do this through the following link: https://visualstudio.microsoft.com/visual-cpp-build-tools/

## 3. I get a message saying PIP is not a known command.
This means you do not have pip installed on your system. This website details how to install pip: https://pip.pypa.io/en/stable/installing/

Essentially first you need to download pip using the command in Terminal or Command Prompt:
```curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py```

Then navigate to the directory in which it is downloaded (should be downloaded in the directory already open) and depending on your system, run the specific command:

Windows: ```py get-pip.py```
Unix/Mac: ```python get-pip.py```
There is a lot of documentation and many YouTube tutorials that cover this.

## 4. I get an error saying "ModuleNotFound: No module named ..."
This means you have not installed the dependencies. Please install these using the command:
```pip install -r requirements.txt```

## 5. I'm having issues with pip.
If you've installed it and are still having issues, ensure that it is in your PATH. This link should help: https://datatofish.com/add-python-to-windows-path/

## 6. How do I open the .env file?
You can use notepad or any text editor.

## 7. I can't see the .env files.
For Windows users:
https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-10-97fbc472-c603-9d90-91d0-1166d1d9f4b5

For Mac Users:
https://www.macworld.co.uk/how-to/show-hidden-files-mac-3520878/

