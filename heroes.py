__author__ = 'Joel'

import datetime
import time

import pyautogui as gui
from pytesseract import image_to_string

class Hero(object):

    buy_coord_offset = (-30, 60)

    def __init__(self, base, gs):
        self.gs = gs
        self.base = base
        self.panelheight = 0
        self.namebox = (0,0,0,0)
        self.name = ""
        self.level = 0
        self.buy_coord = (0,0)
        self.check_interval = datetime.timedelta(seconds=1)
        self.lastcheck = datetime.datetime.now()
        self.intervals = []
        self.isvisible = True
        self.ishidden = False
        self._update_buy_coord()
        self.guilded = False
        self.order = 0

    def _update_buy_coord(self):

        self.buy_coord = (self.base[0] + self.buy_coord_offset[0], self.base[1] + self.buy_coord_offset[1])

    def ocr_name(self):

        # because buying produces visual flair that covers the name... halt ocr after buys...
        if datetime.datetime.now() - self.gs.lastherobuy < datetime.timedelta(seconds=2):
            time_left = datetime.timedelta(seconds=2) - (datetime.datetime.now() - self.gs.lastherobuy)
            time.sleep(time_left.total_seconds())

        textcolor = (102, 51, 204), (254, 254, 254)

        crop = (self.base[0], self.base[1]+5, self.base[0]+370, self.base[1]+37)
        myimage = self.gs.screen.crop(crop)

        mx = crop[2] - crop[0]
        my = crop[3] - crop[1]

        for y in range(my):
            for x in range(mx):
                if myimage.getpixel((x, y)) in textcolor:
                    myimage.putpixel((x, y), (0,0,0))
                else:
                    myimage.putpixel((x, y), (255,255,255))

        self.name = image_to_string(image=myimage)
        self.name = self.name.replace("<", "c")
        if self.name.find("Fares") > -1:
            self.name = self.name.replace("Fares:", "Forest")
        elif self.name == "Amenhatep":
            self.name = "Amenhotep"
        elif self.name == "Frastleaf":
            self.name = "Frostleaf"
        elif self.name.find("."):
            self.name = self.name.replace(".", ",")
        if self.name not in order:
            print("hero name i dont know", self.name)
        else:
            self.order = order[self.name]

    def ocr_level(self):

        textcolor = (102, 51, 204), (254, 254, 254)

        crop = (self.base[0]+220, self.base[1]+40, self.base[0]+370, self.base[1]+70)
        myimage = self.gs.screen.crop(crop)


        mx = crop[2] - crop[0]
        my = crop[3] - crop[1]

        for y in range(my):
            for x in range(mx):
                if myimage.getpixel((x, y)) in textcolor:
                    myimage.putpixel((x, y), (0,0,0))
                else:
                    myimage.putpixel((x, y), (255,255,255))

        level_raw = image_to_string(image=myimage)
        level_raw = level_raw.replace("â€˜!", "1")
        level = ""
        for char in level_raw:
            try:
                int(char)
                level += char
            except:
                pass
        if level:
            self.level = int(level)

    def can_buy(self):

        buy = (253,253,0)
        dont = (254,135,67)
        box = (self.base[0]-145, self.base[1]+102, self.base[0]-30, self.base[1]+103)

        for x in range(box[2]-box[0]):
            pix = self.gs.screen.getpixel((box[0]+x, box[1]))
            if pix == buy:
                return True
            elif pix == dont:
                return False
        else:
            return False

    def buy_timer(self):

        if len(self.intervals) < 2:
            if datetime.datetime.now() - self.lastcheck > self.check_interval:
                self.lastcheck = datetime.datetime.now()
                return True
            else:
                return False

    def setvisible(self, base=None, level=None, init=False):

        if not init:
            self.base = base
            self.level = level
            self._update_buy_coord()
        self.isvisible = True
        self.ishidden = False

        if self not in self.gs.hero.visible:
            self.gs.hero.visible.append(self)

    def sethidden(self):
        self.base = (0,0)
        self.buy_coord = (0,0)
        self.isvisible = False
        self.ishidden = True

        if self in self.gs.hero.visible:
            self.gs.hero.visible.remove(self)

    def try_buy(self, amount):

        try:
            if self.buy_timer():
                if amount == 25:
                    if not self.gs.infocus:
                        return False
                    gui.keyDown(key="z")
                    time.sleep(.2)
                    self.gs.update_screen()
                if self.can_buy():
                    self.check_interval *= .75
                    self.gs.click(self.buy_coord)
                    self.gs.lastherobuy = datetime.datetime.now()
                    return True
                else:
                    self.check_interval *= 2
                    if self.check_interval > datetime.timedelta(minutes=30):
                        self.check_interval = datetime.timedelta(minutes=30)
        finally:
            if amount == 25:
                gui.keyUp(key="z")
        return False

    def __str__(self):

        return self.name + ":" + str(self.level)

    def __repr__(self):

        return self.__str__()


order = {'Cid, the Helpful Adventurer':1,
         'Treebeast':2,
         'Ivan, the Drunken Brawler':3,
         'Brittany, Beach Princess':4,
         'The Wandering Fisherman':5,
         'Betty Clicker':6,
         'The Masked Samurai':7,
         'Leon':8,
         'The Great Forest Seer':9,
         'Alexa, Assassin':10,
         'Natalia, Ice Apprentice':11,
         'Mercedes, Duchess of Blades':12,
         'Bobby, Bounty Hunter':13,
         'Broyle Lindeoven, Fire Mage':14,
         "Sir George II, King's Guard":15,
         'King Midas':16,
         'Referi Jerator, Ice Wizard':17,
         'Abaddon':18,
         'Ma Zhu':19,
         'Amenhotep':20,
         'Beastlord':21,
         'Athena, Goddess of War':22,
         'Aphrodite, Goddess of Love':23,
         'Shinatobe, Wind Deity':24,
         'Grant, The General':25,
         'Frostleaf':26,
         'Dread Knight':27,
         'Atlas':28,
         'Terra':29,
         'Phthalo':30,
         'Orntchya Gladeye, Didensy':31,
         'Lilin':32,
         'Cadmia':33,
         'Alabaster':34,
         'Astraea':35,}