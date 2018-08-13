from pulsesensor import Pulsesensor
import time
import os
import glob
import sys
import argparse

# load the pulse sensor module
p = Pulsesensor()
# start getBPMLoop routine which saves the BPM in its variable
p.startAsyncBPM()

low_threshold = 50
high_threshold = 150

try:
    while True:
        print bpm
        bpm = p.BPM
        if bpm > 0:
            #print("BPM: %d" % bpm)
            # low threshold
            if bpm < low_threshold:
                print 'Low Heartbeat ',(bpm),' | ',(bpm)
                sys.exit(2)
            elif bpm > high_threshold:
                print 'High Heartbeat ',(bpm),' | ',(bpm)
                sys.exit(2)
        else:
            print("No Heartbeat found")
        time.sleep(1)
except:
    p.stopAsyncBPM()