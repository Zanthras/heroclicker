__author__ = 'Joel'

import datetime
import time
import sys



import pyautogui as gui
from pytesseract import image_to_string


class Heroes(object):

    def __init__(self, gs):

        self.gs = gs
        self.tracked = None
        self.scrollbar = 0
        self.visible = []
        self.heroes = {}

    def find_scrollbar(self):

        scrollbar_x = 789
        scrollbar_y_top = 313
        scrollbar_y_bottom = 894

        x = self.gs.window.box[0] + scrollbar_x
        scrollbox = (self.gs.window.box[0] + scrollbar_x,
                     self.gs.window.box[1] + scrollbar_y_top,
                     self.gs.window.box[0] + scrollbar_x + 1,
                     self.gs.window.box[1] + scrollbar_y_bottom)

        for y in range(scrollbar_y_bottom-scrollbar_y_top):
            c = self.gs.window.screen.getpixel((x, y+self.gs.window.box[1]+scrollbar_y_top))
            if c[0] == 255:
                return y+self.gs.window.box[1]+scrollbar_y_top

    def collect_visible_heroes(self):

        if not self.gs.window.infocus:
            return

        bar_location = self.find_scrollbar()

        if bar_location == self.scrollbar:
            return
        else:
            # print(self.scrollbar)
            self.scrollbar = bar_location

        herocrop = (self.gs.window.box[0]+260, self.gs.window.box[1]+270, self.gs.window.box[0]+260+10, self.gs.window.box[3])

        herocolors = [(244, 232, 168), (244, 233, 169), (245, 233, 169), (245, 233, 170), (245, 234, 170),
                      (245, 234, 171), (245, 235, 171), (245, 235, 172), (246, 235, 172), (246, 236, 173),
                      (246, 236, 174), ]
        guildedherocolors = [(255, 219, 82), (255, 219, 83), (255, 220, 83), (255, 221, 84),
                             (255, 221, 85), (255, 222, 86), (255, 223, 86), (255, 223, 87), (255, 224, 88),
                             (255, 224, 89), (255, 225, 89), ]

        temp_list = []

        inheropanel = False
        for i in range(herocrop[3]-herocrop[1]-10):
            normal = False
            guilded = False
            thiscolor = self.gs.window.screen.getpixel((herocrop[0], herocrop[1] + i))
            if thiscolor in herocolors:
                normal = True
            elif thiscolor in guildedherocolors:
                guilded = True
            if normal or guilded:
                if not inheropanel:
                    panel = Hero(base=(herocrop[0], herocrop[1] + i), gs=self.gs)
                    if guilded:
                        panel.guilded = True
                    temp_list.append(panel)
                    inheropanel = panel
                inheropanel.panelheight += 1
            else:
                inheropanel = False

        invalid = []
        valid_heights = [131, 137, 138]
        for heropanel in temp_list:
            if heropanel.panelheight == 131 and heropanel.guilded is not True:
                # print("invalid panel", heropanel.panelheight)
                invalid.append(heropanel)
            elif heropanel.panelheight not in valid_heights:
                # print("invalid panel", heropanel.panelheight)
                invalid.append(heropanel)

        for i in invalid:
            temp_list.remove(i)

        for h in temp_list:
            h.ocr_name()
            h.ocr_level()

        for hero in self.heroes:
            self.heroes[hero].sethidden()
        for newhero in temp_list:
            if newhero.name in self.heroes:
                # print("updating existing", newhero.name)
                self.heroes[newhero.name].setvisible(base=newhero.base, level=newhero.level)
            elif newhero.name:
                # print("adding new hero", newhero.name)
                newhero.setvisible(init=True)
                self.heroes[newhero.name] = newhero

    def collect_all_heroes(self):

        if self.gs.window.infocus:
            # scroll to the top
            self.gs.window.scroll(15)
        self.gs.window.update_screen()
        self.collect_visible_heroes()
        for i in range(15):
            self.gs.window.scroll(-1)
            self.gs.window.update_screen()
            self.collect_visible_heroes()
            # print(self.visible)

        sys.exit(0)


class Hero(object):

    buy_coord_offset = (-30, 60)

    def __init__(self, base, gs):
        self.gs = gs
        self.base = base
        self.panelheight = 0
        self.namebox = (0, 0, 0, 0)
        self.name = ""
        self.level = 0
        self.buy_coord = (0, 0)
        self.check_interval = datetime.timedelta(seconds=1)
        self.lastcheck = datetime.datetime.now()
        self.intervals = []
        self.isvisible = True
        self.ishidden = False
        self._update_buy_coord()
        self.guilded = False
        self.order = 0
        self.shortname = ""

    def _update_buy_coord(self):

        self.buy_coord = (self.base[0] + self.buy_coord_offset[0], self.base[1] + self.buy_coord_offset[1])

    def ocr_name(self):

        # because buying produces visual flair that covers the name... halt ocr after buys...
        if datetime.datetime.now() - self.gs.lastherobuy < datetime.timedelta(seconds=2):
            time_left = datetime.timedelta(seconds=2) - (datetime.datetime.now() - self.gs.lastherobuy)
            time.sleep(time_left.total_seconds())

        textcolor = (102, 51, 204), (254, 254, 254)

        crop = (self.base[0], self.base[1]+5, self.base[0]+370, self.base[1]+37)
        myimage = self.gs.window.screen.crop(crop)

        mx = crop[2] - crop[0]
        my = crop[3] - crop[1]

        for y in range(my):
            for x in range(mx):
                if myimage.getpixel((x, y)) in textcolor:
                    myimage.putpixel((x, y), (0, 0, 0))
                else:
                    myimage.putpixel((x, y), (255, 255, 255))

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
        if self.name not in order and self.name:
            print("hero name i dont know", self.name)
        # for whatever reason the ocr completely fails on lilin, so lets check the scroll bar
        if not self.name and self.gs.hero.scrollbar > 700:
            self.name = "Lilin"
        if self.name:
            self.order = order[self.name][0]
            self.shortname = order[self.name][1]

    def ocr_level(self):

        textcolor = (102, 51, 204), (254, 254, 254)

        crop = (self.base[0]+220, self.base[1]+40, self.base[0]+370, self.base[1]+70)
        myimage = self.gs.window.screen.crop(crop)

        mx = crop[2] - crop[0]
        my = crop[3] - crop[1]

        for y in range(my):
            for x in range(mx):
                if myimage.getpixel((x, y)) in textcolor:
                    myimage.putpixel((x, y), (0, 0, 0))
                else:
                    myimage.putpixel((x, y), (255, 255, 255))

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

        buy = (253, 253, 0)
        dont = (254, 135, 67)
        box = (self.base[0]-145, self.base[1]+102, self.base[0]-30, self.base[1]+103)

        for x in range(box[2]-box[0]):
            pix = self.gs.window.screen.getpixel((box[0]+x, box[1]))
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
        self.base = (0, 0)
        self.buy_coord = (0, 0)
        self.isvisible = False
        self.ishidden = True

        if self in self.gs.hero.visible:
            self.gs.hero.visible.remove(self)

    def try_buy(self, amount):

        try:
            if self.isvisible and self.buy_timer():
                if amount == 25:
                    if not self.gs.window.infocus:
                        return False
                    gui.keyDown(key="z")
                    time.sleep(.2)
                    self.gs.window.update_screen()
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

    def scroll_to(self):

        targetscrollpositions = [335, 367, 400, 432, 464, 497, 529, 561, 594, 626, 659, 691, 723, 756, 788]

        pixels_per_scroll = 32

        scrollbar_height = 453

        current_pos = 756

        highest_order_hero = None

        for h in self.gs.hero.heroes:
            if self.gs.hero.heroes[h].order > highest_order_hero.order:
                highest_order_hero = self.gs.hero.heroes[h]


        pass

    def __str__(self):

        return self.name + ":" + str(self.level)

    def __repr__(self):

        return self.__str__()


order = {'Cid, the Helpful Adventurer': (1, "cid"),
         'Treebeast': (2, "treebeast"),
         'Ivan, the Drunken Brawler': (3, "ivan"),
         'Brittany, Beach Princess': (4, "brittany"),
         'The Wandering Fisherman': (5, "fisherman"),
         'Betty Clicker': (6, "betty"),
         'The Masked Samurai': (7, "samurai"),
         'Leon': (8, "leon"),
         'The Great Forest Seer': (9, "seer"),
         'Alexa, Assassin': (10, "alexa"),
         'Natalia, Ice Apprentice': (11, "natalia"),
         'Mercedes, Duchess of Blades': (12, "mercedes"),
         'Bobby, Bounty Hunter': (13, "bobby"),
         'Broyle Lindeoven, Fire Mage': (14, "fire"),
         "Sir George II, King's Guard": (15, "george"),
         'King Midas': (16, "midas"),
         'Referi Jerator, Ice Wizard': (17, "ice"),
         'Abaddon': (18, "abaddon"),
         'Ma Zhu': (19, "ma"),
         'Amenhotep': (20, "amenhotep"),
         'Beastlord': (21, "beastlord"),
         'Athena, Goddess of War': (22, "athena"),
         'Aphrodite, Goddess of Love': (23, "aphrodite"),
         'Shinatobe, Wind Deity': (24, "shinatobe"),
         'Grant, The General': (25, "grant"),
         'Frostleaf': (26, "frostleaf"),
         'Dread Knight': (27, "dread"),
         'Atlas': (28, "atlas"),
         'Terra': (29, "terra"),
         'Phthalo': (30, "phthalo"),
         'Orntchya Gladeye, Didensy': (31, "gladeye"),
         'Lilin': (32, "lilin"),
         'Cadmia': (33, "cadmia"),
         'Alabaster': (34, "alabaster"),
         'Astraea': (35, "astraea"), }