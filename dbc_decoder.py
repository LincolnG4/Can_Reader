from configparser import ConfigParser, ExtendedInterpolation
import log_func as log
from os import path,listdir,remove,rename
from ast import literal_eval
from time import sleep

# Run config file to setup

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('/home/pi/code/config.init')
log.log_start(literal_eval(config['LOG']['enable_log']), path.join(config['LOG']['path'],config['LOG']['file_name']))

local_path = config['MEASURE']['path']

def get_file(local_path=local_path):
    files = [f for f in listdir(local_path) if path.isfile(path.join(local_path, f)) and f not in listdir(config['MEASURE']['path_decoded']) ]
    files.sort()
    return files

# Starting log

if literal_eval(config['DEFAULT']['enable_decoder']) == True:
    from asammdf import MDF
    def main (file,local_path=local_path):
        
        log.logging.info('[DBC] Starting DBC Decoder')

        dbc_file = list(map(str.strip,config['DBC']['files'].split(',')))
        dbc = [path.join(config['DBC']['path'],f) for f in listdir(config['DBC']['path']) if f in dbc_file ]

        log.logging.info('[DBC] Using DBC = %s',dbc)

        databases = {
                    "CAN": dbc,
                    }

        mdf = MDF(path.join(local_path,file))
        extracted,gps = mdf.extract_bus_logging(database_files=databases),mdf.select(['CAN_DataFrame.Latitude','CAN_DataFrame.Longitude'])

        extracted.append( [gps[0],gps[1]],comment='GPS' )
        extracted.save(path.join(config['MEASURE']['path_decoded'],file),overwrite=True)
        
        log.logging.info('[DBC] File sorted = ./sort/%s',file)
        
        remove(path.join(local_path,file))
        log.logging.info('[DBC] Backup file removed = %s',path.join(local_path,file))

else:
    
    def main (file,local_path=local_path):
        rename(path.join(local_path,file), path.join(config['MEASURE']['path_decoded'],file) )
   
while 1:
    files = get_file()
    log.logging.info('[DBC] Files found = %s',files)

    try:
        if files != []:
            for file in files:
                main(file)

    except Exception as e:
        log.logging.info('[DBC] Error = %s',e)
        pass

    sleep(int(literal_eval(config['DEFAULT']['timer'])//3))