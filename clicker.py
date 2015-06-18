__author__ = 'Joel'
import os
import sys
import datetime
import time
import PIL
from PIL import ImageGrab
import pyttsx
import pyautogui as gui

from crab import Crab, STD, COMPOSITE
from skill import Skill
from window import Window
from heroes import Heroes


class GameState(object):

    def __init__(self, engine):

        self.skills = {}
        # left, top, right, bottom
        self.window = Window(self)
        self.silent = False
        self.engine = engine
        self.lastclickablecheck = datetime.datetime.now()
        self.clickableareas = {}
        self.headcrabcount = 0
        self.lastmouse = (0, 0)
        self.playeridletime = datetime.datetime.now().replace(microsecond=0)
        self.idle = False
        self.gamestart = datetime.datetime.now().replace(microsecond=0)
        self.lastclickable = datetime.datetime.now().replace(microsecond=0)
        self.lastherobuy = datetime.datetime.now()

        self.progression_coord = (0, 0)
        self.progression_state = None
        self.hero = Heroes(self)

    def collect_skill_state(self):

        skills = ["clickstorm", "powersurge", "lucky strikes", "metal detector", "golden clicks", "the dark ritual", "super clicks", "energize", "reload"]

        top = self.window.box[1] + 240
        left = self.window.box[0] + 855
        height = 61
        width = 62

        interval = 12

        for i in range(9):
            skillbox = (left, top, left + width, top + height)
            if i + 1 not in self.skills:
                self.skills[i + 1] = Skill(name=skills[i], imgbox=skillbox, number=i + 1)
            self.skills[i + 1].ingestcolor(self.window.screen)
            self.skills[i + 1].setstate()
            top += interval + height
            if i == 2 or i == 5 or i == 7:
                top += 1

    def collect_clickables(self, collect=False):

        left, top, right, bottom = self.window.box
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
            self.clickableareas[location] = Crab(self.window.screen.crop(box), box=box, location=location)

        if not collect:
            return self.parseclickableimages()

    def parseclickableimages(self):

        results = []

        for location in self.clickableareas:
            clickable = self.clickableareas[location]
            clickable.compare(STD, COMPOSITE)
            if clickable.score > .75:
                self.headcrabcount += 1
                results.append(clickable)
        # readout = [str(self.clickableareas[i].score)[1:4] + " " + self.clickableareas[i].location for i in self.clickableareas]

        now = datetime.datetime.now().replace(microsecond=0)

        # averagetime = (now - self.gamestart)/max(1, self.headcrabcount)

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
            self.idle = False
        else:
            delta = datetime.timedelta(minutes=10)
            if currentime - self.playeridletime > delta:
                x, y = currentpos
                if self.window.box[0] < x < self.window.box[2] and self.window.box[1] < y < self.window.box[3] and x != self.window.box[0]+30 and y != self.window.box[0]+3:
                    gui.moveTo(self.window.box[0]+30, self.window.box[1]+3)
                    gui.click(self.window.box[0]+30, self.window.box[1]+3)
                    print("\rMoving the mouse to a better spot since you appear to be idle".ljust(140, " "))
                    self.idle = True

    def collect_progression(self):

        progression_color = (255, 0, 0)
        progression_coord_offset = (1599, 379)
        self.progression_coord = (self.window.box[0] + progression_coord_offset[0], self.window.box[1] + progression_coord_offset[1])

        if self.window.screen.getpixel(self.progression_coord) == progression_color:
            self.progression_state = 0
            # print("progression locked")
        else:
            self.progression_state = 1
            # print("progression open")

    def dumb_buy(self):

        h = None
        if "Terra" in self.hero.heroes:
            if self.hero.heroes["Terra"].isvisible:
                h = self.hero.heroes["Terra"]
                self.hero.tracked = h

        if h is None:
            return

        if h.try_buy(25):
            if not self.progression_state:
                print("\nunlocking progression, 25 heroes bought")
                self.click(self.progression_coord)

    def click(self, coord):

        currentMouseX, currentMouseY = gui.position()
        gui.click(coord[0], coord[1])
        gui.moveTo(currentMouseX, currentMouseY)


def capture():

    gs = GameState(engine=pyttsx.init())

    gs.window.adjust_size()

    save_directory = r'F:\Documents\Python\heroclicker\unknown'

    gs.window.collect_screen()

    time.sleep(2)
    gs.collect_clickables()
    for clickable_name in gs.clickableareas:
        print()
        clickable = gs.clickableareas[clickable_name]
        filename = 'ScreenShot_'+str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_")+"_" + clickable.location.replace(" ", "_") + '.bmp'
        save_as = os.path.join(save_directory, filename)
        clickable.image.save(save_as)

    gs.engine.say("Work Complete")
    gs.engine.runAndWait()


def screenshot():
    """
    This function has nothing to do with hero clicker, i made it to screenshot witcher3
    """

    engine = pyttsx.init()

    save_directory = r'F:\Documents\Python\heroclicker\unknown'

    while True:
        time.sleep(2)
        img = PIL.ImageGrab.grab()
        filename = 'ScreenShot_'+str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "_") + '.jpg'
        save_as = os.path.join(save_directory, filename)
        img.save(save_as)
        engine.say("Work Complete")
        engine.runAndWait()


def run():

    gs = GameState(engine=pyttsx.init())

    gs.silent = True

    gs.window.adjust_size()

    loop = 0
    while True:
        loop += 1
        cycle_start = datetime.datetime.now()
        gs.idle_save()
        # time.sleep(.5)

        gs.window.collect_screen()
        if gs.window.box == (0, 0, 0, 0):
            print("do i ever hit this??")
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

        if True:
            gs.collect_skill_state()
            gs.do_ritual()
        gs.collect_progression()
        gs.hero.collect_visible_heroes()
        gs.dumb_buy()
        cycletime = datetime.datetime.now()-cycle_start
        if cycletime < datetime.timedelta(seconds=1):
            # print("time to sleep:", (datetime.timedelta(seconds=1)-cycletime).total_seconds())
            time.sleep((datetime.timedelta(seconds=1)-cycletime).total_seconds())

        cycle_status = "\rCycleTime:" + str(cycletime)
        cycle_status += " Clickables:" + str(gs.headcrabcount)
        cycle_status += " Loop:" + str(loop)
        if gs.hero.tracked:
            interval = str(round(gs.hero.tracked.check_interval.total_seconds()))
            left = str(round((datetime.datetime.now() - gs.hero.tracked.lastcheck).total_seconds()))
            cycle_status += " Z Interval:" + interval + "/" + left

        print(cycle_status, end="")


# capture()
run()