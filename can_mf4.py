# -*- coding: utf-8 -*-
from asammdf import MDF, SUPPORTED_VERSIONS, Signal
from time import time
from os import rename,path
from configparser import ConfigParser, ExtendedInterpolation
from ast import literal_eval
import numpy as np
from serial import Serial
from can import interface
import string
from pynmea2 import parse
from datetime import datetime
from asammdf.blocks.source_utils import Source
import log_func as log

# Starting setup
time_save,timer_gps  = time(),time()

# Run config file to setup
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('/home/pi/code/config.init')

# Starting log file
log.log_start(literal_eval(config['LOG']['enable_log']),
              path.join(config['LOG']['path'],config['LOG']['file_name']))

# array definition of type
array_def = [('CAN_DataFrame.ID', '<u4'), ('CAN_DataFrame.IDE', 'u1'),
             ('CAN_DataFrame.DLC', 'u1'), ('CAN_DataFrame.DataBytes', 'u1', (8,)),
             ('CAN_DataFrame.BusChannel', 'u1'),
             ('CAN_DataFrame.Latitude', 'float'), ('CAN_DataFrame.Longitude', 'float')]


# GPS start
lat,lng = 0,0

#CAN array start
array,databyte,sigs,timestamp,arr_can,messages_mask=[], [], [], [], [], []


# CAN Setting
if literal_eval(config['CAN']['enable_filtering']) == True:

    messages_filter = list(map(str.strip,config['CAN']['can_filters'].split(',')))
    for msg in messages_filter:
        if len(msg) > 4:
            messages_mask.append(int("F"*7,16))
        else:
            messages_mask.append(int("F"*3,16))

    messages_mask 
    can_filter = [dict([ ( "can_id", int(i,16) ), ("can_mask", j)]) for i,j in zip(messages_filter,messages_mask)]
    bus = interface.Bus(
        config['CAN']['can_interface'], bustype=config['CAN']['bustype'], can_filters=can_filter)

else:
    bus = interface.Bus(
        config['CAN']['can_interface'], bustype=config['CAN']['bustype'], can_filters = None)


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

log.logging.info('[MEASURE] Service started')

def  mf4_creator(timestamp,array,array_def,sigs):
    
    with MDF(version='4.11') as mdf:
        
        sig = Signal(
            np.rec.array(array, dtype=array_def),
            timestamps=np.array(timestamp, dtype=np.float64),
            name='CAN_DataFrame',
            comment='CAN bus channel collected',
            source=Source(
                source_type=Source.SOURCE_BUS,
                bus_type=Source.BUS_TYPE_CAN,
                name="CAN bus",
                path="CAN bus",
                comment="",
            )
        )
        sigs.append(sig)

        mdf.append(sigs, comment='',
                    common_timebase=True)

        mf_name = ''.join([config['MEASURE']['output_file_name'],
                              (datetime.fromtimestamp(time())).strftime("%d_%m_%Y_%H_%M_%S"),'.mf4'])
        
        mdf.save('/'.join([config['MEASURE']['path'],mf_name]), overwrite=False)
        sigs=[]

    print('[MEASURE] MF4 Created %s'% (mf_name))
    log.logging.info('[MEASURE] MF4 Created: %s',mf_name)

    return sigs

def vectorize(message):
    timestamp.append(message.timestamp)
    int_values = [x for x in message.data]
    array.append((message.arbitration_id, 
                0, message.dlc, tuple(
                int_values), '0',lat,lng))

try:
    while 1:
        try:
            
            message = bus.recv(timeout=5)
  
            if message != None:
                if (time()  - timer_gps) >= 2:
                    lat,lng = GPS(lat,lng)
                    timer_gps = time()
                    
                vectorize(message)    

            else:
                log.logging.warning('[MEASURE] No message on CAN ')

            if (time() - time_save) >= float(config['DEFAULT']['timer']):

                if timestamp != []:
                    sigs = mf4_creator(timestamp,array,array_def,sigs)
                    array,timestamp,arr_can,time_save = [], [], [],time()

                else:
                    log.logging.warning('[MEASURE] File empty: No measure created')
                    array,timestamp,arr_can,time_save= [], [], [],time()

        except Exception as e:
            log.logging.error('[MEASURE] %s ' %(e))
            continue

except KeyboardInterrupt:
    log.logging.error('[MEASURE] Service killed')
    raise
