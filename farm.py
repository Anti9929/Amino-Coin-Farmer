import cv2
import os
from pathlib import Path
import random
import sys
import time

# TODO :
# Pretty much done with the wallet check -> Detect if we failed to press the button and went out of the wallet activity
# Possible solution : Check the ad 3 times, then CV2 recognition, if it fails, relaunch wallet activity <- Not possible, adb doesn't allow to start activities and put them in front
# Search how the ads correctly closes (ex: What does the `x` triggers when clicked) <- Probably impossible since ADB doesn't allow to get activties infos
# Maybe find a way to detect when the add is finished <- Same as above I guess

sleep = 7

class ADB(object):

    def shell(s):
        return os.popen("adb shell %s" % s).read()

    def pull(s):
        os.system("adb pull %s" % s)

    def tap(x, y):
        ADB.shell("input tap %d %d" % (x,y))
        print("Taped at %d %d" % (x,y))

    def screencap(name):
        ADB.shell("screencap -p /sdcard/%s.png" % name)
        ADB.pull("/sdcard/%s.png" % name)
        ADB.shell("rm /sdcard/%s.png" % name)
        print("Took screenshot: %s" %  name)


# Check if we are in the wallet
def walletCheck():
    print("Are we in the wallet?")
    output = ADB.shell("dumpsys window windows")
    for l in output.splitlines():
        if "mCurrentFocus" in l:
            if "com.narvii.amino.master/com.narvii.wallet.WalletActivity" in l:
                print("Yes")
                return True
    print("No")
    return False

# Simple check before pressing the `back` key
# Sometime, we go back to the wallet abrutely, and that breaks the loops
# This check try to counter this
def back():
    if not walletCheck():
        print("Pressing `back`")
        output = ADB.shell("input keyevent 4")              # try to use the `back` key
        time.sleep(5)

# Process started when an ad is played
def adHandling():
    output = ADB.shell("dumpsys activity com.fyber.ads")
    pid = output.split("pid=",1)[1].split("\n", 1)[0]
    print("Waiting 60 seconds for the ad to pass...")
    time.sleep(55)  # Not really 60 seconds, because we already waited 5 seconds to check the ad process


def main():
    global sleep
    MPx = None

    if Path('match.txt').is_file():
        print("Apparently, we already know the position of the button\nSkipping button search")
        try:
            fp = open('match.txt', 'r')
            tmp = fp.readline()[1:-1].split(",")
            MPx, MPy = (int(tmp[0]), int(tmp[1]))
            print("Saved button match : " + str(MPx) + "," + str(MPy))
        finally:
            fp.close()

    while True:
        if MPx is not None:
            print("Amino logo already found")       # Why search again when we already know the position
            if walletCheck():
                ADB.tap(MPx + random.randint(0,100),MPy + random.randint(0,10))
                time.sleep(5)
            try:
                adHandling()
            except Exception as e:
                print("Couldn't find the ad process, maybe we were too quick, retrying")
                time.sleep(2)
                if walletCheck():
                    print("Hey! We're still in the wallet! That's bad!")
        else:
            while True:
                print("Searching Amino video logo \n")
                ADB.screencap('screen')
                # Picture comparison part
                # Read the images from the file
                small_image = cv2.imread('sample.png')
                large_image = cv2.imread('screen.png')
                method = cv2.TM_SQDIFF_NORMED       # Method used for the comparison
                result = cv2.matchTemplate(small_image, large_image, method)
                # We want the minimum squared difference
                mn,ma,mnLoc,maLoc = cv2.minMaxLoc(result)
                # Extract the coordinates of our best match
                MPx,MPy = mnLoc
                # Get the size of the template. This is the same size as the match.
                trows,tcols = small_image.shape[:2]
                print("Current match: " + str(ma*100)[:5] + "%")
                if ma >= 0.95:
                    print("Match at " + str(mnLoc))
                    fp = open('match.txt', 'w+')
                    fp.write(str(mnLoc)).close()
                    print("Saved position for future uses")
                    os.remove("screen.png")
                    ADB.tap(MPx + random.randint(0,100),MPy + random.randint(0,10)) # Not tapping exactly on the same pixels each time, more realism
                    time.sleep(5)
                    try:
                        adHandling()
                    except Exception as e:
                        print("Couldn't find the ad process, match may be incorrect")
                        break
                    break
                time.sleep(2)
        back()
        try:
            output = ADB.shell("dumpsys activity com.fyber.ads")
            pid = output.split("pid=",1)[1].split("\n", 1)[0]   # Split to only get the pid# Split to only get the pid
            print("Ad pid : " + pid + "\nKilling the ad if it didn't succeeded")
            ADB.shell("su -c kill " + pid)   # -2 to kill cleanly
            time.sleep(sleep)
        except Exception as e:
            try:
                print("Couldn't find the ad process, maybe a strange Vungle ad")
                output = ADB.shell("dumpsys activity com.vungle.warren.ui.VungleActivity")
                pid = output.split("pid=",1)[1].split("\n", 1)[0]   # Split to only get the pid# Split to only get the pid
                print("Ad pid : " + pid + "\nKilling the ad")
                ADB.shell("su -c kill " + pid)   # -2 to kill *cleanly*
                time.sleep(sleep)
            except Exception as e:
                print("Couldn't find both type of ad process\nEither we didn't find the ad button or we succesfully pressed the `back` key")

    print("We got out of the loop, that's BAD")

if __name__ == '__main__':
    try:
        if(sys.argv[1] is "-c" or "--connect"):
            def warning():          #Pretty sure it's absolutely NOT a good idea to set up a function here
                print("Usage: -c <ip address>(:<port>)\n--connect <ip address>(:<port>)")
                sys.exit(0)

            try:
                s = sys.argv[2]
            except Exception as e:
                warning()
            a = s.split('.')
            if len(a) != 4:
                warning()
            for x in a:
                if not x.isdigit():
                    warning()
                i = int(x)
                if i < 0 or i > 255:
                    warning()
            if("failed" in os.popen("adb connect %s" % s).read()):
                print("Couldn't connect to your android. Please try to use a cable, or specify a port")
                sys.exit(0)
            time.sleep(2)
        main()
    except KeyboardInterrupt:
        print('Interrupted, killing adb')
        os.popen("adb kill-server")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
