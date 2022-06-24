import logging

def log_start(enable_log,file_name):
    if enable_log == True:
        return logging.basicConfig(filename=file_name,
                            format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S',level=logging.INFO)
    else:
        return logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
