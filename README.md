# Amino Coin farmer
__You cannot use this script if your Android device is not rooted, and if don't have busybox installed__

To use this script, you'll need to :

1. Install adb on your system
    * On linux, simply use `sudo apt-get install android-tools` or `sudo yum install android-tools`
    * On windows, get `adb.exe`, `AdbWinApi.dll` and `AdbWinUsbApi.dll` and put them next to the script

2.Install the necessary libraries using `pip install -r requirements.txt` (of course, you'll need python 3)

3.If you haven't already, go to the developpements settings of your phone/tablet, and enable Android Debug Bridge (ADB)

4.You should be ready to launch this script, now simply go to the Wallet screen of the Amino app, start the script (`python farm.py`), and let the coins rain

A `screen.png` file should temporarily appear when running the script for the first time. It is simply used to find the correct button to press.

Once the button is found, this script will save a `match.txt` file. This file simply contain the coordinates of the button that were found the first time you ran the script. If you change your device, remove this file, and the script will search the button again, to adapt to your new device.
