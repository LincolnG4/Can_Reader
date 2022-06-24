# -*- coding: utf-8 -*-
import serial
import can
import time as t
import string
import pynmea2
import csv
from os import rename
from configparser import ConfigParser

# Run config file to setup
config = ConfigParser()
config.read('config.init')

# Starting setup
time_save = t.time()
log_file = config['PATHS']['log_file'] % ((str(time_save)).replace('.', '-'))
f_start = open(log_file, "w")
f_start.close()

# GPS Setting
serial_port = serial.Serial(config['GPS']['port'],
                            baudrate=config['GPS']['baudrate'],
                            timeout=config['GPS']['timeout'])
lat = 0
lng = 0

# CAN Setting
bus = can.interface.Bus(
    config['CAN']['can_interface'], bustype=config['CAN']['bustype'])


def log(time_save, list_data):
    if (t.time() - time_save) >= config['DEFAULT']['timer']:
        rename(config['PATHS']['log_file'] %
               ((str(time_save)).replace('.', '-')),
               config['PATHS']['output_file'] % ((str(time_save)).replace('.', '-')))
        time_save = t.time()

    with open(config['PATHS']['log_file'] % ((str(time_save)).replace('.', '-')), 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(list_data)
    return time_save


def GPS(serial_port):
    dataout = pynmea2.NMEAStreamReader()
    newdata = serial_port.readline()
    if newdata[0:6] == "$GPRMC":
        try:
            newmsg = pynmea2.parse(newdata)
            lat = newmsg.latitude
            lng = newmsg.longitude
        except:
            pass
        return lat, lng


try:
    while True:
        try:
            message = bus.recv()

            list_data = [message.timestamp,
                         message.arbitration_id, message.flags, message.dlc,
                         message.data, '0', GPS(serial_port)[0], GPS(serial_port)[1]]

            time_save = log(time_save, list_data)

        except:
            continue

except KeyboardInterrupt:
    raise
