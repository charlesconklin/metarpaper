#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import logging
import time
import navbuttons
import paperdraw
import requests as req # type: ignore


base_path = os.getcwd()
airport_file_path = os.path.join(base_path, 'paperairports')

logging.basicConfig(level=logging.INFO)

wx_url = "https://aviationweather.gov/api/data/metar?hours=0&format=json&ids="

with open(airport_file_path) as a_file:
    airports_array = a_file.readlines()
airports_array = [x.strip() for x in airports_array]

wx_url = wx_url + ",".join([a for a in airports_array if a != "NULL"])

paperSettings = {}
paperSettings["metar_list"] = []
paperSettings["loop_count"] = 0
paperSettings["loop_index"] = 0
paperSettings["hold"] = False
paperSettings["hold_sec"] = 0

hold_amount = 20
timeBetweenAiports = 5

def getMetarInfo(code):
    for m in paperSettings["metar_list"]:
        if m["icaoId"] == code:
            return m        
        
        info = {}
        info["icaoId"] = code
        info["name"] = "No Metar Available"        
        info["fltCat"] = ""
    return None

def displayMetarAtIndex(indexVal):
    a_code = airports_array[paperSettings["loop_index"]]
    info = getMetarInfo(a_code)
    logging.info("draw airport weather: " + info["icaoId"])
    paperdraw.drawMetar(info)

def displayMetars():
    paperSettings["loop_count"] = 1
    while paperSettings["loop_count"] < 3:
        print(f"loop {paperSettings["loop_count"]}")
        paperSettings["loop_index"] = 0
            
        while paperSettings["loop_index"] < len(airports_array):
            while paperSettings["hold"] == True:
                print(f"hold {paperSettings['hold_sec']}")
                paperSettings["hold_sec"] -= 1
                paperSettings["hold"] = paperSettings["hold_sec"] > 0
                time.sleep(1)
            displayMetarAtIndex(paperSettings["loop_index"])
            time.sleep(timeBetweenAiports)
            paperSettings["loop_index"] += 1
        paperSettings["loop_count"] += 1

def incrementDisplayIndex():
    logging.info("increment")
    iVal = paperSettings["loop_index"]
    iVal += 1
    if iVal >= len(airports_array):
        iVal = 0
    displayMetarAtIndex(iVal)
    paperSettings["loop_index"] = iVal
    paperSettings["hold"] = True    
    paperSettings["hold_sec"] = hold_amount

def decrementDisplayIndex():
    logging.info("decrement")
    iVal = paperSettings["loop_index"]
    iVal -= 1
    if iVal < 0:
        iVal = len(airports_array) - 1
    displayMetarAtIndex(iVal)    
    paperSettings["loop_index"] = iVal
    paperSettings["hold"] = True    
    paperSettings["hold_sec"] = hold_amount

def moveTostart():
    logging.info("start")
    paperSettings["loop_index"] = 0
    displayMetarAtIndex(paperSettings["loop_index"])
    paperSettings["hold"] = True    
    paperSettings["hold_sec"] = hold_amount

def moveToEnd():
    logging.info("end")
    paperSettings["loop_index"] = len(airports_array) - 1
    displayMetarAtIndex(paperSettings["loop_index"])
    paperSettings["hold"] = True    
    paperSettings["hold_sec"] = hold_amount

def onButtonPress(buttonId):
    logging.info(f"onButtonPress: Button {buttonId} pressed.")
    match buttonId:
        case navbuttons.button_1:
            logging.info(f"- first button.")
            moveTostart()
        case navbuttons.button_2:
            logging.info(f"- second button.")
            decrementDisplayIndex()
        case navbuttons.button_3:
            logging.info(f"- third button.")
            incrementDisplayIndex()
        case navbuttons.button_4:
            logging.info(f"- fourth button.")
            moveToEnd()
        case _:
            logging.info(f"- UNKNOWN button.")

try:
    logging.info("Metar Paper start. Press Ctrl+C to stop.")
    # watch the buttons for press events
    navbuttons.watchButtons(onButtonPress)
    paperdraw.initPaperDraw()
    while True:
        resp = req.get(wx_url)
        #print(str(resp.status_code) + ": " + resp.text)
        if resp.status_code == 200:
            paperSettings["metar_list"] = resp.json()
            displayMetars()
        else:
            print(str(resp.status_code) + ": " + resp.text)
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    exit()

finally:
    paperdraw.shutdownPaperDraw()
