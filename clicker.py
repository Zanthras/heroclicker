__author__ = 'Joel'
import os
import sys
import datetime
import time
import subprocess
import PIL
from PIL import ImageGrab, Image
import pyttsx
import pyautogui as gui
import numpy
from collections import defaultdict

from crab import Crab, STD, COMPOSITE
from skill import Skill
from window import Window

from pytesseract import image_to_string


class Hero(object):

    def __init__(self, base, gs):
        self.gs = gs
        self.base = base
        self.panelheight = 0
        self.namebox = (0,0,0,0)
        self.name = ""
        self.level = 0
        self.buy_coord_offset = (-30, 60)
        self.buy_coord = (base[0] + self.buy_coord_offset[0], base[1] + self.buy_coord_offset[1])
        self.check_interval = datetime.timedelta(seconds=1)
        self.lastcheck = datetime.datetime.now()
        self.intervals = []

    def ocr_name(self):

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


class GameState(object):

    def __init__(self, engine):

        self.skills = {}
        # left, top, right, bottom
        self.windowbox = (0,0,0,0)
        self.screen = None
        self.desiredsize = (1662, 942)
        self.silent = False
        self.correctscreen = False
        self.engine = engine
        self.lastclickablecheck = datetime.datetime.now()
        self.clickableareas = {}
        self.headcrabcount = 0
        self.lastmouse = (0, 0)
        self.playeridletime = datetime.datetime.now().replace(microsecond=0)
        self.gamestart = datetime.datetime.now().replace(microsecond=0)
        self.lastclickable = datetime.datetime.now().replace(microsecond=0)
        self.progression_coord_offset = (1599, 379)
        self.progression_coord = (0, 0)
        self.progression_color = (255, 0, 0)
        self.progression_state = None
        self.visibleheroes = []
        self.lastherocheck = datetime.datetime.now() - datetime.timedelta(seconds=30)
        self.tracked_hero = None

    def collect_skill_state(self):

        skills = ["clickstorm", "powersurge", "lucky strikes", "metal detector", "golden clicks", "the dark ritual", "super clicks", "energize", "reload"]

        top = self.windowbox[1] + 240
        left = self.windowbox[0] + 855
        height = 61
        width = 62

        interval = 12

        for i in range(9):
            skillbox = (left, top, left + width, top + height)
            if i + 1 not in self.skills:
                self.skills[i + 1] = Skill(name=skills[i], imgbox=skillbox, number=i + 1)
            self.skills[i + 1].ingestcolor(self.screen)
            self.skills[i + 1].setstate()
            top += interval + height
            if i == 2 or i == 5 or i == 7:
                top += 1

    def adjust_size(self):
        c = 0

        while True:
            img = PIL.ImageGrab.grab()
            w = Window(img)
            windowbox = w.find_window()
            fullwindow = img.crop(windowbox)
            realsize = fullwindow.size
            print("\rWidth: " + str(self.desiredsize[0]-realsize[0]) + " Height: " + str(self.desiredsize[1]-realsize[1]) + " "+ str(c), end="")
            if (self.desiredsize[0]-realsize[0], self.desiredsize[1]-realsize[1]) == (0,0):
                break
            time.sleep(.1)
            c+=1
        print()

    def collect_screen(self):

        self.screen = PIL.ImageGrab.grab()
        try:
            w = Window(self.screen)
            windowbox = w.find_window()
            left, top, right, bottom = windowbox
            windowheight = bottom-top
            windowwidth = right-left
            if windowheight == self.desiredsize[1] and windowwidth == self.desiredsize[0]:
                self.infocus = True
                if self.windowbox != windowbox:
                    if not self.silent:
                        self.engine.say("window position is locked in")
                        self.engine.runAndWait()
                self.windowbox = windowbox
                self.progression_coord = (self.windowbox[0] + self.progression_coord_offset[0], self.windowbox[1] + self.progression_coord_offset[1])
            else:
                self.infocus = False
        except:
            pass

    def update_screen(self):

        self.screen = PIL.ImageGrab.grab()

    def collect_clickables(self, collect=False):

        left, top, right, bottom = self.windowbox
        # window width 1662 height 942
        # crab  width 45 height 50

        windowheight = bottom-top
        windowwidth = right-left

        # these are all hand calculated from an initial test run
        magic_width_percent = 0.02707581227436823
        magic_height_percent = 0.05307855626326964

        magic_menu_left_percent = 0.44103489771359805
        magic_bottom_left_percent = 0.737063778580024
        magic_leftbottom_left_percent = 0.6299638989169675
        magic_lefttop_left_percent = 0.6407942238267148
        magic_rightbottom_left_percent = 0.8489771359807461
        magic_righttop_left_percent = 0.8898916967509025

        magic_menu_top_percent = 0.6963906581740976
        magic_bottom_top_percent = 0.732484076433121
        magic_leftbottom_top_percent = 0.6125265392781316
        magic_lefttop_top_percent = 0.5339702760084926
        magic_rightbottom_top_percent = 0.643312101910828
        magic_righttop_top_percent = 0.6284501061571125

        crabboxheight = round(windowheight * magic_height_percent)
        crabboxwidth = round(windowwidth * magic_width_percent)

        menucrabwidthoffset = round(windowwidth * magic_menu_left_percent)
        bottomcrabwidthoffset = round(windowwidth * magic_bottom_left_percent)
        leftbottomcrabwidthoffset = round(windowwidth * magic_leftbottom_left_percent)
        lefttopwidthoffset = round(windowwidth * magic_lefttop_left_percent)
        rightbottomcrabwidthoffset = round(windowwidth * magic_rightbottom_left_percent)
        righttopwidthoffset = round(windowwidth * magic_righttop_left_percent)

        menucrabheightoffset = round(windowheight * magic_menu_top_percent)
        bottomcrabheightoffset = round(windowheight * magic_bottom_top_percent)
        leftbottomcrabheightoffset = round(windowheight * magic_leftbottom_top_percent)
        lefttopheightoffset = round(windowheight * magic_lefttop_top_percent)
        rightbottomcrabheightoffset = round(windowheight * magic_rightbottom_top_percent)
        righttopheightoffset = round(windowheight * magic_righttop_top_percent)

        menucrabtopoffset = 0

        menucrabbox = (left+menucrabwidthoffset, top+menucrabheightoffset, left+menucrabwidthoffset+crabboxwidth, top+menucrabheightoffset+crabboxheight)
        # 1225 690
        bottomcrabbox = (left+bottomcrabwidthoffset, top+bottomcrabheightoffset, left+bottomcrabwidthoffset+crabboxwidth, top+bottomcrabheightoffset+crabboxheight)

        # 1047, 577
        leftbottomcrabbox = (left+leftbottomcrabwidthoffset, top+leftbottomcrabheightoffset, left+leftbottomcrabwidthoffset+crabboxwidth, top+leftbottomcrabheightoffset+crabboxheight)
        # 1065, 503
        leftopcrabbox = (left+lefttopwidthoffset, top+lefttopheightoffset, left+lefttopwidthoffset+crabboxwidth, top+lefttopheightoffset+crabboxheight)

        # 1411, 606
        rightbottomcrabbox = (left+rightbottomcrabwidthoffset, top+rightbottomcrabheightoffset, left+rightbottomcrabwidthoffset+crabboxwidth, top+rightbottomcrabheightoffset+crabboxheight)
        # 1479l 592
        righttopcrabbox = (left+righttopwidthoffset, top+righttopheightoffset, left+righttopwidthoffset+crabboxwidth, top+righttopheightoffset+crabboxheight)

        clickableboxes = [(menucrabbox, "menu"),
                          (bottomcrabbox, "bottom"),
                          (leftopcrabbox, "left top"),
                          (leftbottomcrabbox, "left bottom"),
                          (rightbottomcrabbox, "right bottom"),
                          (righttopcrabbox, "right top")]


        for box, location in clickableboxes:
            self.clickableareas[location] = Crab(self.screen.crop(box), box=box, location=location)

        if not collect:
            return self.parseclickableimages()

    def parseclickableimages(self):

        results = []
        scores = []

        for location in self.clickableareas:
            clickable = self.clickableareas[location]
            clickable.compare(STD, COMPOSITE)
            if clickable.score > .75:
                self.headcrabcount += 1
                results.append(clickable)
        readout = [str(self.clickableareas[i].score)[1:4] + " " + self.clickableareas[i].location for i in self.clickableareas]

        now = datetime.datetime.now().replace(microsecond=0)

        averagetime = (now - self.gamestart)/max(1, self.headcrabcount)

        # print("\rFound: " + str(self.headcrabcount) + "; " + ", ".join(readout) + " Interval: " + str(now-self.lastclickable) + " Avg: " + str(averagetime), end="", flush=True)
        # if len(results) > 0:
        #     self.lastclickable = datetime.datetime.now().replace(microsecond=0)
        #     print()

        return results

    def do_ritual(self):

        output = "\r"
        for i in self.skills:
            output += str(self.skills[i].number) + ":" + str(self.skills[i].state) + "  "
        # print(output, end="")

        if self.skills[6].state and self.skills[8].state and self.skills[9].state:
            print("\rexecuting dark ritual".ljust(140, " "))
            self.skills[8].click()
            self.skills[6].click()
            self.skills[9].click()
        elif self.skills[8].state and self.skills[9].state:
            print("\rcharging dark ritual".ljust(140, " "))
            self.skills[8].click()
            self.skills[9].click()

    def idle_save(self):

        currentpos = gui.position()
        currentime = datetime.datetime.now().replace(microsecond=0)

        if self.lastmouse != currentpos:
            self.playeridletime = currentime
            self.lastmouse = currentpos
        else:
            delta = datetime.timedelta(minutes=10)
            if currentime - self.playeridletime > delta:
                x, y = currentpos
                if self.windowbox[0] < x < self.windowbox[2] and self.windowbox[1] < y < self.windowbox[3]:
                    gui.moveTo(self.windowbox[0]+10, self.windowbox[1]+1)
                    gui.click(self.windowbox[0]+10, self.windowbox[1]+1)
                    print("\rMoving the mouse to a better spot since you appear to be idle".ljust(140, " "))

    def collect_heroes(self):

        textbox = (511, 319, 625, 350)

        box = (self.windowbox[0] + textbox[0],
               self.windowbox[1] + textbox[1],
               self.windowbox[0] + textbox[2],
               self.windowbox[1] + textbox[3],)

        myimage = self.screen.crop(box)


        mx, my = myimage.size

        output = Image.new(myimage.mode, myimage.size)

        for y in range(my):
            for x in range(mx):
                if myimage.getpixel((x, y)) == (254, 254, 254):
                    myimage.putpixel((x, y), (0,0,0))
                else:
                    myimage.putpixel((x, y), (255,255,255))


        print(image_to_string(image=myimage))

        sys.exit(0)

    def collect_visible_heroes(self):

        if datetime.datetime.now() - self.lastherocheck < datetime.timedelta(seconds=30):
            return
        else:
            self.lastherocheck = datetime.datetime.now()

        herocrop = (self.windowbox[0]+260, self.windowbox[1]+270, self.windowbox[0]+260+10, self.windowbox[3])

        herocolors = [(244, 232, 168), (244, 233, 169), (245, 233, 169), (245, 233, 170), (245, 234, 170),
                      (245, 234, 171), (245, 235, 171), (245, 235, 172), (246, 235, 172), (246, 236, 173),
                      (246, 236, 174), (255, 219, 82), (255, 219, 83), (255, 220, 83), (255, 221, 84),
                      (255, 221, 85), (255, 222, 86), (255, 223, 86), (255, 223, 87), (255, 224, 88),
                      (255, 224, 89), (255, 225, 89), ]

        temp_list = []

        inheropanel = False
        for i in range(herocrop[3]-herocrop[1]-10):
            thiscolor = self.screen.getpixel((herocrop[0], herocrop[1] + i))
            if thiscolor in herocolors:
                if not inheropanel:
                    panel = Hero(base=(herocrop[0], herocrop[1] + i), gs=self)
                    temp_list.append(panel)
                    if len(temp_list) == 1:
                        for h in self.visibleheroes:
                            if h.base == panel.base:
                                # print("\nno change to the hero list skipping collection")
                                return
                        else:
                            self.visibleheroes = temp_list
                    panel.panelheight = 0
                    inheropanel = panel
                inheropanel.panelheight += 1
            else:
                inheropanel = False



        invalid = []
        valid_heights = [131, 137, 138]
        for heropanel in self.visibleheroes:
            if heropanel.panelheight not in valid_heights:
                invalid.append(heropanel)

        for i in invalid:
            self.visibleheroes.remove(i)

        for h in self.visibleheroes:
            h.ocr_name()
            h.ocr_level()

    def dumb_buy(self):

        terra = None
        samurai = None
        for hero in self.visibleheroes:
            if hero.name == "Terra":
                terra = hero
                self.tracked_hero = terra

        if terra is None:
            return

        if self.screen.getpixel(self.progression_coord) == self.progression_color:
            self.progression_state = 0
            # print("progression locked")
        else:
            self.progression_state = 1
            # print("progression open")

        if self.infocus:
            if terra.buy_timer():
                gui.keyDown(key="z")
                time.sleep(.2)
                self.update_screen()
                if terra.can_buy():
                    terra.check_interval = terra.check_interval * .75
                    self.click(terra.buy_coord)
                    if not self.progression_state:
                        print("\nunlocking progression, 25 heroes bought")
                        self.click(self.progression_coord)
                else:
                    terra.check_interval = terra.check_interval * 2
                gui.keyUp(key="z")




    def click(self, coord):
        currentMouseX, currentMouseY = gui.position()
        gui.click(coord[0], coord[1])
        gui.moveTo(currentMouseX, currentMouseY)


def capture():

    gs = GameState(engine=pyttsx.init())

    gs.adjust_size()

    SaveDirectory = r'F:\Documents\Python\heroclicker\unknown'

    gs.collect_screen()

    time.sleep(2)
    gs.collect_clickables()
    for clickablename in gs.clickableareas:
        print()
        clickable = gs.clickableareas[clickablename]
        filename = 'ScreenShot_'+str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_")+"_" + clickable.location.replace(" ", "_") + '.bmp'
        save_as = os.path.join(SaveDirectory, filename)
        clickable.image.save(save_as)

    gs.engine.say("Work Complete")
    gs.engine.runAndWait()


def screenshot():
    '''
    This function has nothing to do with hero clicker, i made it to screenshot witcher3
    '''

    engine = pyttsx.init()

    SaveDirectory = r'F:\Documents\Python\heroclicker\unknown'

    while True:

        time.sleep(2)
        img = PIL.ImageGrab.grab()
        filename = 'ScreenShot_'+str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_") + '.jpg'
        save_as = os.path.join(SaveDirectory, filename)
        img.save(save_as)
        engine.say("Work Complete")
        engine.runAndWait()


def run():

    gs = GameState(engine=pyttsx.init())

    gs.silent = True

    gs.adjust_size()

    loop = 0
    while True:
        loop += 1
        cycle_start = datetime.datetime.now()
        gs.idle_save()
        # time.sleep(.5)

        gs.collect_screen()
        if gs.windowbox == (0,0,0,0):
            continue

        if datetime.datetime.now() - gs.lastclickablecheck > datetime.timedelta(seconds=10):
            gs.lastclickablecheck = datetime.datetime.now()
            for clickable in gs.collect_clickables():
                print()
                clickable.savegood()
                clickable.click()
                if not gs.silent:
                    gs.engine.say("\nHead crab found at position " + clickable.location)
                    gs.engine.runAndWait()

        if False:
            gs.collect_skill_state()
            gs.do_ritual()
        gs.collect_visible_heroes()
        gs.dumb_buy()
        cycletime = datetime.datetime.now()-cycle_start
        if cycletime < datetime.timedelta(seconds=1):
            # print("time to sleep:", (datetime.timedelta(seconds=1)-cycletime).total_seconds())
            time.sleep((datetime.timedelta(seconds=1)-cycletime).total_seconds())

        cycle_status = "\rCycleTime:" + str(datetime.datetime.now()-cycle_start)
        cycle_status += " Clickables:" + str(gs.headcrabcount)
        cycle_status += " Loop:" + str(loop)
        if gs.tracked_hero:
            cycle_status += " Z Interval:" + str(gs.tracked_hero.check_interval)

        print(cycle_status, end="")


# capture()
run()

