from os import path,listdir,remove
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from configparser import ConfigParser, ExtendedInterpolation
from time import time,sleep
import log_func as log
from ast import literal_eval

# Run config file to setup
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('/home/pi/code/config.init')

# Starting log file
log.log_start(literal_eval(config['LOG']['enable_log']),
              path.join(config['LOG']['path'],config['LOG']['file_name']))



try:
    connect_str = config['CLOUD']['connection']

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a unique name for the container
    container_name = config['CLOUD']['container']
    # Create a local directory to hold blob data
    local_path = config['CLOUD']['path']
    container_client = ContainerClient.from_connection_string(connect_str,container_name)
    log.logging.info('[CLOUD] service enable = %s'%(literal_eval(config['DEFAULT']['enable_cloud'])))
    while 1:
        if literal_eval(config['DEFAULT']['enable_cloud']) == True:
            log.logging.info('[CLOUD] Cloud: Looking for files...')
            try:
                # Create a file in the local data directory to upload and download
                local_file_name = [f for f in listdir(local_path) if path.isfile(path.join(local_path, f))]
                local_file_name.sort()
                
                # Upload the created file
                for file in local_file_name:
                    try:
                        if (time() - path.getmtime(path.join(local_path,file))) > 1:
                            blob_client = container_client.get_blob_client(file)
                            log.logging.info('[CLOUD] Uploading: %s'%(file))
                            with open(path.join(local_path,file),'rb') as data:
                                upload_file = blob_client.upload_blob(data,validate_content=True,overwrite=True)
                            remove(path.join(local_path,file))
                        else:
                            log.logging.info('[CLOUD] File Found. Waiting to finish')
                    except:
                        log.logging.warning('[CLOUD] File %s error to sent'%(file))
                        pass    
                sleep(float(config['DEFAULT']['timer'])//3)

            except Exception as ex:
                log.logging.warning('[CLOUD] %s'%(ex))
                pass


except Exception as ex:
    log.logging.warning('[CLOUD] %s'%(ex))
    pass