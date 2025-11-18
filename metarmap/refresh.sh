/usr/bin/sudo pkill -F /home/pi/metarmap/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/pi/metarmap/metar.py & echo $! > /home/pi/metarmap/metarpid.pid
