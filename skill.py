import datetime

from PIL import Image
import numpy
import pyautogui as gui

class Skill(object):

    def __init__(self, name, imgbox, image=None, number=0):

        self.name = name
        self.image = image
        self.box = imgbox
        self.number = number
        self.state = 0
        self.maxx = self.box[2] - self.box[0]
        self.maxy = self.box[3] - self.box[1]
        self.maxx_range = range(self.maxx)
        self.maxy_range = range(self.maxy)
        dt = numpy.dtype({'names': ['r','g','b'], 'formats': [numpy.int16, numpy.int16, numpy.int16]})
        self.array = numpy.zeros([self.maxy, self.maxx], dtype=dt)
        self.base = numpy.zeros([self.maxy, self.maxx], dtype=dt)
        self.loadbase()
        self.last_collect = None
        self.is_unlocked = False

    def click(self):

        currentMouseX, currentMouseY = gui.position()

        gui.click((self.box[0] + self.box[2]) // 2, (self.box[1] + self.box[3]) // 2)
        gui.moveTo(currentMouseX, currentMouseY)

    def setstate(self):

        scores = []

        for c in "rgb":
            for y in self.maxy_range:
                for x in self.maxx_range:
                    scores.append((255 - abs(self.array[y, x][c] - self.base[y, x][c])) / 255)

        score = numpy.mean(scores)
        if score > .98:
            self.state = 1
            self.is_unlocked = True
            self.last_collect = datetime.datetime.now()
        elif score > .7:
            self.state = 0
            self.is_unlocked = True
            self.last_collect = datetime.datetime.now()
        else:
            self.state = None
            self.is_unlocked = False


    def ingestcolor(self, image):

        #image is assumed to be the entire game screen

        for y in range(self.maxy):
            for x in range(self.maxx):
                self.array[y, x] = image.getpixel((self.box[0] + x, self.box[1] + y))

    def loadbase(self):

        basestatefile = Image.open("skills/" + self.name + ".bmp")
        for y in range(self.maxy):
            for x in range(self.maxx):
                self.base[y, x] = basestatefile.getpixel((x, y))

    def saveasbase(self, gs):

        self.image = gs.screen.crop(self.box)
        self.image.save(self.name + ".bmp")

    def __str__(self):

        humanstate = ""
        if self.state is None:
            humanstate = "-Unavailable"
        elif self.state == 1:
            humanstate = "-Ready"
        else:
            humanstate = "-Charging"

        return self.name + humanstate

    def __repr__(self):

        return self.__str__()