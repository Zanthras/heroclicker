import os
import sys
import datetime

import PIL
from PIL import Image
import numpy
import pyautogui as gui

import matplotlib
import matplotlib.pyplot as plt

BLACK = (0,0,0)
WHITE = (255,255,255)


class Crab(object):

    def __init__(self, image, ingest=True, location="", box=None):

        self.image = image
        self.maxx, self.maxy = self.image.size
        self.maxx_range = range(self.maxx)
        self.maxy_range = range(self.maxy)
        dt = numpy.dtype({'names': ['r','g','b'], 'formats': [numpy.int16, numpy.int16, numpy.int16]})
        self.array = numpy.zeros([self.maxy, self.maxx], dtype=dt)

        if ingest:
            self.ingestcolor()

        self.score = 0
        self.location = location
        self.box = box

    def ingestcolor(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                self.array[y, x] = self.image.getpixel((x, y))

    def mask(self, maskedimage):

        for y in range(self.maxy):
            for x in range(self.maxx):

                my = tuple(self.array[y, x])
                ot = tuple(maskedimage.array[y, x])

                new = (int(my[0]*(ot[0]/255)), int(my[1]*(ot[1]/255)), int(my[2]*(ot[2]/255)))

                self.array[y, x] = new

    def save(self, name):

        output = Image.new(self.image.mode, self.image.size)
        output.putdata(self.array.flatten().tolist())
        # output.show()
        output.save(name)

    def savegood(self):

        SaveDirectory = r'F:\Documents\Python\heroclicker\clean_fish'
        filename = 'ScreenShot_'+str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_")+"_" + self.location.replace(" ", "_") + '.bmp'
        save_as = os.path.join(SaveDirectory, filename)
        self.image.save(save_as)

    def compare(self, STD, composite):

        scores = []

        for c in "rgb":
            for y in self.maxy_range:
                for x in self.maxx_range:
                    if 0 < STD[y, x] < 11:
                        scores.append(max((64-abs(self.array[y, x][c] - composite.array[y, x][c]))/64, 0))

        self.score = numpy.mean(scores)

    def click(self):

        currentMouseX, currentMouseY = gui.position()

        left, top, right, bottom = self.box

        gui.click(((left + right)) // 2, (top + bottom) // 2)
        gui.moveTo(currentMouseX, currentMouseY)


def producemask():

    masked_file = r"F:\Documents\Python\heroclicker\source\masked_final.bmp"
    masked = Image.open(masked_file)


    mycrab = Crab(image=masked)
    mycrab.ingestcolor()

    for y in range(mycrab.maxy):
        for x in range(mycrab.maxx):
            if tuple(mycrab.array[y, x]) == WHITE:
                mycrab.array[y, x] = BLACK
            else:
                mycrab.array[y, x] = WHITE

    masked_file_dest = r"F:\Documents\Python\heroclicker\source\masked_inverse.bmp"
    masked_final = Image.new(masked.mode, masked.size)
    masked_final.putdata(mycrab.array.flatten().tolist())
    masked_final.save(masked_file_dest)


def parsegood():

    from collections import defaultdict

    DATA = defaultdict(int)

    # masked_file = r"F:\Documents\Python\heroclicker\source\masked_inverse.bmp"
    # masked = Image.open(masked_file)
    # maskedcrab = Crab(masked)

    ref_file = r"F:\Documents\Python\heroclicker\source\masked_inverse.bmp"
    ref = Image.open(ref_file)

    averaged_file = r"F:\Documents\Python\heroclicker\source\averaged_fish.bmp"
    averaged = Crab(Image.new(ref.mode, ref.size))

    std_file = r"F:\Documents\Python\heroclicker\source\std.bmp"
    stdimage = Crab(Image.new(ref.mode, ref.size))

    cleandirectory = r"F:\Documents\Python\heroclicker\clean_fish"
    cleanlist = os.listdir(cleandirectory)


    rgb = {"r": [], "g": [], "b": []}

    for rawfile in cleanlist:

        filename = "\\".join((cleandirectory, rawfile))
        crab = Crab(Image.open(filename))
        for l in "rgb":
            rgb[l].append(crab.array[l])

    stdarray = numpy.zeros([stdimage.maxy, stdimage.maxx])

    for l in "rgb":
        pass
        for array in rgb[l]:
            averaged.array[l] += array
        averaged.array[l] /= (len(cleanlist))
        for y in averaged.maxy_range:
            for x in averaged.maxx_range:
                # if tuple(maskedcrab.array[y, x]) == WHITE:
                    blah = int(numpy.std([array[y, x] for array in rgb[l]]))
                    DATA[blah] += 1
                    stdarray[y, x] += blah
                    stdimage.array[y, x][l] = blah
                # else:
                #     stdimage.array[y, x][l] = WHITE

    stdarray[:] = stdarray[:]/3

    numpy.save("masked_std_array_fish", stdarray)
    # stdimage.save(std_file)
    averaged.save(averaged_file)

    # plt.plot([DATA[x] for x in range(255)])
    # plt.show()


# masked_file = r"F:\Documents\Python\heroclicker\source\masked_inverse.bmp"
# masked = Image.open(masked_file)
#
#
# masked_crab = Crab(image=masked)
#
# gooddirectory = r"F:\Documents\Python\heroclicker\_confirmed"
# cleandirectory = r"F:\Documents\Python\heroclicker\clean"
# trashdirectory = r"F:\Documents\Python\heroclicker\_trash"
#
# goodlist = os.listdir(gooddirectory)
# trashlist = os.listdir(trashdirectory)
#
# c = 0
# for rawfile in goodlist:
#     c+=1
#
#     filename = "\\".join((gooddirectory, rawfile))
#
#     testcrabimage = Image.open(filename)
#     testcrab = Crab(testcrabimage)
#     testcrab.mask(masked_crab)
#     testcrab.save(cleandirectory + "\\" + str(c) + ".bmp")

numpy.set_printoptions(linewidth=300, edgeitems=9)

STD = numpy.load("masked_std_array_fish.npy")

_averaged_file = r"F:\Documents\Python\heroclicker\source\averaged_fish.bmp"
_averaged = Image.open(_averaged_file)

COMPOSITE = Crab(image=_averaged)
# parsegood()




