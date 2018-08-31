import cv2
import os
import time
import sys

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

def main(*args):

    while True:
        print("Searching Amino video logo \n")
        while True:
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
                ADB.tap(MPx,MPy)
                time.sleep(5)
                try:
                    output = ADB.shell("dumpsys activity com.fyber.ads")
                    pid = output.split("pid=",1)[1].split("\n", 1)[0]
                except Exception as e:
                    print("Couldn't find the add process, match is incorrect")
                    break
                print("Waiting 60 seconds for the ad to pass...")
                time.sleep(55)  # Not really 60 seconds, because we already waited 5 seconds to check the ad process
                break
            time.sleep(2)

        try:
            output = ADB.shell("dumpsys activity com.fyber.ads")
            pid = output.split("pid=",1)[1].split("\n", 1)[0]   # Split to only get the pid# Split to only get the pid
            print("Ad pid : " + pid)
            print("Killing ad")
            ADB.shell("su -c kill " + pid)
            time.sleep(5)
        except Exception as e:
            print("Couldn't find the add process, assuming we didn't find the ad button")

if __name__ == '__main__':
    main(*sys.argv)
