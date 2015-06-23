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
        self.scrollpositions = [4, 36, 69, 101, 133, 166, 198, 230, 263, 295, 328, 360, 392, 425, 457, 460]
        self.visiblewait = False

    def find_scrollbar(self):

        scrollbar_x = self.gs.window.box[0] + 789
        scrollbar_y_top = self.gs.window.box[1] + 313
        scrollbar_y_bottom = self.gs.window.box[1] + 894

        # x = self.gs.window.box[0] + scrollbar_x

        # box = (scrollbar_x, scrollbar_y_top, scrollbar_x+40, scrollbar_y_bottom)
        # self.gs.window.screen.crop(box).show()
        # sys.exit(0)


        for y in range(scrollbar_y_bottom-scrollbar_y_top):
            c = self.gs.window.screen.getpixel((scrollbar_x, y+scrollbar_y_top))
            # print(c)
            if c[0] == 255:
                # print(y)
                return self.find_scroll_position(y)

    def collect_visible_heroes(self, force=False):

        if not self.gs.window.infocus:
            return
        # this is to let functions that dont directly call this method still specify force via a module level global
        if self.visiblewait:
            force = True
            self.visiblewait = False

        # because buying produces visual flair that covers the ui... ignore collection after buys...
        if datetime.datetime.now() - self.gs.lastherobuy < datetime.timedelta(seconds=2):
            if not force:
                return
            else:
                time_left = datetime.timedelta(seconds=2) - (datetime.datetime.now() - self.gs.lastherobuy)
                time.sleep(time_left.total_seconds())

        bar_location = self.find_scrollbar()

        if bar_location == self.scrollbar:
            # print("scrollbar didnt move")
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
            # print(newhero.name)
            if newhero.name in self.heroes:
                # print("updating existing", newhero.name)
                entry = self.heroes[newhero.name]
                entry.setvisible(base=newhero.base, level=newhero.level)
                entry._update_coords(newhero.base)

            elif newhero.name:
                # print("adding new hero", newhero.name)
                newhero.setvisible(init=True)
                self.heroes[newhero.name] = newhero

    def collect_all_heroes(self):

        if self.gs.window.infocus:
            # scroll to the top
            self.gs.window.scroll(15)
        self.gs.window.update_screen()
        self.collect_visible_heroes(force=True)
        # the last scroll is tiny and pointless
        for i in range(14):
            self.gs.window.scroll(-1)
            self.gs.window.update_screen()
            self.collect_visible_heroes(force=True)

    def scroll_to_bottom(self):

        pos = self.find_scroll_position()
        if pos != self.scrollpositions[-1]:
            # print("scrolling to bottom")
            self.gs.window.scroll(-15)

    def find_scroll_position(self, amount=None):

        if amount is None:
            pos_to_check = self.scrollbar
        else:
            pos_to_check = amount

        currentscroll = 0
        best_distance = 999
        if pos_to_check in self.scrollpositions:
            currentscroll = pos_to_check
        else:
            for target in self.scrollpositions:
                distance = abs(pos_to_check - target)
                if distance < best_distance:
                    best_distance = distance
                    currentscroll = target
        # print("currentscroll", currentscroll)
        # if amount:
        #     print("Amount", amount, "current", currentscroll)
        return currentscroll

    def upgrade(self):

        # TODO: this function is taking some late game shortcuts, I will need to fix for early game

        self.scroll_to_bottom()
        self.gs.window.click((self.gs.window.box[0] + 467, self.gs.window.box[1] + 825))
        self.gs.lastherobuy = datetime.datetime.now()

        for heroname in self.heroes:
            if self.heroes[heroname].level >= 200:
                # print("setting", self.heroes[heroname], "to be upgraded")
                self.heroes[heroname].upgraded = True

    def ascend(self):

        self.gs.click_clickables = False

        god = None
        if "Amenhotep" in self.heroes:
            god = self.heroes["Amenhotep"]
        if god and self.gs.clickablesready and not self.gs.click_clickables:
            if god.level < 150:
                god.buy_up_to(150)
            else:
                print(" ASCENDED! +", self.gs.souls, "souls")
                god.scroll_to()
                self.gs.window.update_screen()
                self.collect_visible_heroes(force=True)
                # box = (god.base[0] + 197 - 26, god.base[1] + 103 - 25, god.base[0] + 197 + 26, god.base[1] + 103 + 25)
                # self.gs.window.screen.crop(box).show()
                self.gs.window.click((god.base[0]+197, god.base[1]+103))
                self.gs.window.update_screen()
                # self.gs.window.screen.show()
                self.gs.window.click((self.gs.window.box[0]+725, self.gs.window.box[1]+620))

                for heroname in self.heroes:
                    self.heroes[heroname].reset()

                self.gs.souls = 0
                self.gs.peakspm = 0
                self.gs._existingsouls = 0
                self.gs.soulstimer = datetime.datetime.now() - datetime.timedelta(seconds=20)
                self.gs.lastpeak = datetime.datetime.now()
                self.gs.click_clickables = True
                self.gs.ascensionstart = datetime.datetime.now().replace(microsecond=0)
                self.gs.clickablesready[0].savegood()
                self.gs.clickablesready[0].click()
                time.sleep(3)
                self.collect_all_heroes()
                self.gs.window.scroll(-2)
        else:
            return


class Hero(object):

    buy_coord_offset = (-30, 60)

    def __init__(self, base, gs):
        self.gs = gs
        self.base = base
        self.panelheight = 0
        self.namebox = (0, 0, 0, 0)
        self._update_name_coord()
        self.name = ""
        self.level = 0
        self.buy_coord = (0, 0)
        self.check_interval = datetime.timedelta(seconds=.1)
        self.lastcheck = datetime.datetime.now()
        self.isvisible = True
        self.ishidden = False
        self._update_buy_coord()
        self.guilded = False
        self.order = 0
        self.shortname = ""
        self.can_buy_100 = True
        self.upgraded = False
        self.progression_level = 0
        self.box = (self.base[0]-60, self.base[1], self.base[0]+500, self.base[1]+100)

    def _update_coords(self, newbase):

        self.base = newbase
        self._update_name_coord()
        self._update_buy_coord()

    def _update_name_coord(self):

        self.namebox = (self.base[0], self.base[1]+5, self.base[0]+370, self.base[1]+37)

    def _update_buy_coord(self):

        self.buy_coord = (self.base[0] + self.buy_coord_offset[0], self.base[1] + self.buy_coord_offset[1])

    def ocr_name(self):

        textcolor = (102, 51, 204), (254, 254, 254)

        crop = (self.base[0], self.base[1]+5, self.base[0]+370, self.base[1]+37)

        # TODO change it to be self.namebox as soon as you can test
        # myimage = self.gs.window.screen.crop(self.namebox)
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

    def try_buy(self, amount, timer=True):


        keys = {10: "shift", 25: "z", 100: "ctrl"}

        hotkey = False
        if amount in keys:
            hotkey = keys[amount]
        # print("amount", amount, "hotkey", hotkey)

        if timer:
            if not self.buy_timer():
                return False
        if self.isvisible:
            if hotkey:
                if not self.gs.window.infocus:
                    # print("exiting because window isnt in focus")
                    return False
                gui.keyDown(key=hotkey)
                time.sleep(.2)
                self.gs.window.update_screen()
            if self.can_buy():
                if timer:
                    self.check_interval *= .75
                self.gs.window.click(self.buy_coord)
                self.level += amount
                self.gs.lastherobuy = datetime.datetime.now()
                if hotkey:
                    gui.keyUp(key=hotkey)
                return True
            else:
                if timer:
                    self.check_interval *= 2
                    if self.check_interval > datetime.timedelta(minutes=30):
                        self.check_interval = datetime.timedelta(minutes=30)
        if hotkey:
            gui.keyUp(key=hotkey)
        return False

    def buy_up_to(self, amount):

        if not self.gs.window.infocus:
            return

        can_buy_25 = True
        can_buy_10 = True
        purchased = False
        purchased_one = False
        while self.level < amount:
            if self.can_buy_100 and amount-self.level >= 100:
                # print("trying to buy 100", self)
                if not self.try_buy(100, timer=False):
                    # print("cant ever buy 100 of", self)
                    self.can_buy_100 = False
                else:
                    purchased = True
            elif can_buy_25 and amount-self.level >= 25:
                # print("trying to buy 25", self)
                if not self.try_buy(25, timer=False):
                    # print("cant buy 25 of", self)
                    can_buy_25 = False
                else:
                    purchased = True
            elif can_buy_10 and amount-self.level >= 10:
                # print("trying to buy 10", self)
                if not self.try_buy(10, timer=False):
                    # print("cant buy 10 of", self)
                    can_buy_10 = False
                else:
                    purchased = True
            else:
                # print("trying to buy 1", self)
                self.gs.window.update_screen()
                if not self.try_buy(1, timer=False):
                    # print("done buying", self)z
                    if purchased:
                        self.check_interval *= .75
                    else:
                        if amount-self.level < 10 and purchased_one:
                            self.check_interval *= .75
                        else:
                            self.check_interval *= 1.5
                            if self.check_interval > datetime.timedelta(minutes=30):
                                self.check_interval = datetime.timedelta(minutes=30)
                    return
                else:
                    purchased_one = True

    def scroll_to(self, wait=False):

        if wait:
            self.gs.visiblewait = True

        DEBUG = False

        # if there are no visible heroes calculation is impossible dont do shit.
        if not self.gs.hero.visible:
            return

        # scrollpositions = [335, 367, 400, 432, 464, 497, 529, 561, 594, 626, 659, 691, 723, 756, 788]

        currentscroll = 0
        best_distance = 999
        if self.gs.hero.scrollbar in self.gs.hero.scrollpositions:
            currentscroll = self.gs.hero.scrollbar
        else:
            for target in self.gs.hero.scrollpositions:
                distance = abs(self.gs.hero.scrollbar - target)
                if distance < best_distance:
                    best_distance = distance
                    currentscroll = target
        if DEBUG:
            print("currentscroll", currentscroll)

        lowestorderhero = None
        highestorderhero = None
        for hero in self.gs.hero.visible:
            if lowestorderhero is None:
                lowestorderhero = hero
                highestorderhero = hero
            else:
                if hero.order < lowestorderhero.order:
                    lowestorderhero = hero
                if hero.order > highestorderhero.order:
                    highestorderhero = hero
        if DEBUG:
            print("lowest", lowestorderhero.shortname)
            print("highest", highestorderhero.shortname)

        highest_order_hero = None
        for h in self.gs.hero.heroes:
            if highest_order_hero is None:
                highest_order_hero = self.gs.hero.heroes[h]
            if self.gs.hero.heroes[h].order > highest_order_hero.order:
                highest_order_hero = self.gs.hero.heroes[h]
        if DEBUG:
            print("max highest", highest_order_hero.shortname)

        # example im at 400
        # betty clicker is the lowest i cant calc she is order #6
        # self is #3 (brittany) i need to move up one click
        # or self is #10 (alex) i need to move down one click

        scroll = 0
        if self.order < lowestorderhero.order:
            ticks_to_top = (currentscroll - self.gs.hero.scrollpositions[0]) // 32
            if DEBUG:
                print("ticks to top", ticks_to_top)
            heroes_per_tick = (lowestorderhero.order - 1) / ticks_to_top
            if DEBUG:
                print("heroes per tick", heroes_per_tick)
            heroes_to_traverse = lowestorderhero.order - self.order
            if DEBUG:
                print("heroes to traverse", heroes_to_traverse)
            for i in range(15):
                i += 1
                if heroes_to_traverse < heroes_per_tick*i:
                    scroll = i
                    if DEBUG:
                        print("final scroll", scroll)
                    break
        else:
            ticks_to_bottom = (self.gs.hero.scrollpositions[-1] - currentscroll) // 32
            if DEBUG:
                print("ticks to bottom", ticks_to_bottom)
            heroes_per_tick = (highest_order_hero.order - highestorderhero.order) / ticks_to_bottom
            if DEBUG:
                print("heroes per tick", heroes_per_tick)
            heroes_to_traverse = self.order - highestorderhero.order
            if DEBUG:
                print("heroes to traverse", heroes_to_traverse)
            for i in range(14):
                i += 1
                if heroes_to_traverse < heroes_per_tick*i:
                    scroll = -i
                    if DEBUG:
                        print("final scroll", scroll)
                    break
        # pixels_per_scroll = 32
        # scrollbar_height = 453
        # current_pos = 756
        self.gs.step = "Scrolling to " + self.shortname
        self.gs.window.scroll(scroll)

    def reset(self):

        self.level = 0
        self.sethidden()
        self.check_interval = datetime.timedelta(seconds=.1)
        self.lastcheck = datetime.datetime.now()
        self.can_buy_100 = True
        self.upgraded = False
        self.progression_level = 0

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
         'Orntchya Gladeye, Didensy': (31, "banana"),
         'Lilin': (32, "lilin"),
         'Cadmia': (33, "cadmia"),
         'Alabaster': (34, "alabaster"),
         'Astraea': (35, "astraea"), }