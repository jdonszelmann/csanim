from PIL import Image,ImageDraw

from subprocess import Popen, PIPE
import sys,os
from colors import Color

from pyglet.gl import *
import ctypes,pyglet

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

class BaseFrameManager:

	def __init__(self,fps,width,height,name,Q="high",AA=2):

		self.scale = AA 
	

		self.width = width*self.scale
		self.height = height*self.scale

		self.videomaker = VideoMaker(fps,name,Q)
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
		
		currentimage = currentimage.resize((self.width//self.scale,self.height//self.scale), Image.ANTIALIAS)

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


class GLFrameManager(BaseFrameManager):

	FBO = None

	def SetScreen(self, left, top, right, bottom):
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity();
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(left,right,bottom,top,-1.0,1.0)
		glMatrixMode(GL_MODELVIEW)

	def SetRenderTarget(self,texture=None):
		if not texture:
			# use screen when no texture was specified
			glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
			glViewport(0,0,self.width,self.height)
			SetScreen(0,0,self.width,self.height)
		else:
			# create FBO object once
			if not self.FBO:
				self.FBO = GLuint()
				glGenFramebuffersEXT(1, ctypes.byref(self.FBO))

			# bind the frame buffer
			glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.FBO)

			# check that the texture has a depth render-buffer (not strictly neccessary)
			try: _t = texture.DepthRB
			except:
				texture.DepthRB = GLuint()
				glGenRenderbuffersEXT(1, ctypes.byref(texture.DepthRB))
				glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, texture.DepthRB)
				glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT16, texture.width, texture.height)

			# bind texture and depth buffer to FBO
			glBindTexture(texture.target, texture.id)
			glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, texture.target, texture.id, 0)
			glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, texture.DepthRB)

			# clear FBO and set some GL defaults
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glEnable(GL_DEPTH_TEST)
			glDepthFunc(GL_LEQUAL)
			glClearDepth(1.0)
			glClearColor(*(self.background.getfloat()), 0.0)  # set clear color yourself!
			glViewport(0,0, texture.width, texture.height)
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			SetScreen(0, 0, texture.width, texture.height)

			# simple error checking
			status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
			assert status == GL_FRAMEBUFFER_COMPLETE_EXT

	def new_frame(self):
		pass

	def handlers(self,currentimage):
		pass
		# for i in self.frameevents:
		# 	if i == self.framecounter:
		# 		self.frameevents[i](self)

		# for i in self.frameobjects:
		# 	i.update(currentimage)


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