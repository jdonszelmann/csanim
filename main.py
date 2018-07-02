#!/usr/bin/python3

from PIL import Image,ImageDraw


import sys,os
from colors import Color
from framemanager import FrameManager
from shapes import *



#https://en.wikipedia.org/wiki/List_of_common_resolutions
f = FrameManager(60,1920,1080,"video.mp4","low",AA=1) #1080p 60fps
f.set_background(Color(0, 130, 200))
@f.second(5)	
def second5(manager):
	manager.set_background(Color(0, 128, 128))
	manager.draw(Polygon(120,Color(128, 0, 0),900,900,1200,1200,900,1200))

f.run(60*10)