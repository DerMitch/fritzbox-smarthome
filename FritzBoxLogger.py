# coding: utf-8
#!/usr/bin/env python3
"""
    FRITZ!Box SmartHome Temperature Tracker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from fritzhome import fritz
import datetime 
import time
import matplotlib.pyplot as plt
import glob
from threading import Thread
import signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class FritzBoxTemeraturePlotter(object):
    def parseFile(self, filename):
        logger.debug("Parsing file" + filename)
        f = open(filename,'r')
        timestamp=[]
        temperature=[]
        with open(filename) as f:
            mylist = f.read().splitlines()
        for line in mylist:
            line=line.split(";")
            timestamp.append(datetime.datetime.strptime(line[0],"%Y-%m-%d %H:%M:%S"))
            temperature.append(float(line[1]))
        return [timestamp,temperature]

    def __init__(self,plotnow=0):
        if plotnow:
            self.plot()
            
    def plot(self):
        logger.info("Start plotting")
        for file in glob.glob("LOG_*.txt"):
            data=self.parseFile(file)
            plt.plot(data[0],data[1],'o--',label=file[4:-4])
        plt.ylabel('temperature [°]')
        plt.legend(loc='upper center');
        plt.gcf().autofmt_xdate()
        plt.ylim(18,24)
        logger.debug("Showing plot")
        plt.show()
        logger.info("Closing plot")

class FritzBoxLogger(fritz.FritzBox,Thread):
    def __init__(self, ip, username, password, use_tls=False):
        super().__init__(ip, username, password, use_tls)
        Thread.__init__(self)
        self.goon=True
            
    def startLogging(self, repeats=2,delay=1):    
        i=0
        while (i!=repeats):
            super().login()
            allactors=super().get_actors()
            for actor in allactors:
                with open("LOG_" + actor.name+".txt", "a") as myfile:
                    myfile.write(time.strftime("%Y-%m-%d %H:%M:%S")+";"+str(actor.get_temperature())+"\n")
                logger.info(str(actor.get_temperature())+" [°C] @ " + actor.name)
            i=i+1;
            logger.warn('Close plot to refresh data')
            
            for j in range(delay):
                if not self.goon:
                    logger.warn('Fritzlogger stopped.')
                    return
                else:
                    time.sleep(1)
 
    def stopit(self):
        self.goon=False
        
    def run(self):
        self.startLogging(-1,3)
        
def signal_handler(signal, frame):
    logger.warn('You pressed Ctrl+C, stopping FritzLogger')
    f.stopit()
    
signal.signal(signal.SIGINT, signal_handler)

f=FritzBoxLogger("fritz.box", "smarthome","smarthome")
f.start();


while f.isAlive():
    p=FritzBoxTemeraturePlotter(1)

