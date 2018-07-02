
from PIL import Image,ImageDraw


from subprocess import Popen, PIPE
from colors import Color
from framemanager import FrameManager,FrameObject

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
