from PIL import Image,ImageDraw,ImageOps

from subprocess import Popen, PIPE
import sys,os
from .colors import Color



class VideoMaker:
	def __init__(self,fps,name):
		self.fps = fps
		self.name = name
		print("starting image stream....")

		self.ffmpegprocess =  Popen([
			'ffmpeg', 
			'-y',
			'-f', 'image2pipe',
			'-pix_fmt', 'rgba',
			'-vcodec', 'png', 
			'-r', str(self.fps), 
			'-i', '-', 
			'-vcodec', 'mpeg4', 
			'-qscale', '1', 
			'-r', str(self.fps), 
			str(self.name),
			'-loglevel', 'error',
			'-an'], 
			stdin=PIPE)


	def add_image(self,im):
		im.save(self.ffmpegprocess.stdin, 'PNG')

	def finish(self):
		self.ffmpegprocess.stdin.close()
		print("stopping image stream...")
		self.ffmpegprocess.wait()

	def kill(self):
		self.ffmpegprocess.kill()

class BaseFrameManager:
	"""
	subclasses must implement new_frame() and handlers().
	"""
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
		self.saverequests = []

	def new_frame(self):
		raise NotImplemented

	def set_background(self,color):
		self.background = color


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

	def save(self,name):
		self.saverequests.append(name)

class FrameManager(BaseFrameManager):

	def new_frame(self):
		currentimage = Image.new("RGB", (self.width,self.height), self.background.get())
		self.handlers(currentimage)
		
		self.videomaker.add_image(currentimage)
		for i in self.saverequests:
			currentimage.save(i,"PNG")
		saverequests = []

	def handlers(self,currentimage):
		for i in self.frameevents:
			if i == self.framecounter:
				self.frameevents[i](self)

		for i in self.frameobjects:
			i.update(currentimage)



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