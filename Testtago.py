# -*- coding: utf-8 -*-
import tago
import cantools
from pprint import pprint
from time import time,sleep
from os import rename,path
from configparser import ConfigParser, ExtendedInterpolation
from ast import literal_eval
import numpy as np
from serial import Serial
from can import interface
import string
from pynmea2 import parse
from datetime import datetime
import log_func as log
import csv
import random
my_device = tago.Device('8c06628d-7781-4c1c-a679-b9bea76c9767')

# Starting setup
time_save,timer_gps  = time(), time()

# Run config file to setup
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('/home/pi/code/config.init')
# Starting log file
log.log_start(literal_eval(config['LOG']['enable_log']),
              path.join(config['LOG']['path'],config['LOG']['file_name']))
# Starting log file
log.log_start(literal_eval(config['LOG']['enable_log']),
              path.join(config['LOG']['path'],config['LOG']['file_name']))


db = cantools.database.load_file('/home/pi/code/dbc/j1939.dbc')


with open('gps.csv',newline='') as filegps:
    spamreader = csv.reader(filegps, delimiter=',', quotechar='|')
    simugps = [row for row in spamreader]

# CAN Setting
if literal_eval(config['CAN']['enable_filtering']) == True:

    messages_filter = list(map(str.strip,config['CAN']['can_filters'].split(',')))
    can_filter = [dict([ ( "can_id", int(i,16) ), ("can_mask", int("F"*7,16)) ]) for i in messages_filter]
    bus = interface.Bus(
        config['CAN']['can_interface'], bustype=config['CAN']['bustype'], can_filters=can_filter)

else:
    bus = interface.Bus(
        config['CAN']['can_interface'], bustype=config['CAN']['bustype'], can_filters = None)

ig = 0
# GPS start
lat,lng = 0,0
data = []
def GPS(lat,lng):
    try:
        # GPS Setting
        serial_port = Serial(config['GPS']['port'],
                                    baudrate=int(config['GPS']['baudrate']),
                                    timeout=0.5)
        newdata = serial_port.readline()
        newdata = newdata.decode("utf-8")

        if newdata[0:6] == "$GPRMC":
            try:
                newmsg = parse(newdata)
                lat,lng  = newmsg.latitude, newmsg.longitude
                log.logging.info('[MEASURE] GPS On ')
            except Exception as e:
                log.logging.warning('[MEASURE] Error GPS:%s'%(e))
                return lat, lng
                
        return lat,lng

    except:
        log.logging.warning('[MEASURE] GPS Off ')
        return lat,lng
# GPS Init
lat,lng = GPS(lat,lng)

msg_filter = ['EngSpeed','TachographVehicleSpeed','FuelLevel1','EngIntercoolerTemp','EngTurboOilTemp','EngFuelTemp1','EngOilTemp1','TrailerABSStatus','AccelPedalPos1','TotalVehicleDistance','EngTorqueMode']

while 1:
    


    try:  
        message = bus.recv(timeout=5)
        #print(message)
        try:
            a = db.decode_message(message.arbitration_id, message.data)
        except:
            pass

       
        # if message != None:
        #     if (time()  - timer_gps) >= 2:
        #         lat,lng = GPS(lat,lng)
        #         if lat != 0 and lng != 0 :
        #             gpsdata = {
        #                     "variable": "location",
        #                     "value": "My Address",
        #                     "location": {
        #                         "lat": lat,
        #                         "lng": lng
        #                     },
        #                     "metadata": {
        #                         "color": "green",
        #                         "icon": "Truck"
        #                     }
        #                     }
        #             result = my_device.insert(gpsdata)
        #             #print(result, 'GPS')
        #         timer_gps = time()

        try:
            if (time()  - time_save) >= random.randint(0, 5):
                for x in a.keys() :
                    #print(x)
                    if x in msg_filter:
                        if a[x] != 'Nota available':
                            data = {
                                    'variable': x,
                                    'unit'    : 'rpm',
                                    'value'   : str(a[x]),
                                    'time'    : str(datetime.now(tz=None))
                                    }

                            result = my_device.insert(data)
                            #   7   print(result, x,a[x])
                            data = {
                                    "variable": "location",
                                    "value": "My Address",
                                    "location": {
                                        "lat": float(simugps[ig][0]),
                                        "lng": float(simugps[ig][1])
                                    },
                                    "metadata": {
                                        "color": "green"
                                    }
                                    }
                            ig += 1
                            result = my_device.insert(data)
                            #print(result)
                time_save = time()
        except:
            pass

        
    except IOError:
        type, value, traceback = sys.exc_info()
        #print('Error opening %s: %s' % (value.filename, value.strerror))


