# DMMGamePlayerFastLauncher

DMM Game Player Fast Launcher for secure and fast start-up

![img.shields.io](https://img.shields.io/github/downloads/fa0311/DMMGamePlayerFastLauncher/total)

[日本語](/README.md) / [English](/README-en.md)

[Detailed instructions(Japanese)](/docs/README-advance.md)

## Features

- **One click to launch the game**
- **Run with minimal privileges**
- **Do not send hardware information to DMM**

## Installation

Download `DMMGamePlayerFastLauncher-Setup.exe` from [Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases)
Run and set up

## Using

Run `DMMGamePlayerProductIdChecker.exe` in `%AppData%\DMMGamePlayerFastLauncher\tools`
Note down the `product_id` of the game you want to activate

![screenshot1](docs/img/DMMGamePlayerProductIdChecker1.png)

Right-click in Explorer or on the desktop and select **New**, **Shortcut**  
Enter the **DMMGamePlayerFastLauncher path** and `product_id` in **Type the location of the item**

Examples:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume`  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner`

**Type a name for this shortcut** can be anything

Then just double-click the shortcut to run it

## Receive update notifications

Notify me when there are updates to this tool

![screenshot1](docs/img/subscribe1.png)
![screenshot1](docs/img/subscribe2.png)

## Source

[Lutwidse/priconner_launch.py](https://gist.github.com/Lutwidse/82d8e7a20c96296bc0318f1cb6bf26ee)
[kira-96/Inno-Setup-Chinese-Simplified-Translation](https://github.com/kira-96/Inno-Setup-Chinese-Simplified-Translation)

## License

DMMGamePlayerFastLauncher is under MIT License
