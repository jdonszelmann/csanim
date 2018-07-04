#!/usr/bin/python3

from PIL import Image,ImageDraw


import sys,os
from colors import Color
from framemanager import FrameManager
from shapes import *



#https://en.wikipedia.org/wiki/List_of_common_resolutions
f = FrameManager(60,1920,1080,"video.mp4") #1080p 60fps
f.set_background(Color(0, 0, 0))
@f.second(1)	
def second1(manager):

	# manager.draw(Polygon(120,Color(128, 0, 0),600,600,1000,1000,900,1000))
	manager.draw(LatexText(120,
		Color(255,255,255),
		100,100,#x,y
		1.5,#scale
		r'\int_0^1 e^x\,dx' #latex
		))

@f.second(3)	
def second3(manager):

	# manager.draw(Polygon(120,Color(128, 0, 0),600,600,1000,1000,900,1000))
	manager.draw(LatexText(120,
		Color(255,255,255),
		100,100,#x,y
		1.5,#scale
		r"""
		M =
		\begin{bmatrix}
		 1&  3& \\ 
		 2&  4& 
		\end{bmatrix}
		"""
		))

@f.second(5)	
def second5(manager):

	# manager.draw(Polygon(120,Color(128, 0, 0),600,600,1000,1000,900,1000))
	manager.draw(LatexText(120,
		Color(255,255,255),
		100,100,#x,y
		1.5,#scale
		r'f\left ( x \right ) = \sqrt[3]{x}' #latex
		))


f.run(60*10)