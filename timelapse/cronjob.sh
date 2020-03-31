fuser -k 8080/tcp
fuser -k 8090/tcp
export DISPLAY=:0
/usr/bin/python3 /home/pi/Documenten/raspberrypi/timelapse/timelapse.py
pkill -o chromium
