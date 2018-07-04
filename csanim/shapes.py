
from PIL import Image,ImageDraw,ImageFont

from io import BytesIO
from subprocess import Popen, PIPE
from .colors import Color
from .framemanager import FrameManager,FrameObject
import sys,os
from .generate_latex import generate_latex

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

class Text(FrameObject):
	def init(self,color,size,x,y,text,align="left"):
		self.color = color
		self.size = size
		self.x = x
		self.y = y
		self.text = text
		self.align = align

	def draw(self,image):
		draw = ImageDraw.Draw(image)
		draw.multiline_text((self.x,self.y), self.text, fill=self.color.get(), font=ImageFont.truetype("./recources/fonts/Monospace.ttf".format(PATH), self.size), anchor=None, spacing=0, align=self.align)

class LatexText(FrameObject):
	def init(self,color,x,y,scale,text,quality=10):
		self.color = color
		self.x = x
		self.y = y
		self.scale = scale
		self.text = text

		self.quality = quality

	def draw(self,image):
		im = generate_latex(self.text,self.color.get(),self.quality)
	
		image.paste(im.resize((int(im.width*self.scale/self.quality),int(im.height*self.scale/self.quality)),Image.BILINEAR), (self.x,self.y))
		# draw = ImageDraw.Draw(image)
		# draw.multiline_text((self.x,self.y), self.text, fill=self.color.get(), font=ImageFont.truetype("./recources/fonts/Monospace.ttf".format(PATH), self.size), anchor=None, spacing=0, align=self.align)
