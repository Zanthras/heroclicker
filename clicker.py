"""
    Clicker Hero Bot
    Copyright (C) 2015  Joel Whitcomb

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import datetime
import time

import pip

try:
    import PIL
    from PIL import ImageGrab
except ImportError:
    print("Installing Pillow/PIP")
    pip.main(["pip", "install", "Pillow"])
    import PIL
    from PIL import ImageGrab
try:
    import pyautogui as gui
except ImportError:
    pip.main(["pip", "install", "pyautogui"])
    import pyautogui as gui
try:
    import pytesseract
    from pytesseract import image_to_string
except ImportError:
    pip.main(["pip", "install", "pytesseract"])
    import pytesseract
    from pytesseract import image_to_string

with open("tesseract_location.txt") as f:
    loc = f.read().strip()

pytesseract.pytesseract.tesseract_cmd = loc

from crab import Crab, STD, COMPOSITE
from skill import Skill
from window import Window
from heroes import Heroes
from bot import program
from relic import RelicInfo

class GameState(object):

    def __init__(self, engine):

        self.skills = {}
        # left, top, right, bottom
        self.window = Window(self)
        self.silent = False
        self.engine = engine
        self.gamestart = datetime.datetime.now().replace(microsecond=0)
        self.ascensionstart = datetime.datetime.now().replace(microsecond=0)
        # Information for determining if there is a human at the desk
        self.lastmouse = (0, 0)
        self.playeridletime = datetime.datetime.now().replace(microsecond=0)
        self.idle = False
        # Headcrab/Fish/Clickable Information
        self.lastclickablecheck = datetime.datetime.now()
        self.clickableareas = {}
        self.headcrabcount = 0
        self.lastclickable = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(seconds=10)
        self.clickablesready = []
        self.click_clickables = True
        # Auto level progression information
        self.progression_coord = (0, 0)
        self.progression_state = None
        # Timer for preventing OCR after any hero has been purchased
        self.lastherobuy = datetime.datetime.now() - datetime.timedelta(seconds=3)
        # heroes module, all hero information is there
        self.hero = Heroes(self)
        # Hero Souls information
        self.souls = 0
        self.peakspm = 0
        self.soulstimer = datetime.datetime.now() - datetime.timedelta(seconds=20)
        self.lastpeak = datetime.datetime.now()
        self.firstload = True
        self._existingsouls = 0
        # What step am I on for the gameplay
        self.step = "None"
        self.ascensiondesired = False
        self.log = open("logs/" + str(self.ascensionstart).replace(":", "-").replace(" ", "-") + ".log", "w")
        # Relic information
        self.relics = RelicInfo(self)

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

        if not datetime.datetime.now() - self.lastclickablecheck > datetime.timedelta(seconds=10):
            return
        else:
            self.lastclickablecheck = datetime.datetime.now()

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
            self.clickablesready = self.parseclickableimages()

    def collect_souls(self):

        now = datetime.datetime.now()
        # visual flair from buying would screw up the OCR
        if now - self.lastherobuy < datetime.timedelta(seconds=2):
            return

        # Collect hero souls every 11 seconds since OCR isnt CPU Free
        if not (now - datetime.timedelta(seconds=11)) > self.soulstimer:
            return
        else:
            self.soulstimer = now

        crop = (self.window.box[0]+525, self.window.box[1]+250, self.window.box[0]+525+285, self.window.box[1]+250+17)
        image = self.window.screen.crop(crop)

        mx = crop[2] - crop[0]
        my = crop[3] - crop[1]

        for y in range(my):
            for x in range(mx):
                if image.getpixel((x, y)) == (254, 254, 254):
                    image.putpixel((x, y), (0, 0, 0))
                else:
                    image.putpixel((x, y), (255, 255, 255))

        raw_souls = image_to_string(image=image)
        cleaned_raw = ""
        chars = "1234567890."
        past_plus = False
        for c in raw_souls:
            if c in chars:
                cleaned_raw += c
            if c == "+":
                past_plus = True
            if past_plus and c == "e":
                cleaned_raw += c
            if past_plus and c == "a":
                cleaned_raw += "4"
        # print(cleaned_raw)
        if "e" not in cleaned_raw:
            if cleaned_raw:
                try:
                    hopefully_souls = int(cleaned_raw)
                except ValueError:
                    # self.window.screen.crop(crop).show()
                    # sys.exit(0)
                    hopefully_souls = 0
                if hopefully_souls > self.souls:
                    self.souls = hopefully_souls
                else:
                    # pretend the soul collection didnt happen
                    self.soulstimer = now - datetime.timedelta(seconds=11)

        else:
            parts = cleaned_raw.split("e")
            try:
                hopefully_souls = float(parts[0]) ** int(parts[1])
            except ValueError:
                hopefully_souls = 0
                print("data error on souls", raw_souls)
            if hopefully_souls > self.souls:
                self.souls = hopefully_souls
            else:
                print("parse error on souls", raw_souls)

        if self.firstload and self.souls:
            self._existingsouls = self.souls
            self.firstload = False
            self.ascensionstart -= datetime.timedelta(seconds=60)

        # print(self.souls)

    def collect_progression(self):

        progression_color = (255, 0, 0)
        progression_coord_offset = (1599, 379)
        self.progression_coord = (self.window.box[0] + progression_coord_offset[0], self.window.box[1] + progression_coord_offset[1])

        if self.window.screen.getpixel(self.progression_coord) == progression_color:
            if self.progression_state:
                for heroname in self.hero.heroes:
                    self.hero.heroes[heroname].progression_level = self.hero.heroes[heroname].level
            self.progression_state = 0
            # print("progression locked")
        else:
            self.progression_state = 1
            # print("progression open")

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
                if self.window.box[0] < x < self.window.box[2] and self.window.box[1] < y < self.window.box[3] and x != self.window.box[0]+30 and y != self.window.box[0]+30:
                    gui.moveTo(self.window.box[0]+30, self.window.box[1]+30)
                    print("\rMoving the mouse to a better spot since you appear to be idle".ljust(140, " "))
                    self.idle = True

    def calc_souls(self):

        ascension_minutes = (datetime.datetime.now() - self.ascensionstart).total_seconds()/60
        if ascension_minutes == 0:
            ascension_minutes = 1
        if self.souls == 0:
            spm = 0
        else:
            spm = (self.souls-self._existingsouls)/ascension_minutes
        if spm > self.peakspm:
            self.peakspm = spm
            # self.soulstimer = datetime.datetime.now() - self.soulstimer
            self.lastpeak = datetime.datetime.now()

        if (datetime.datetime.now() - self.lastpeak) > datetime.timedelta(minutes=3):
            # phrase = "Ascend now, two minutes without new peak souls per minute"
            # self.engine.say(phrase)
            # self.engine.runAndWait()
            self.ascensiondesired = True
            self.click_clickables = False
            self.hero.ascend()
        else:
            self.ascensiondesired = False
            self.click_clickables = True
        # debug
        # try:
        #     if self.peakspm / spm > 3:
        #         print()
        #         print("data anomaly: asc_min", ascension_minutes, "souls", self.souls, "spm", spm, "existing", self._existingsouls)
        # except ZeroDivisionError:
        #     pass
        # if spm < 0:
        #         print()
        #         print("data anomaly: asc_min", ascension_minutes, "souls", self.souls, "spm", spm, "existing", self._existingsouls)

        return spm


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


def run():
    os.system("mode con cols=180 lines=20")

    gs = GameState(engine=None)

    gs.silent = True

    gs.window.adjust_size()

    loop = 0
    max_print_size = 0
    while True:
        loop += 1
        cycle_start = datetime.datetime.now()
        gs.idle_save()
        # time.sleep(.5)

        gs.window.collect_screen()
        if gs.window.box == (0, 0, 0, 0):
            print("do i ever hit this??")
            continue

        gs.collect_souls()
        gs.collect_clickables()
        if ASCENSION_DEBUG:
            gs.click_clickables = False
            gs.hero.ascend()

        if gs.click_clickables and gs.clickablesready:
            clickable = gs.clickablesready.pop()
            clickable.savegood()
            clickable.click()

        if False:
            gs.collect_skill_state()
            gs.do_ritual()
        gs.collect_progression()
        if not gs.hero.heroes:
            gs.hero.collect_all_heroes()
        gs.hero.collect_visible_heroes()

        # execute bot instructions
        program(gs)
        cycletime = datetime.datetime.now()-cycle_start
        if cycletime < datetime.timedelta(seconds=1):
            # print("time to sleep:", (datetime.timedelta(seconds=1)-cycletime).total_seconds())
            time.sleep((datetime.timedelta(seconds=1)-cycletime).total_seconds())

        now = datetime.datetime.now().replace(microsecond=0)

        cycle_status = "\rCycle:" + str(cycletime.seconds) + "." + str(cycletime.microseconds)[:3]
        cycle_status += " Start: " + str(now - gs.gamestart)
        cycle_status += " Ascension " + str(now - gs.ascensionstart)
        cycle_status += " Clickables:" + str(gs.click_clickables)[:1] + str(gs.headcrabcount)
        # cycle_status += " Loop:" + str(loop)
        if gs.hero.tracked:
            interval = str(round(gs.hero.tracked.check_interval.total_seconds()))
            left = str(round((datetime.datetime.now() - gs.hero.tracked.lastcheck).total_seconds()))
            cycle_status += " Buy Interval:" + interval + "/" + left
        spm = gs.calc_souls()
        cycle_status += " SPM:" + str(round(spm)) + "/" + str(round(gs.peakspm))
        # cycle_status += " Focus:" + str(gs.window.infocus)
        time_till_ascend = datetime.datetime.now() - gs.lastpeak
        if time_till_ascend < datetime.timedelta(minutes=3):
            output = str(round((datetime.timedelta(minutes=3) - time_till_ascend).total_seconds()))
        elif not gs.ascensiondesired:
            output = str(round((datetime.timedelta(minutes=3) - time_till_ascend).total_seconds()))
        else:
            output = str(gs.ascensiondesired)

        cycle_status += " Ascend:" + output
        cycle_status += " " + gs.step
        if len(cycle_status) > max_print_size:
            max_print_size = len(cycle_status)
        print("\r" + " " * max_print_size, end="")
        print(cycle_status, end="")
        gs.log.write(str(int((now - gs.ascensionstart).total_seconds())) + "," + str(round(gs.peakspm)) + "," + str(round(spm)) + "\n" )

ASCENSION_DEBUG = False


try:
    run()
except KeyboardInterrupt:
    print("\nBot Stopped", end="")

