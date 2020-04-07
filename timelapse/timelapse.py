# This file does the following:
# 1) Check time of day to see if sun is still up
# 2) If so, take picture
# 3) Upload to Google Drive

from sys import exit
import logging
import os

os.chdir("/home/pi/Documents/raspberrypi/timelapse")

logging.basicConfig(
    filename='timelapse.log',
    filemode='a',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# # Kill processes on ports 8080 and 8090, needed for Google Authentication
#os.system("fuser -k 8080/tcp")
#os.system("fuser -k 8090/tcp")

# 1) Check time and see if sun still up
from astral import LocationInfo
from astral.sun import sun
import datetime
import pytz
city = LocationInfo("Antwerp", "Belgium", "Europe/Brussels", 51.26,4.4)
s = sun(city.observer,date=datetime.date.today())
local = pytz.timezone("Europe/Brussels")
current_time = local.localize(datetime.datetime.now())

dawn = s["dawn"].astimezone(local)
sunrise = s["sunrise"].astimezone(local)
sunset = s["sunset"].astimezone(local)
dusk = s["dusk"].astimezone(local)

if current_time < sunrise or current_time > sunset:
    logging.critical('No sunlight, no picture')
    exit(0)

# 2) Take picture
import gphoto2 as gp
from time import sleep

try:
    camera = gp.Camera()
    camera.init()
    print('Capturing image')
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
    target = '/home/pi/Documents/raspberrypi/timelapse/test.jpg'
    print('Copying image to', target)
    camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)
    camera.exit()
    # logging.critical("Picture taken")
except:
    logging.error("Can't take picture")
    exit(0)

# 3) Write to Google Drive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

try:
    g_login = GoogleAuth()
    g_login.LocalWebserverAuth()
except:
    logging.error("Can't authenticate Google Drive")
    exit(0)

try:
    drive = GoogleDrive(g_login)
except:
    logging.error("Can't initialize Google Drive object")
    exit(0)    

# Code to get list of all folders:
# file_list = drive.ListFile({'q': 'trashed=false', 'maxResults': 10}).GetList()
# for file1 in file_list:
#   print('title: %s, id: %s' % (file1['title'], file1['id']))

image_to_upload = drive.CreateFile({'parents': [{'kind': 'drive#fileLink','id': '1K1-DGt0d_EinoMFhr27e1FuKEegM_eQz'}],'title':current_time.strftime("%d-%m-%Y--%H:%M:%S") + '.jpg','mimeType':'image/jpeg'})
image_to_upload.SetContentFile('test.jpg')

try:
    image_to_upload.Upload()
    logging.critical('Image uploaded to Google Drive')
except:
    logging.error("Can't upload image file to Google Drive")
    exit(0)   
