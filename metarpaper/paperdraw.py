#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime

import logging
logging.basicConfig(level=logging.INFO)

base_path = os.getcwd()
fontsdir = os.path.join(base_path, 'fonts')
logging.info(f" Font Dir: {fontsdir}")
libdir = os.path.join(base_path, 'wavesharelib')
logging.info(f" Lib Dir: {libdir}")
if os.path.exists(libdir):
    sys.path.append(libdir)


from wavesharelib import epd2in7_V2
import time
from PIL import Image,ImageDraw,ImageFont # type: ignore
import traceback
import metartranslate
#264 X 176
epd = epd2in7_V2.EPD()

font10 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 10)
font12 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 12)
font18 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 18)
font24 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 24)
font35 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 35)

def getStringValue(metarObj, fieldName):
    return "" if fieldName not in metarObj else str(metarObj[fieldName])
def getFloatValue(metarObj, fieldName):    
    return float(0) if fieldName not in metarObj else float(metarObj[fieldName])
def getArrayValue(metarObj, fieldName):
    return [] if fieldName not in metarObj else metarObj[fieldName]
def epoch_to_24hr_time(epoch_value: float) -> str:
    # 1. Convert the epoch value (float) to a datetime object.
    # fromtimestamp() uses the system's local timezone for conversion.
    try:
        dt_object = datetime.datetime.fromtimestamp(epoch_value)
    except ValueError as e:
        return f"Error: Invalid epoch value provided. {e}"
    # 2. Format the datetime object to extract the 24-hour time.
    # %H: Hour (24-hour clock) as a zero-padded decimal number.
    # %M: Minute as a zero-padded decimal number.
    time_string = dt_object.strftime("%H:%M")

    return time_string

def initPaperDraw():
    epd.init()
    epd.display_Base_color(epd.GRAY1)
    epd.Clear()
    #canvas.text((10, 0), 'METAR MAP', font = font35, fill = epd.GRAY4)
    #epd.display(epd.getbuffer(imageBase))

def shutdownPaperDraw():
    epd.Clear()
    epd2in7_V2.epdconfig.module_exit(cleanup=True)

def drawMetar(metarInfo):
    logging.info(f"METAR: {getStringValue(metarInfo, "rawOb")}")
    fltCat = getStringValue(metarInfo, "fltCat")
    icaoId = getStringValue(metarInfo, "icaoId")
    icaoName = getStringValue(metarInfo, "name")
    windDir = getStringValue(metarInfo, "wdir")
    windSpeed = getStringValue(metarInfo, "wspd")
    windGust = getStringValue(metarInfo, "wgst")
    visibility = getStringValue(metarInfo, "visib")
    currentWx = getStringValue(metarInfo, "wxString")
    cloudCover = getStringValue(metarInfo, "cover")
    cloudsArray = getArrayValue(metarInfo, "clouds")
    altimeter = getFloatValue(metarInfo, "altim") / 33.864
    temp = getFloatValue(metarInfo, "temp")
    dewp = getFloatValue(metarInfo, "dewp")
    epochTime = getFloatValue(metarInfo, "obsTime")

    windDesc = "Unknown" 
    visibilityDesc = "Unkown"
    currWeatherDesc = ""
    cloudSummaryDesc = ""
    cloudLayerDesc = []
    altimeterDesc = ""
    tempDesc = ""
    timeDesc = ""

    if windDir != "":
        if windSpeed == "0":
            windDesc = "Calm"
        else:
            windDesc = f"{windDir}° @ {windSpeed} KTS"
            if windGust != "":
                windDesc += f" Gusting {windGust} KTS"
    
    if visibility != "":        
        visibilityDesc = visibility.replace("+", "") + " Miles"
        if "+" in visibility:
            visibilityDesc = "More Than " + visibilityDesc

    if currentWx != "":
        currWeatherDesc = metartranslate.translateWeather(currentWx)
    
    if cloudCover != "":
        cloudSummaryDesc = metartranslate.translateSky(cloudCover)

    if cloudsArray is not None and len(cloudsArray) > 0:
        for cloudLayer in cloudsArray:
            clDesc = metartranslate.translateCloudLayer(cloudLayer)
            cloudLayerDesc.append(clDesc)
            topDesc =  metartranslate.translateCloudLayerTop(cloudLayer)
            if topDesc != "":
                cloudLayerDesc.append(topDesc)

    if altimeter != "":
        altimeterDesc = f"{altimeter:.2f}"
        
    if temp != "":
        tempDesc = f"Tempurature: {temp:.0f}°C  Dew Point: {dewp:.0f}°C"

    if epochTime > 0:
        timeDesc = epoch_to_24hr_time(epochTime)
        
    logging.info(f"drawMetar > {icaoId} - {icaoName}")
    imageBase = Image.new('1', (epd.height, epd.width), epd.GRAY1)
    canvas = ImageDraw.Draw(imageBase)
    # first line airport and Flt Cat
    canvas.text((10, 0), icaoId, font = font35, fill = epd.GRAY4)
    tpos = 200 if len(fltCat) > 3 else 220
    canvas.text((tpos, 6), fltCat, font = font24, fill = epd.GRAY4)
    # second line is name of airport
    canvas.text((10, 35), icaoName, font = font12, fill = epd.GRAY4)
    # draw split line    
    canvas.line(( 0,  51,  epd.height, 51), fill = epd.GRAY4)    
    # winds    
    canvas.text((10, 52), f"Wind: {windDesc}", font = font12, fill = epd.GRAY4)
    # visibility
    canvas.text((10, 66), f"Visibilty: {visibilityDesc}", font = font12, fill = epd.GRAY4)
    # tempurature
    canvas.text((10, 78), tempDesc, font = font12, fill = epd.GRAY4)
    # weather
    maxCloudLines = 5
    offset = 0
    rightset = 0
    if (currWeatherDesc != ""):
        maxCloudLines -= 1
        offset += 12
        canvas.text((10, 90), f"Weather: {currWeatherDesc}", font = font12, fill = epd.GRAY4)    
    if len(cloudLayerDesc) > 0:
        for cloudLayer in cloudLayerDesc:
            if maxCloudLines <= 0:
                break
            maxCloudLines -= 1
            if rightset > 0:
                canvas.text((10 + rightset, 90 + offset), f"{cloudLayer}", font = font12, fill = epd.GRAY4)
            else: 
                canvas.text((10, 90 + offset), f"Clouds: {cloudLayer}", font = font12, fill = epd.GRAY4)
                rightset += 44
            offset += 12
    else:
        canvas.text((10, 90 + offset), f"Clouds: {cloudSummaryDesc}", font = font12, fill = epd.GRAY4)
        offset += 12

    # altimeter
    canvas.text((10, 90 + offset), f"Altimeter: {altimeterDesc}", font = font12, fill = epd.GRAY4)
    
    # time at bottome
    canvas.text((10, epd.width - 13), f"Observed at {timeDesc}", font = font12, fill = epd.GRAY4)

    logging.info("=> Display")
    epd.display(epd.getbuffer(imageBase))
  
