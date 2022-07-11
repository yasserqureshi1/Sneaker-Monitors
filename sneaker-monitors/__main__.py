from pyfiglet import  figlet_format
import six
import os
import subprocess
import ctypes
import traceback
try:
    from termcolor import colored
except ImportError:
    colored = None
import time

from db import create_config_db, get_config, update_config, get_all_config, columns

from __init__ import __version__, __author__, __monitors__


def clear():
    if os.name in ("nt", "dos"):
        ctypes.windll.kernel32.SetConsoleTitleW(f"SNEAKER MONITORS [v{__version__}] - Created by {__author__}")
        os.system("cls")
    elif os.name in ("linux", "osx", "posix"): os.system("clear")
    else: print("\n") * 100


def log(text, colour, font='slant', figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(text, colour))
        else:
            six.print_(colored(figlet_format(
                text, font=font), colour))
    else:
        six.print_(text)

def python_os():
    if os.name in ("nt", "dos"):
        return 'python'
    elif os.name in ("linux", "osx", "posix"): 
        return 'python3'
    else:
        return 'python'


def configure(monitor):
    clear()
    log(F' ***** CONFIGURE {monitor.upper()} *****', colour='green')
    items = get_config(monitor)
    log(f'Type in the value you want for... ', colour='blue')
    log('If you want to keep the current value, just hit ENTER', colour='blue')
    log('If you want to keep the field empty, type "null"', colour='blue')
    inputs = []
    for index, column in enumerate(columns):
        log(f' CURRENT VALUE OF {column.upper()} = {items[index+1]}', colour='blue')
        value = input('NEW VALUE: ')
        if value == "":
            inputs.append(None)
        else:
            inputs.append(str(value))
    log('* UPDATING... *', colour='blue')
    update_config(monitor, inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], inputs[7], inputs[8])
    log('* UPDATED *', colour='blue') 
    log('Going back...', colour='blue')
    time.sleep(1)
    configure_screen()


def get_monitor(index):
    return __monitors__[int(index)].lower()


def get_monitor_path(index):
    return os.path.realpath(get_monitor(index)+'/monitor.py')


def monitor_command(command):
    os.system(command)


def run_monitor(path):
    subprocess.run(path, shell=True)


def run_screen():
    clear()
    log('Select the monitor(s) you want to run. To run multiple, list them with spaces (Example: 1 5 6 7), but note that running too many monitors at once may harm your computer. It is suggested a maximum of 4 monitors to be used at one time, but different systems may be able to handle more or less.', colour='green')
    for i, m in enumerate(__monitors__):
        log(f'    [{i}] {m}', colour='blue')
    log(f'    [{i+1}] Back', colour='blue')
    log('Type the option(s) here: ', colour='green')
    monitor_options = input().split(' ')

    try:
        if str(int(i)+1) in monitor_options:
            main()

        commands = ''
        start = 0
        for m in monitor_options:
            if start == 0:
                commands+=f'{python_os()} {os.path.abspath(f"sneaker-monitors/monitors/{get_monitor(m)}/monitor.py")}'
                start = 1
            else:
                commands+=f' & {python_os()} {os.path.abspath(f"sneaker-monitors/monitors/{get_monitor(m)}/monitor.py")}'

        print(commands)
        clear()
        log('--- RUNNING ---', colour='blue')
        subprocess.run(commands, shell=True)

    except:
        print(traceback.format_exc())
        log('Something went wrong. Please check the input... ', colour='red')
        time.sleep(2)
        run_screen()


def configure_screen():
    clear()
    log('Select the monitor you want to configure.', colour='green')
    for i, m in enumerate(__monitors__):
        log(f'    [{i}] {m}', colour='blue')
    log(f'    [{i+1}] View all configurations', colour='blue')
    log(f'    [{i+2}] Back', colour='blue')
    log('Type the option here: ', colour='green')
    monitor_option = input()

    if str(int(i)+1) in monitor_option:
        clear()
        log(' ** ALL CONFIGURATIONS **', colour='green')
        items = get_all_config()
        print('MONITOR NAME | WEBHOOK | USERNAME | AVATAR URL | COLOUR | DELAY | KEYWORDS | PROXIES | FREE PROXIES | DETAILS')
        for i in items:
            print(i)

        if type(input()) == type(""):
            configure_screen()

    # Go back
    if str(int(i)+2) in monitor_option:
        main()

    try:
        monitor = get_monitor(monitor_option)
        configure(monitor)

    except:
        log('Something went wrong. Please check the input... ', colour='red')
        time.sleep(2)
        configure_screen()
    

def main():
    create_config_db()
    clear()
    log('Sneaker Monitors', colour='red', figlet=True)
    log('Created by GitHub:yasserqureshi1   Discord:TheBrownPanther2#8491', colour='yellow')
    log('Choose option: ', colour='green')
    log('    [1] Run Monitors', colour='blue')
    log('    [2] Configure Monitors', colour='blue')
    log('    [3] Help', colour='blue')
    log('    [4] Exit', colour='blue')
    print('')
    log('Type option value here: ', colour='green')

    option = input()
    if option == '1':
        # Run Monitors
        run_screen()

    elif option == '2':
        configure_screen()

    elif option == '3':
        clear()
        log(' ***** HELP *****\n', colour='green')
        log('You can follow along to YouTube tutorials at:', colour='blue')
        log('https://www.youtube.com/c/yascode\n',colour='green')
        log('You can find documentation at the following link:', colour='blue')
        log('https://yasserqureshi1.github.io/Sneaker-Monitors/\n', colour='green')  # Link to documentation
        log('You can join the Discord server for more help here:', colour='blue')
        log('https://discord.gg/kWmAqpUtrf\n', colour='green')  # Link to discord server
        log('\n\nPress any button to go back.', colour='yellow')
        if type(input()) == type(""):
            main()

    elif option == '4':
        clear()
        exit()
    
    else:
        log('Invalid option. Please try again in...', colour='red')
        time.sleep(1)
        log('3', colour='red')
        time.sleep(1)
        log('2', colour='red')
        time.sleep(1)
        log('1', colour='red')
        main()

if __name__ == '__main__':
    main()