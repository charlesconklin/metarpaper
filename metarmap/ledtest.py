#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import board
import neopixel
import time
import datetime
try:
	import astral
except ImportError:
	astral = None

# ledtest.py script iteration 1.0.0

# ---------------------------------------------------------------------------
# ------------START OF CONFIGURATION-----------------------------------------
# ---------------------------------------------------------------------------

# NeoPixel LED Configuration
LED_COUNT		= 22			# Number of LED pixels.
LED_PIN			= board.D18		# GPIO pin connected to the pixels (18 is PCM).
LED_BRIGHTNESS	= 0.5	    	# Float from 0.0 (min) to 1.0 (max)
LED_ORDER		= neopixel.RGB	# Strip type and colour ordering

COLOR_GREEN		= (255,0,0)		# Green
COLOR_RED		= (0,255,0)		# Red
COLOR_BLUE		= (0,0,255)		# Blue
COLOR_CLEAR		= (0,0,0)		# Clear

# ---------------------------------------------------------------------------
# ------------END OF CONFIGURATION-------------------------------------------
# ---------------------------------------------------------------------------

print("Running ledtest.py at " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))

looplimit = 3
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS, pixel_order = LED_ORDER, auto_write = False)
currentcolor = COLOR_RED
lednum = 0

while looplimit > 0:
    print("> LOOP")
    print("-> RED")
    currentcolor = COLOR_RED
    lednum = 0
    while lednum < LED_COUNT:
        pixels[lednum] = currentcolor
        lednum += 1
    # Update actual LEDs all at once
    pixels.show()
    time.sleep(10)

	
    print("-> GREEN")
    currentcolor = COLOR_GREEN
    lednum = 0
    while lednum < LED_COUNT:
        pixels[lednum] = currentcolor
        lednum += 1
    # Update actual LEDs all at once
    pixels.show()
    time.sleep(10)
		
    print("-> BLUE")
    currentcolor = COLOR_BLUE
    lednum = 0
    while lednum < LED_COUNT:
        pixels[lednum] = currentcolor
        lednum += 1
    # Update actual LEDs all at once
    pixels.show()
    time.sleep(10)

    looplimit -= 1

print()
print("CLEAR DISPLAY")
lednum = 0

while lednum < LED_COUNT:
    pixels[lednum] = COLOR_CLEAR
    lednum += 1

pixels.show()
print()
print("Done")

exit(0) # Successful exit