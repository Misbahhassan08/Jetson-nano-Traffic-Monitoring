import os
from logClass import *
import os.path
from os import path
import datetime


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_dt = datetime.datetime.now().strftime('%Y_%m_%d')
csv_file = 'AggSpeedInfo_{}.csv'.format(_dt)
old_csv_file = csv_file
video = '{}/testVideo2.mp4'.format(ROOT_DIR)
model = "ssd-mobilenet-v2"
model_th = 0.3
show_output = False

hiSpeed = 70
lowSpeed = 30

EnforceSpeed = 70
VehicleDirection = 'Down'
VehicleLan = 'LN'
GPSLati =  22.2315
GPSLongi = 43.25

overSpeedPath = './temp/overSpeed'
aggpath = './temp/aggregate'



header= ['EventDateTime',
            'VehicleSpeed',
            'EnforceSpeed',
            'VehicleDirection',
            'VehicleLane',
            'GPSLatitude',
            'GPSLogitude',
            'ImageFilename',
            'RefFilename',
            'RefolderPath'
            ]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
loggingStreamHandler = CSVTimedRotatingFileHandler(filename=csv_file, header = header) #to save to file
loggingStreamHandler.setFormatter(CSVFormatter())
logger.addHandler(loggingStreamHandler)

def scanlog():
    global old_csv_file
    global csv_file
    global logger
    global loggingStreamHandler
    
    old_csv_file = csv_file
    csv_file = 'AggSpeedInfo_{}.csv'.format(datetime.datetime.now().strftime('%Y_%m_%d'))
    if not path.isfile(csv_file):
        csv_file = 'AggSpeedInfo_{}'.format(datetime.datetime.now().strftime('%Y_%m_%d'))
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        loggingStreamHandler = CSVTimedRotatingFileHandler(filename=csv_file, header = header) #to save to file
        loggingStreamHandler.setFormatter(CSVFormatter())
        logger.addHandler(loggingStreamHandler)

        return False
    else: return True
   

