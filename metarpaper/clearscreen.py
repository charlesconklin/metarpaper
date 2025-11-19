#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import paperdraw

logging.basicConfig(level=logging.INFO)

try:
    paperdraw.initPaperDraw()
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    exit()
finally:
    paperdraw.shutdownPaperDraw()
