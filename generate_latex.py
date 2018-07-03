
import sys,os
from PIL import Image
import atexit


"""
this module will generate a png image representation of a latex string. 
this function is very expensive, use with care. a caching system is built in
so calling it multiple times with the same latex string will not take as much time
as calling it with different strings 
"""

latexdir = "./latex"

def all_done():
	if not os.path.exists(latexdir):
		return
	for i in os.listdir(latexdir):
		os.remove(os.path.join(latexdir,i))
	os.rmdir(latexdir)


atexit.register(all_done)


cache = {}

def generate_latex(texstring,color,quality):
	if not os.path.exists(latexdir):
		os.mkdir(latexdir)

	if texstring in cache:
		return Image.open(cache[texstring])

	name = "latexfile"

	latexstring = r"""
	\documentclass{{standalone}}
	\pagestyle{{empty}}
	\usepackage{{xcolor}}

	\definecolor{{main}}{{RGB}}{{ {},{},{} }}

	\begin{{document}}
	\color{{main}}
	$$$
	{}
	$$$

	\end{{document}}


	""".format(*color,texstring)

	f = open(name + ".tex","w")
	f.write(latexstring)
	f.close()


	os.system("pdflatex -interaction=batchmode -output-format=dvi {}".format(name + ".tex"))

	os.system("dvipng -D {}000 -bg Transparent {}".format(str(quality),name + ".dvi"))

	im = Image.open(name + "1.png")
	os.remove(name + ".tex")
	os.remove(name + ".log")
	os.remove(name + ".aux")
	os.remove(name + ".dvi")
	os.remove(name + "1.png")

	name = os.path.join(latexdir,str(len(cache)) + ".png")
	im.save(name)
	cache[texstring] = name

	return im


if __name__ == '__main__':
	#just some tests. with 1 call it takes 0.221 seconds
	#with 2 calls it takes 0.219 seconds
	generate_latex(r'\int_0^1 e^x\,dx')
	generate_latex(r'\int_0^1 e^x\,dx')

