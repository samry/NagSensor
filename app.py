#!/usr/bin/python
import time
import os
import glob
import sys
import argparse

# extended from https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino
import threading
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0

class Pulsesensor:
    def __init__(self, channel = 0, bus = 0, device = 0):
        self.channel = channel
        self.BPM = 0
        self.adc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    def getBPMLoop(self):
        # init variables
        rate = [0] * 10         # array to hold last 10 IBI values
        sampleCounter = 0       # used to determine pulse timing
        lastBeatTime = 0        # used to find IBI
        P = 512                 # used to find peak in pulse wave, seeded
        T = 512                 # used to find trough in pulse wave, seeded
        thresh = 525            # used to find instant moment of heart beat, seeded
        amp = 100               # used to hold amplitude of pulse waveform, seeded
        firstBeat = True        # used to seed rate array so we startup with reasonable BPM
        secondBeat = False      # used to seed rate array so we startup with reasonable BPM

        IBI = 600               # int that holds the time interval between beats! Must be seeded!
        Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat". 
        lastTime = int(time.time()*1000)
        
        while not self.thread.stopped:
            Signal = self.adc.read_adc(self.channel)
            currentTime = int(time.time()*1000)
            
            sampleCounter += currentTime - lastTime
            lastTime = currentTime
            
            N = sampleCounter - lastBeatTime

            # find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3:     # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T:                          # T is the trough
                    T = Signal                          # keep track of lowest point in pulse wave 

            if Signal > thresh and Signal > P:
                P = Signal

            # signal surges up in value every time there is a pulse
            if N > 250:                                 # avoid high frequency noise
                if Signal > thresh and Pulse == False and N > (IBI/5.0)*3:       
                    Pulse = True                        # set the Pulse flag when we think there is a pulse
                    IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
                    lastBeatTime = sampleCounter        # keep track of time for next pulse

                    if secondBeat:                      # if this is the second beat, if secondBeat == TRUE
                        secondBeat = False;             # clear secondBeat flag
                        for i in range(len(rate)):      # seed the running total to get a realisitic BPM at startup
                          rate[i] = IBI

                    if firstBeat:                       # if it's the first time we found a beat, if firstBeat == TRUE
                        firstBeat = False;              # clear firstBeat flag
                        secondBeat = True;              # set the second beat flag
                        continue

                    # keep a running total of the last 10 IBI values  
                    rate[:-1] = rate[1:]                # shift data in the rate array
                    rate[-1] = IBI                      # add the latest IBI to the rate array
                    runningTotal = sum(rate)            # add upp oldest IBI values

                    runningTotal /= len(rate)           # average the IBI values 
                    self.BPM = 60000/runningTotal       # how many beats can fit into a minute? that's BPM!

            if Signal < thresh and Pulse == True:       # when the values are going down, the beat is over
                Pulse = False                           # reset the Pulse flag so we can do it again
                amp = P - T                             # get amplitude of the pulse wave
                thresh = amp/2 + T                      # set thresh at 50% of the amplitude
                P = thresh                              # reset these for next time
                T = thresh

            if N > 2500:                                # if 2.5 seconds go by without a beat
                thresh = 512                            # set thresh default
                P = 512                                 # set P default
                T = 512                                 # set T default
                lastBeatTime = sampleCounter            # bring the lastBeatTime up to date        
                firstBeat = True                        # set these to avoid noise
                secondBeat = False                      # when we get the heartbeat back
                self.BPM = 0

            time.sleep(0.005)
            
        
    # Start getBPMLoop routine which saves the BPM in its variable
    def startAsyncBPM(self):
        self.thread = threading.Thread(target=self.getBPMLoop)
        self.thread.stopped = False
        self.thread.start()
        return
        
    # Stop the routine
    def stopAsyncBPM(self):
        self.thread.stopped = True
        self.BPM = 0
        return

# parser = argparse.ArgumentParser(description='A heartbeat sensor-optimized Nagios plugin for the PulseSensor.com pulse sensor and the MCP3008 ADC')
# parser.add_argument('-w', '--warning', type=float, required=True, help='A BPM rate of 120 or greater')
# parser.add_argument('-c', '--critical', type=float, required=True, help='A BPM rate of 160 or greater')
# parser.add_argument('--version', action='version', version='version 0.1')

# load the pulse sensor module
p = Pulsesensor()
# start getBPMLoop routine which saves the BPM in its variable
p.startAsyncBPM()

# low threshold, if heartrate is under these numbers send out a warning
warning_low_threshold = 45
critical_low_threshold = 35
# high threshold, if heartrate is over these numbers send out a warning
warning_high_threshold = 120
critical_high_threshold = 160

# try:
#     args = parser.parse_args()
# except:
#     print 'Unexpected command line input'
#     sys.exit(3)

while True:
    print bpm
    bpm = p.BPM
    if bpm > 0:
        #print("BPM: %d" % bpm)
        # low threshold
        if bpm < warning_low_threshold:
            print 'Warning: Low Heartbeat ',(bpm),' | ',(bpm)
            # sys.exit(1)
        elif bpm > warning_high_threshold:
            print 'Warning: High Heartbeat ',(bpm),' | ',(bpm)
            # sys.exit(1)
        elif bpm > critical_high_threshold:
            print 'Critical: High Heartbeat ',(bpm),' | ',(bpm)
            # sys.exit(2)
        elif bpm < critical_low_threshold:
            print 'Critical: Low Heartbeat ',(bpm),' | ',(bpm)
            # sys.exit(2)
    else:
        print("No Heartbeat found")
    time.sleep(1)