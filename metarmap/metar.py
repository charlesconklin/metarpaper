#!/usr/bin/env python3
import os
import json
import requests as req # type: ignore
import board # type: ignore
import neopixel # type: ignore
import time
import datetime
try:
	import astral # type: ignore
except ImportError:
	astral = None

# metar.py script iteration 1.5.1

# ---------------------------------------------------------------------------
# ------------START OF CONFIGURATION-----------------------------------------
# ---------------------------------------------------------------------------

# NeoPixel LED Configuration
LED_COUNT		= 22			# Number of LED pixels.
LED_PIN			= board.D18		# GPIO pin connected to the pixels (18 is PCM).
LED_BRIGHTNESS		= 0.5			# Float from 0.0 (min) to 1.0 (max)
LED_ORDER		= neopixel.RGB		# Strip type and colour ordering

COLOR_VFR		= (255,0,0)		# Green
COLOR_VFR_FADE		= (125,0,0)		# Green Fade for wind
COLOR_MVFR		= (0,0,255)		# Blue
COLOR_MVFR_FADE		= (0,0,125)		# Blue Fade for wind
COLOR_IFR		= (0,255,0)		# Red
COLOR_IFR_FADE		= (0,125,0)		# Red Fade for wind
COLOR_LIFR		= (0,125,125)		# Magenta
COLOR_LIFR_FADE		= (0,75,75)		# Magenta Fade for wind
COLOR_CLEAR		= (0,0,0)		# Clear
COLOR_LIGHTNING		= (255,255,255)		# White
COLOR_HIGH_WINDS 	= (255,255,0) 		# Yellow

# ----- Blink/Fade functionality for Wind and Lightning -----
# Do you want the METARMap to be static to just show flight conditions, or do you also want blinking/fading based on current wind conditions
ACTIVATE_WINDCONDITION_ANIMATION = True	# Set this to False for Static or True for animated wind conditions
#Do you want the Map to Flash white for lightning in the area
ACTIVATE_LIGHTNING_ANIMATION = True		# Set this to False for Static or True for animated Lightning
# Fade instead of blink
FADE_INSTEAD_OF_BLINK	= True			# Set to False if you want blinking
# Blinking Windspeed Threshold
WIND_BLINK_THRESHOLD	= 15			# Knots of windspeed to blink/fade
HIGH_WINDS_THRESHOLD	= 25			# Knots of windspeed to trigger Yellow LED indicating very High Winds, set to -1 if you don't want to use this
ALWAYS_BLINK_FOR_GUSTS	= False			# Always animate for Gusts (regardless of speeds)
# Blinking Speed in seconds
BLINK_SPEED		= 1.0			# Float in seconds, e.g. 0.5 for half a second
# Total blinking time in seconds.
# For example set this to 300 to keep blinking for 5 minutes if you plan to run the script every 5 minutes to fetch the updated weather
BLINK_TOTALTIME_SECONDS	= 300

# ----- Daytime dimming of LEDs based on time of day or Sunset/Sunrise -----
ACTIVATE_DAYTIME_DIMMING = False		# Set to True if you want to dim the map after a certain time of day
BRIGHT_TIME_START	= datetime.time(7,0)	# Time of day to run at LED_BRIGHTNESS in hours and minutes
DIM_TIME_START		= datetime.time(19,0)	# Time of day to run at LED_BRIGHTNESS_DIM in hours and minutes
LED_BRIGHTNESS_DIM	= 0.1			# Float from 0.0 (min) to 1.0 (max)

USE_SUNRISE_SUNSET 	= True			# Set to True if instead of fixed times for bright/dimming, you want to use local sunrise/sunset
LOCATION 		= "Salt Lake City"		# Nearby city for Sunset/Sunrise timing, refer to https://astral.readthedocs.io/en/latest/#cities for list of cities supported

# ----- Show a set of Legend LEDS at the end -----
SHOW_LEGEND = False			# Set to true if you want to have a set of LEDs at the end show the legend
# You'll need to add 7 LEDs at the end of your string of LEDs
# If you want to offset the legend LEDs from the end of the last airport from the airports file,
# then change this offset variable by the number of LEDs to skip before the LED that starts the legend
OFFSET_LEGEND_BY = 0
# The order of LEDs is:
#	VFR
#	MVFR
#	IFR
#	LIFR
#	LIGHTNING
#	WINDY
#	HIGH WINDS


# ---------------------------------------------------------------------------
# ------------END OF CONFIGURATION-------------------------------------------
# ---------------------------------------------------------------------------

def getMetarInfo(wx_array, airport_code):
	for wx in wx_array:
		if wx['icaoId'] == airport_code:
			return wx
	return None

print("Running metar.py at " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))

# Figure out sunrise/sunset times if astral is being used
if astral is not None and USE_SUNRISE_SUNSET:
	try:
		# For older clients running python 3.5 which are using Astral 1.10.1
		ast = astral.Astral()
		try:
			city = ast[LOCATION]
		except KeyError:
			print("Error: Location not recognized, please check list of supported cities and reconfigure")
		else:
			print(city)
			sun = city.sun(date = datetime.datetime.now().date(), local = True)
			BRIGHT_TIME_START = sun['sunrise'].time()
			DIM_TIME_START = sun['sunset'].time()
	except AttributeError:
		# newer Raspberry Pi versions using Python 3.6+ using Astral 2.2
		import astral.geocoder # type: ignore
		import astral.sun # type: ignore
		try:
			city = astral.geocoder.lookup(LOCATION, astral.geocoder.database())
		except KeyError:
			print("Error: Location not recognized, please check list of supported cities and reconfigure")
		else:
			print(city)
			sun = astral.sun.sun(city.observer, date = datetime.datetime.now().date(), tzinfo=city.timezone)
			BRIGHT_TIME_START = sun['sunrise'].time()
			DIM_TIME_START = sun['sunset'].time()
	print("Sunrise:" + BRIGHT_TIME_START.strftime('%H:%M') + " Sunset:" + DIM_TIME_START.strftime('%H:%M'))

# Initialize the LED strip
bright = BRIGHT_TIME_START < datetime.datetime.now().time() < DIM_TIME_START
print("Wind animation:" + str(ACTIVATE_WINDCONDITION_ANIMATION))
print("Lightning animation:" + str(ACTIVATE_LIGHTNING_ANIMATION))
print("Daytime Dimming:" + str(ACTIVATE_DAYTIME_DIMMING) + (" using Sunrise/Sunset" if USE_SUNRISE_SUNSET and ACTIVATE_DAYTIME_DIMMING else ""))

pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS_DIM if (ACTIVATE_DAYTIME_DIMMING and bright == False) else LED_BRIGHTNESS, pixel_order = LED_ORDER, auto_write = False)

# Read the airports file to retrieve list of airports and use as order for LEDs
base_path = os.getcwd()
airport_file_path = os.path.join(base_path, 'airports.txt')
with open(airport_file_path) as a_file:
	airports_array = a_file.readlines()
airports_array = [x.strip() for x in airports_array]

stationList = []
metar_array = []
# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://aviationweather.gov/data/api/#/Dataserver/dataserverMetars
url = "https://aviationweather.gov/api/data/metar?hours=0&format=json&ids=" + ",".join([item for item in airports_array if item != "NULL"])
print(url)
resp = req.get(url)
if resp.status_code == 200:	
	# print(resp.text)
	# Retrieve flying conditions from the service response and store in a dictionary for each airport
	metar_array = resp.json()
	for metar in metar_array:
		stationId = metar['icaoId']
		print(stationId)

		#preset new fields for data display
		metar['windGust'] = False
		metar['windy'] = False
		metar['highWinds'] = False
		metar['lightning'] = False

		if 'fltCat' not in metar:
			print(" - Missing flight condition, skipping.")
			metar["fltCat"] = "UNK"
			continue

		if 'wgst' in metar:
			metar['windGust'] = True if (ALWAYS_BLINK_FOR_GUSTS or int(metar['wgst']) > WIND_BLINK_THRESHOLD) else False

		if 'wspd' in metar:
			# windy true id beyond threshold or gust beyond threshold
			metar['windy'] = True if (ACTIVATE_WINDCONDITION_ANIMATION and (int(metar["wspd"]) >= WIND_BLINK_THRESHOLD or metar["windGust"] == True)) else False
			metar['highWinds'] = True if HIGH_WINDS_THRESHOLD != -1 and \
								 ((metar['windy'] == True and int(metar["wspd"]) >= HIGH_WINDS_THRESHOLD) or \
								 (metar['windGust'] == True and int(metar["wgst"]) >= HIGH_WINDS_THRESHOLD)) else False

		if 'rawOb' in metar:
			print(' - ' + metar['rawOb'])
			rawText = metar['rawOb']
			metar['lightning'] = False if ((rawText.find('LTG', 4) == -1 and rawText.find('TS', 4) == -1) or rawText.find('TSNO', 4) != -1) else (True and ACTIVATE_LIGHTNING_ANIMATION)
		
# Setting LED colors based on weather conditions
looplimit = int(round(BLINK_TOTALTIME_SECONDS / BLINK_SPEED)) if (ACTIVATE_WINDCONDITION_ANIMATION or ACTIVATE_LIGHTNING_ANIMATION) else 1

windCycle = False
numAirports = len(stationList)
while looplimit > 0:
	i = 0
	for airportcode in airports_array:
		# Skip NULL entries
		if airportcode == "NULL":
			i += 1
			continue

		color = COLOR_CLEAR
		metarData = getMetarInfo(metar_array, airportcode)
		windy = False
		highWinds = False
		lightningConditions = False

		if metarData != None:
			windy = True if windCycle == True and metarData["windy"] == True else False
			highWinds = True if windCycle == True and metarData["highWinds"] == True else False
			lightningConditions = True if windCycle == False and metarData["lightning"] == True else False
			
			if metarData["fltCat"] == "VFR":
				color = COLOR_VFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else COLOR_HIGH_WINDS if highWinds else (COLOR_VFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif metarData["fltCat"] == "MVFR":
				color = COLOR_MVFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else COLOR_HIGH_WINDS if highWinds else (COLOR_MVFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif metarData["fltCat"] == "IFR":
				color = COLOR_IFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else COLOR_HIGH_WINDS if highWinds else (COLOR_IFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			elif metarData["fltCat"] == "LIFR":
				color = COLOR_LIFR if not (windy or lightningConditions) else COLOR_LIGHTNING if lightningConditions else COLOR_HIGH_WINDS if highWinds else (COLOR_LIFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR) if windy else COLOR_CLEAR
			else:
				color = COLOR_CLEAR
		
		print("Setting LED " + str(i) + " for " + airportcode + " to " + ("lightning " if lightningConditions else "") + ("very " if highWinds else "") + ("windy " if windy else "") + (metarData["fltCat"] if metarData != None else "None") + " " + str(color))
		pixels[i] = color
		i += 1

	# Legend
	if SHOW_LEGEND:
		pixels[i + OFFSET_LEGEND_BY] = COLOR_VFR
		pixels[i + OFFSET_LEGEND_BY + 1] = COLOR_MVFR
		pixels[i + OFFSET_LEGEND_BY + 2] = COLOR_IFR
		pixels[i + OFFSET_LEGEND_BY + 3] = COLOR_LIFR
		if ACTIVATE_LIGHTNING_ANIMATION == True:
			pixels[i + OFFSET_LEGEND_BY + 4] = COLOR_LIGHTNING if windCycle else COLOR_VFR # lightning
		if ACTIVATE_WINDCONDITION_ANIMATION == True:
			pixels[i+ OFFSET_LEGEND_BY + 5] = COLOR_VFR if not windCycle else (COLOR_VFR_FADE if FADE_INSTEAD_OF_BLINK else COLOR_CLEAR)    # windy
			if HIGH_WINDS_THRESHOLD != -1:
				pixels[i + OFFSET_LEGEND_BY + 6] = COLOR_VFR if not windCycle else COLOR_HIGH_WINDS  # high winds

	# Update actual LEDs all at once
	pixels.show()
	
	# Switching between animation cycles
	time.sleep(BLINK_SPEED)
	windCycle = False if windCycle else True
	looplimit -= 1

print()
print("Done")

