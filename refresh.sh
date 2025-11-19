/usr/bin/sudo pkill -F /home/pi/metar/metarmap/metarpid.pid
/usr/bin/sudo pkill -F /home/pi/metar/metarpaper/metarpaperpid.pid
/usr/bin/sudo /usr/bin/python3 /home/pi/metar/metarmap/metar.py & echo $! > /home/pi/metar/metarmap/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/pi/metar/metarpaper/metarpaper.py & echo $! > /home/pi/metar/metarpaper/metarpaperpid.pid

