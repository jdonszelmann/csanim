
# CSanim

It's like manim (the program Grant uses for his channel 3blue1brown) but for computer science! special thanks to Grant Sanderson (3blue1brown, https://github.com/3b1b/manim)


Csanim generates videos. Many test videos can be found on our youtube channel [thekeychain](https://www.youtube.com/channel/UCUvhgZVZjBGB5NvLH_M-n9g)


## installation:

To install csanim, clone this repository, and run the install.sh script. (commands below) 
This script is only tested for Ubuntu.
To install csanim on other systems install the following packages:

- ffmpeg
- python3
- pyhon3-pip
- python3-opengl (or use pip3 install pyopengl)
- dvipng
- texlive
- texlive-latex-extra

installation commands: (Ubuntu): 
```bash
git clone https://github.com/jonay2000/csanim
cd csanim
./install.sh
```

## usage:

To start, import csanim with 
```python
from csanim import *
```

After this import, you can start a new video by creating a frame manager:

```python
#FrameManager(fps,width,height,name)
f = FrameManager(60,1920,1080,"video.mp4") #1080p 60fps
f.set_background(Color(0, 0, 0))
```

Now you can start defining points in the video at which some change to the seen will happen.
This can be done with the @f.second() or @f.frame() decorator.

f.second(sec) will take 1 argument defining on which second the function must be called (this can be a float)
f.frame(frame)  will take 1 argument defining on which frame the function must be called (this must be an integer)

example:
```python
@f.second(1)	
def second1(manager):

	manager.draw(LatexText(120, #visible for 120 frames (2 seconds on 60fps)
		Color(255,255,255),		#color: white
		100,100,#x,y 			#draw on (100,100)
		1.5,#scale				#scale up by 50%
		r'\int_0^1 e^x\,dx' 	#latex string (integral from 0 to 1 of e^x dx)
		))

```
now you can start rendering this video by calling the run() method of thye framemanager:

```python
f.run(2*60) #run takes 1 argument specifying how many frames should be rendered. Since the video is on 60 fps
#it should run 120 frames for 2 seconds. After the first second the Latex text will be visible
```

this last action may take some time, depending on the complexity of the scene. There are currently NO optimizations so slow might mean very slow

