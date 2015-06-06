#! /usr/bin/env python
# Filename: odroidw_meter.py
# -*- coding: utf-8 -*-
"""Smart meter application module for Odroid W.

Setup Description
#################

This application module utilizes the external 12-bit MCP3208 ADC
connected to the Odroid W via SPI to be used as a real-time 
smart-power-meter. Current clamps in series with burden resistors
are connected to the input channels of the MCP3208. The MCP3208 is
connected to the GPIO port of the W using the following configuration:

    MCP3208
    +------+
CH0 |1   16| V_DD      -->    3V3 (Pin 1)
CH1 |2   15| V_REF     -->    3V3 (Pin 1)
CH2 |3   14| AGND      -->    GND (Pin 6)
CH3 |4   13| CLK       -->    SCLK (Pin 23)
CH4 |5   12| D_OUT     -->    MISO (Pin 21)
CH5 |6   11| D_IN      -->    MOSI (Pin 19)
CH6 |7   10| CS/SHDN   -->    CE0 (Pin 26)
CH7 |8    9| DGND      -->    GND (Pin 6)
    +------+

Method of Operation
###################

Current transducers (clamps) are used to measure AC currents. 
An AC current in the primary winding of the transducer produces an
alternating magnetic field in the core, which then induces an
alternating current in the secondary winding circuit. A burdon resistor
, which is connected in series within this circuit, converts the
current into a proportional voltage. This voltage is measured by the
ADC and send via SPI to the W.

The goal is to identify the amplitude of each phase as precisely as
possible to determine the power consumption in 60Hz intervals (mains
frequency). Assuming a constant grid voltage, current can be translated 
into power. 

The amplitude of each phase is identified, measured, and 
submitted to a remote server via http get requests. 
Assuming a constant grid voltage, the current is translated to power.
The remote server analyzes the submitted data (int) and saves
it into a mysql database.

This module makes use of threading to enable data collection while
http requests are sent.

Dependencies
############

The following third-party packages are needed:
    #. **spidev**
       Python bindings for Linux SPI access through spidev::
           
           git clone git://github.com/doceme/py-spidev
	   cd py-spidev/
	   sudo python setup.py install

        This install requires:
            
            sudo apt-get install python-dev

This packages if needed if internal 10-bit ADC of C1 has to be accessed
or for other GPIO functionality:
    #. **wiringpi2**
       A python interface to WiringPi 2.0 library for easy interfacing 
       with GPIO pins of Odroid C1/ Raspberry Pi. Also supports i2c and
       SPI::
       
           git clone https://github.com/Gadgetoid/WiringPi2-Python.git
	   cd WiringPi2-Python
	   sudo python setup.py install 

Module
######

Attributes:
    average (list): dynamic storage space for current amplitudes   
"""

import spidev
import wiringpi2
import thread
import time
import datetime
import threading
from threading import Thread, enumerate
from urllib import urlopen
from time import sleep
import pygame
import os
import numpy

__author__ = "vschw"
__copyright__ = "Copyright 2015, University of Hawaii at Manoa"
__credits__ = ["Reza Ghorbani"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "vschw"
__email__ = "volkers@hawaii.edu"
__status__ = "alpha"

average = [],[]
UPDATE_INTERVAL = 0.0001


def init_wiringpi2():
    """Enables wiringPi2 on Odroid C1.
    
    This function enables access to all GPIOs of the C1.
    Furthermore, both analog (ADC) ports are opened.
    """ 
        
    wiringpi2.wiringPiSetup()
    pass
  
def init_spidev():
    """Enables spidev on Odroid C1.
    
    This function enables access SPI on the C1 utilizing
    spidev0.0 from the kernel driver.
    """ 
    
    global spi   
    spi = spidev.SpiDev()
    spi.open(0,1)
    
def init_tft():
    os.environ["SDL_FBDEV"] = "/dev/fb1"
    os.environ['SDL_VIDEODRIVER']="fbcon"
    global screen

    pygame.init()
    pygame.mouse.set_visible(0)
    size = width,height = 320,240
    screen = pygame.display.set_mode(size)

def bit_to_power(bit, **kwargs):
    """Converts ADC bits to power in Watt
        
    Args:
        bit (int): Input from ADC port in bit.
	**kwargs: ADC precision and power conversion factor (int).
	
    Returns:
        Power in Watt (int).
    """  
    
    conversion = kwargs.get('conversion', 1600)
    precision = kwargs.get('precision', 4096)
    return [int(bit[0] * conversion / precision), int(bit[1] * conversion / precision)]

def average_bit():
    """Returns average bit value of current 'average'-list.
   
    Returns:
        Average of "average" list (float).
    """ 
    
    global average    
    if average[0] and average[1]:
	return [sum(average[0]) / float(len(average[0])), sum(average[1]) / float(len(average[1]))]
    elif average[0] and not average[1]:
        return [sum(average[0]) / float(len(average[0])), 0]
    elif average[1] and not average[0]:
        return [0, sum(average[1]) / float(len(average[1]))]
    else:
	return [0, 0]

def send_http_get(power, sleeptime):
    """Returns average bit value of current 'average'-list.
  
    Args:
        power (int): average power since last send event.
	sleeptime (float): time interrupt to reduce server load. 
	  
    Returns:
        Average of "average" list (float).
    """ 
    
    global average
    timenow = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-4])
   
    sites = ['http://redlab.colo.hawaii.edu/dirgtrams+'+str(power[0])+'+'+str(power[1])+    '+'+str(timenow)]
    print sites
    average = [],[]
    multi_get(sites,timeout=1)
    time.sleep(sleeptime)
    print 'data submitted: ' + str(power) + 'W, list length: ' + str(len(average[0]))
    #display_power(power)

def http_get_thread(d, **kwargs):
    conversion = kwargs.get('conversion', 1600)
    precision = kwargs.get('precision', 4096)   
    sleeptime = kwargs.get('sleeptime', 0.5) 
    while True:	   
        power = bit_to_power(average_bit(), precision = precision, conversion = conversion)
	send_http_get(power, sleeptime) 

def adcread_C1(**kwargs):
    adc_port = kwargs.get('adc_port', 1)
    signal = 0
    sig = [0, 0, 0, 0]
       
    while True:
       signal = wiringpi2.analogRead(adc_port)      
       if signal < sig[0] <= sig[1] >= sig[2] > sig[3]:
           average[channel].append(signal)
	   time.sleep(0.01)	   
       sig = [signal] + sig
       del sig[-1]
       
def adcread_MCP3208(channel0, channel1): 
    sig1 = [0, 0, 0, 0]
    sig2 = [0, 0, 0, 0]
    while True:    
        r1 = spi.xfer2([4 | 2 | (channel0 >> 2), (channel0 & 3) << 6, 0])
        signal1 = ((r1[1] & 15) << 8) + r1[2]
        if signal1 < sig1[0] <= sig1[1] >= sig1[2] > sig1[3]:
            arr = numpy.array([sig1[0], sig1[1], sig1[2], sig1[3], signal1])
            if numpy.std(arr, axis=0) < 40:
                average[channel0].append(sig1[1])
                #time.sleep(0.00001) 
                #print str(signal1)+' '+str(sig1[0])+' '+str(sig1[1])+' '+str(sig1[2])+' '+str(sig1[3])

        r2 = spi.xfer2([4 | 2 | (channel1 >> 2), (channel1 & 3) << 6, 0])
        signal2 = ((r2[1] & 15) << 8) + r2[2]       
        if signal2 < sig2[0] <= sig2[1] >= sig2[2] > sig2[3]:
            arr = numpy.array([sig2[0], sig2[1], sig2[2], sig2[3], signal2])
            if numpy.std(arr, axis=0) < 40:
                average[channel1].append(sig2[1])
                #time.sleep(0.00001) 
                #print str(signal2)+' '+str(sig2[0])+' '+str(sig2[1])+' '+str(sig2[2])+' '+str(sig2[3])

        sig1 = [signal1] + sig1
        del sig1[-1]
        sig2 = [signal2] + sig2
        del sig2[-1]
       	
def csv_write(d):
    time.sleep(0.9988)
    print datetime.datetime.now()
    threading.Timer(1, csv_write(1)).start();

def multi_get(uris,timeout=1.0):
    def alive_count(lst):
        alive = map(lambda x : 1 if x.isAlive() else 0, lst)
        return reduce(lambda a,b : a + b, alive)
    threads = [ URLThread(uri) for uri in uris ]
    for thread in threads:
        thread.start()
    while alive_count(threads) > 0 and timeout > 0.0:
        timeout = timeout - UPDATE_INTERVAL
        sleep(UPDATE_INTERVAL)
    return [ (x.url, x.response) for x in threads ]

def display_power(power):
    screen.fill((0,0,0))
    smallfont = pygame.font.SysFont("Monofonto", 30)
    descr = smallfont.render("Current Power Consumption:", 1, (255, 255, 255))
    screen.blit(descr, (10, 10))

    c1font = pygame.font.SysFont("Monofonto", 35)
    c1label = c1font.render("Circuit 1:", 1, (255, 255, 0))
    screen.blit(c1label, (40, 45))

    myfont = pygame.font.SysFont("Monofonto", 100)
    powerlabel1 = myfont.render(str(power[0])+"W", 1, (0, 255, 30))
    screen.blit(powerlabel1, (40, 65))

    c2label = c1font.render("Circuit 2:", 1, (255, 255, 0))
    screen.blit(c2label, (40, 140))

    powerlabel2 = myfont.render(str(power[1])+"W", 1, (0, 255, 30))
    screen.blit(powerlabel2, (40,160))

    pygame.display.update()

class URLThread(Thread):
    def __init__(self,url):
        super(URLThread, self).__init__()
        self.url = url
        self.response = None

    def run(self):
        self.request = urlopen(self.url)
        self.response = self.request.read()

if __name__="__main__":    
    init_wiringpi2()
    init_spidev()	
    #init_tft()
    #thread.start_new_thread(csv_write, (1,))
    thread.start_new_thread(http_get_thread, (1,), {'sleeptime':0.5, 'conversion':4490})
    #thread.start_new_thread(adcread_C1())
    thread.start_new_thread(adcread_MCP3208(0, 1))
