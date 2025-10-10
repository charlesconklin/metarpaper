#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime

base_path = os.getcwd()
picdir = os.path.join(base_path, 'pic')
libdir = os.path.join(base_path, 'wavesharelib')

if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from wavesharelib import epd2in7_V2
import time
from PIL import Image,ImageDraw,ImageFont # type: ignore
import traceback
import metartranslate

logging.basicConfig(level=logging.INFO)
#264 X 176
epd = epd2in7_V2.EPD()
imageBase = Image.new('1', (epd.height, epd.width), epd.GRAY1)  # 255: clear the frame
canvas = ImageDraw.Draw(imageBase)

font10 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 10)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)

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
    altimeter = str(round(getFloatValue(metarInfo, "altim") / 33.864, 2))
    temp = getFloatValue(metarInfo, "temp")
    dewp = getFloatValue(metarInfo, "dewp")
    epochTime = getFloatValue(metarInfo, "obsTime")

    # = getStringValue(metarInfo, "")
    windDesc = "Unknown" 
    visibilityDesc = "Unkown"
    currWeatherDesc = ""
    cloudSummaryDesc = ""
    cloudLayerDesc = []
    altimeterDesc = ""
    tempDesc = ""
    timeDesc = ""

    if windDir != "":
        windDesc = f"{windDir} @ {windSpeed}"
        if windGust != "":
            windDesc += f" Gusting {windGust}"
    
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

    if altimeter != "":
        altimeterDesc = altimeter
    
    if temp != "":
        tempDesc = f"Tempurature: {str(int(round(temp, 0)))}   Dew Point: {str(int(round(dewp, 0)))}"

    if epochTime > 0:
        timeDesc = epoch_to_24hr_time(epochTime)


    logging.info(f"drawMetar > {icaoId} - {icaoName}")
    canvas.rectangle((0, 0, epd.height, epd.width), fill = epd.GRAY1)
    # first line airport and Flt Cat
    canvas.text((10, 0), icaoId, font = font35, fill = epd.GRAY4)
    tpos = 200 if len(fltCat) > 3 else 220
    canvas.text((tpos, 6), fltCat, font = font24, fill = epd.GRAY4)
    # second line is name of airport
    canvas.text((10, 35), icaoName, font = font12, fill = epd.GRAY4)
    # draw split line
    #canvas.line(( epd.height/2, 50,  epd.height/2,  epd.width), fill = epd.GRAY4)    
    # winds
    
    canvas.text((10, 52), f"Wind: {windDesc}", font = font12, fill = epd.GRAY4)
    
    canvas.text((10, 66), f"Visibilty: {visibilityDesc}", font = font12, fill = epd.GRAY4)
    canvas.text((10, 78), tempDesc, font = font12, fill = epd.GRAY4)
    canvas.text((10, 90), f"Altimeter: {altimeterDesc}", font = font12, fill = epd.GRAY4)
    offset = 0
    if (currWeatherDesc != ""):
        offset += 12
        canvas.text((10, 102), f"Weather: {currWeatherDesc}", font = font12, fill = epd.GRAY4)    
    if len(cloudLayerDesc) > 0:
        for cloudLayer in cloudLayerDesc:
            canvas.text((10, 102 + offset), f"Clouds: {cloudLayer}", font = font12, fill = epd.GRAY4)
            offset += 12
    else:
        canvas.text((10, 102 + offset), f"Clouds: {cloudSummaryDesc}", font = font12, fill = epd.GRAY4)

    epd.display_Fast(epd.getbuffer(imageBase))
    


# try:
#     resp = req.get(wx_url)
#     if resp.status_code == 200:
#         metar_array = resp.json

    
#     #########################
#     logging.info("epd2in7 Demo")   
#     epd = epd2in7_V2.EPD()
    
#     '''2Gray(Black and white) display'''
#     logging.info("init and Clear")
#     epd.init()
#     epd.Clear()
#     font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
#     font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
#     font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    
#     # Quick refresh
#     logging.info("Quick refresh demo")
#     epd.init_Fast()
#     # Drawing on the Vertical image
#     logging.info("1.Drawing on the Vertical image...")
#     Limage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
#     draw = ImageDraw.Draw(Limage)
#     draw.text((2, 0), 'hello world', font = font18, fill = 0)
#     draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
#     draw.line((10, 90, 60, 140), fill = 0)
#     draw.line((60, 90, 10, 140), fill = 0)
#     draw.rectangle((10, 90, 60, 140), outline = 0)
#     draw.line((95, 90, 95, 140), fill = 0)
#     draw.line((70, 115, 120, 115), fill = 0)
#     draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
#     draw.rectangle((10, 150, 60, 200), fill = 0)
#     draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
#     epd.display_Fast(epd.getbuffer(Limage))
#     time.sleep(2)
    
#     logging.info("2.read bmp file")
#     Himage = Image.open(os.path.join(picdir, '2in7.bmp'))
#     epd.display_Fast(epd.getbuffer(Himage))
#     time.sleep(2)
    
#     # Normal refresh
#     logging.info("Normal refresh demo")
#     epd.init()
#     logging.info("3.read bmp file on window")
#     Himage2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
#     bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
#     Himage2.paste(bmp, (50,10))
#     epd.display(epd.getbuffer(Himage2))
#     time.sleep(2)
    
#     # Drawing on the Horizontal image
#     logging.info("4.Drawing on the Horizontal image...")
#     Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
#     draw = ImageDraw.Draw(Himage)
#     draw.text((10, 0), 'hello world', font = font24, fill = 0)
#     draw.text((150, 0), u'微雪电子', font = font24, fill = 0)    
#     draw.line((20, 50, 70, 100), fill = 0)
#     draw.line((70, 50, 20, 100), fill = 0)
#     draw.rectangle((20, 50, 70, 100), outline = 0)
#     draw.line((165, 50, 165, 100), fill = 0)
#     draw.line((140, 75, 190, 75), fill = 0)
#     draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
#     draw.rectangle((80, 50, 130, 100), fill = 0)
#     draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
#     epd.display_Base(epd.getbuffer(Himage))
#     time.sleep(2)
    
#     # partial update
#     logging.info("5.show time")
#     epd.init()   
#     '''
#     # If you didn't use the EPD_2IN7_V2_Display_Base() function to refresh the image before,
#     # use the EPD_2IN7_V2_Display_Base_color() function to refresh the background color, 
#     # otherwise the background color will be garbled 
#     '''
#     # epd.display_Base_color(0xff)
#     # Himage = Image.new('1', (epd.height ,epd.width), 0xff)
#     # draw = ImageDraw.Draw(time_image)
#     num = 0
#     while (True):
#         draw.rectangle((10, 110, 120, 150), fill = 255)
#         draw.text((10, 110), time.strftime('%H:%M:%S'), font = font24, fill = 0)
#         newimage = Himage.crop([10, 110, 120, 150])
#         Himage.paste(newimage, (10,110)) 
#         epd.display_Partial(epd.getbuffer(Himage),110, epd.height - 120, 150, epd.height - 10)
#         num = num + 1
#         if(num == 10):
#             break
    
#     # epd.init() 
#     # epd.clear()
#     # epd.display_Base_color(0xff)
#     # Himage = Image.new('1', (epd.width ,epd.height), 0xff)
#     # draw = ImageDraw.Draw(Himage)
#     # num = 0
#     # while (True):
#         # draw.rectangle((10, 10, 120, 50), fill = 255)
#         # draw.text((10, 10), time.strftime('%H:%M:%S'), font = font24, fill = 0)
#         # newimage = Himage.crop([10, 10, 120, 50])
#         # Himage.paste(newimage, (10,10)) 
#         # epd.display_Partial(epd.getbuffer(Himage),10, 10, 120, 50)
#         # num = num + 1
#         # if(num == 10):
#             # break
    
#     '''4Gray display'''
#     logging.info("4Gray display--------------------------------")
#     epd.Init_4Gray()
    
#     Limage = Image.new('L', (epd.width, epd.height), 0)  # 255: clear the frame
#     draw = ImageDraw.Draw(Limage)
#     draw.text((20, 0), u'微雪电子', font = font35, fill = epd.GRAY1)
#     draw.text((20, 35), u'微雪电子', font = font35, fill = epd.GRAY2)
#     draw.text((20, 70), u'微雪电子', font = font35, fill = epd.GRAY3)
#     draw.text((40, 110), 'hello world', font = font18, fill = epd.GRAY1)
#     draw.line((10, 140, 60, 190), fill = epd.GRAY1)
#     draw.line((60, 140, 10, 190), fill = epd.GRAY1)
#     draw.rectangle((10, 140, 60, 190), outline = epd.GRAY1)
#     draw.line((95, 140, 95, 190), fill = epd.GRAY1)
#     draw.line((70, 165, 120, 165), fill = epd.GRAY1)
#     draw.arc((70, 140, 120, 190), 0, 360, fill = epd.GRAY1)
#     draw.rectangle((10, 200, 60, 250), fill = epd.GRAY1)
#     draw.chord((70, 200, 120, 250), 0, 360, fill = epd.GRAY1)
#     epd.display_4Gray(epd.getbuffer_4Gray(Limage))
#     time.sleep(2)
    
#     #display 4Gra bmp
#     Himage = Image.open(os.path.join(picdir, '2in7_Scale.bmp'))
#     epd.display_4Gray(epd.getbuffer_4Gray(Himage))
#     time.sleep(2)

#     logging.info("Clear...")
#     epd.init()   
#     epd.Clear()
#     logging.info("Goto Sleep...")
#     epd.sleep()
        
# except IOError as e:
#     logging.info(e)
    
# except KeyboardInterrupt:    
#     logging.info("ctrl + c:")
#     epd2in7_V2.epdconfig.module_exit(cleanup=True)
#     exit()
