#!/usr/bin/python3

from PIL import Image,ImageDraw
from subprocess import Popen, PIPE

import sys,os
from colors import Color

class VideoMaker:
	def __init__(self,fps,name,Q="high"):
		self.fps = fps
		self.name = name
		self.Q = Q
		print("starting image stream....")
		if self.Q == "high":
			self.ffmpegprocess =  Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', str(self.fps), '-i', '-', '-vcodec', 'mpeg4', '-qscale', '5', '-r', str(self.fps), str(self.name)], stdin=PIPE)
		elif self.Q == "low":
			self.ffmpegprocess =  Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', str(self.fps), '-i', '-', '-vcodec', 'mpeg4', '-qscale', '5', '-r', str(self.fps), str(self.name)], stdin=PIPE)
		else:
			raise ValueError("Q must be high or low")

	def add_image(self,im):
		if self.Q == "high":
			im.save(self.ffmpegprocess.stdin, 'PNG')
		elif self.Q == "low":
			im.save(self.ffmpegprocess.stdin, 'JPEG')

	def finish(self):
		self.ffmpegprocess.stdin.close()
		print("stopping image stream...")
		self.ffmpegprocess.wait()

	def kill(self):
		self.ffmpegprocess.kill()

class FrameObject:
	visible = True
	duration = -1

	def __init__(self,duration,*args,**kwargs):
		self.duration = duration
		self.init(*args,**kwargs)

	def init(self,*args,**kwargs):
		raise NotImplemented

	def update(self,currentimage):
		if self.duration > 0:
			self.duration -= 1
		if self.duration == 0:
			self.visible = False
		if self.visible:
			self.draw(currentimage)

	#must be implemented by subclass
	def draw(self,image):
		raise NotImplemented

	def setvisible(self,val):
		self.visible = val

class Ellipse(FrameObject):
	def init(self,color,x,y,rx,ry=None):
		self.color = color
		if ry == None:
			ry = rx
		self.x1 = x - rx
		self.y1 = y - ry
		self.x2 = x + rx
		self.y2 = y + ry

	def draw(self,image):
		draw = ImageDraw.Draw(image)
		draw.ellipse((self.x1,self.y1,self.x2,self.y2), fill=self.color.get())

class Rectangle(FrameObject):
	def init(self,color,x,y,w,h):
		self.color = color
		if h == None:
			h = w
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	def draw(self,image):
		draw = ImageDraw.Draw(image)
		draw.rectangle((self.x1,self.y1,self.x2,self.y2), fill=self.color.get())

class Line(FrameObject):
	def init(self,color,x1,y1,x2,y2):
		self.color = color
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

	def draw(self,image):
		draw = ImageDraw.Draw(image)
		draw.line((self.x1,self.y1,self.x2,self.y2), fill=self.color.get())

class Polygon(FrameObject):
	def init(self,color,*args):
		self.color = color
		self.coords = args

	def draw(self,image):
		draw = ImageDraw.Draw(image)
		draw.polygon(self.coords, fill=self.color.get())


class FrameManager:

	def __init__(self,fps,width,height,name):
		self.width = width
		self.height = height

		self.videomaker = VideoMaker(fps,name)
		self.reset()
		self.frameevents = {}

		def handle_exception(exctype,value,tb):
			print("ERROR finishing tasks")
			self.videomaker.kill()
			sys.__excepthook__(exctype, value, tb)

		sys.excepthook = handle_exception


	def reset(self):
		self.background = Color(0,0,0)
		self.framecounter = 0	
		self.frameobjects = []

	def new_frame(self):
		currentimage = Image.new("RGB", (self.width,self.height), self.background.get())
		self.handlers(currentimage)
		self.videomaker.add_image(currentimage)

	def set_background(self,color):
		self.background = color

	def handlers(self,currentimage):
		for i in self.frameevents:
			if i == self.framecounter:
				self.frameevents[i](self)

		for i in self.frameobjects:
			i.update(currentimage)

	def finish(self):
		self.videomaker.finish()

	def run(self,frames):
		print(self.frameevents)
		for i in range(frames):
			print('rendering: frame {}/{} ({:.1%})\r'.format(self.framecounter,frames,self.framecounter/frames),end="")
			self.new_frame()
			self.framecounter+=1
		self.finish()

	def frame(self,num):
		def retfunc(func):
			self.frameevents[num] = func
		return retfunc

	def second(self,num):
		def retfunc(func):
			self.frameevents[num*self.videomaker.fps] = func
		return retfunc		

	def draw(self,fobject):
		self.frameobjects.append(fobject)

#https://en.wikipedia.org/wiki/List_of_common_resolutions
f = FrameManager(60,1920,1080,"video.mp4")
f.set_background(Color(0, 130, 200))

@f.second(5)	
def second5(manager):
	manager.set_background(Color(0, 128, 128))
	manager.draw(Polygon(120,Color(128, 0, 0),300,300,400,400,300,400))

f.run(60*10)