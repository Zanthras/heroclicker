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
import win32clipboard
import hashlib
import base64
import json
import time
import sys

import pyautogui as gui

bonuses = {
    None: "None",
    0: "None",
    1: "DPS When Idle",
    2: "Click Damage",
    3: "Boss Fight Timer",
    4: "Click Storm Duration",
    5: "Chance of Double Ruby",
    6: "Zones after Ascension",
    7: "Gilded Damage Bonus",
    8: "Metal Detector Duration",
    9: "Golden Click Duration",
    10: "Lucky Strike Duration",
    11: "Power Surge Duration",
    12: "Super Click Duration",
    13: "",
    14: "Hero Soul DPS",
    15: "Critical Click Damage",
    16: "Chance of Treasure Chest",
    17: "Chance of Primal Boss",
    18: "Chance of 10x Gold",
    19: "Hero Cost Decrease",
    20: "Gold Drop from Golden Clicks",
    21: "Gold Drop from Chests",
    22: "Gold Drop",
    23: "",
    24: "Gold When Idle",
    25: "Hero Soul Drops",
}


class Relic(object):

    def __init__(self, index, jsondict, slots, gs):

        self.gs = gs
        self.index = index
        self.name = jsondict["name"]
        self.level = jsondict["level"]
        self.bonus1type = jsondict["bonusType1"]
        self.bonus1level = jsondict["bonus1Level"]
        self.bonus2type = jsondict["bonusType2"]
        self.bonus2level = jsondict["bonus2Level"]
        self.bonus3type = jsondict["bonusType3"]
        self.bonus3level = jsondict["bonus3Level"]
        self.bonus4type = jsondict["bonusType4"]
        self.bonus4level = jsondict["bonus4Level"]
        self.bonuses = {self.bonus1type: self.bonus1level,
                        self.bonus2type: self.bonus2level,
                        self.bonus3type: self.bonus3level,
                        self.bonus4type: self.bonus4level}
        self.rarity = jsondict["rarity"]
        for slot in slots:
            if int(slots[slot]) == int(index):
                self.position = int(slot)
                break
        if self.position <= 4:
            self.equipped = True
        else:
            self.equipped = False

    def get_pos(self, number):

        relics_per_row = 6

        if number <= 4:
            x = 140 + (int(number) - 1) * 185
            y = 360
        elif number < 33:
            number -= 4

            y = 520 + (number - 1) // relics_per_row * 100
            x = 160 + ((number - (number - 1) // relics_per_row * relics_per_row) - 1) * 100
        else:
            assert "You are screwed i cant count that high or low"
        return self.gs.window.box[0] + x, self.gs.window.box[1] + y

    def __gt__(self, other):

        if not isinstance(other, type(self)):
            assert TypeError

        for skill in self.gs.relics.skill_order:
            if skill in other.bonuses and skill not in self.bonuses:
                return False
            if skill in self.bonuses and skill not in other.bonuses:
                return True
            if skill in self.bonuses and skill in other.bonuses:
                if other.bonuses[skill] > self.bonuses[skill]:
                    return False
                elif other.bonuses[skill] < self.bonuses[skill]:
                    return True
                else:
                    # check the next skill
                    continue
        if self.rarity > other.rarity:
            return True
        elif self.rarity < other.rarity:
            return False
        else:
            return True

    def __lt__(self, other):

        return not self.__gt__(other)

    def __str__(self):

        return self.name

    def __repr__(self):

        skills = bonuses[self.bonus1type] + " lvl:" + str(self.bonus1level) + "\n"
        if self.bonus2type:
            skills += bonuses[self.bonus2type] + " lvl:" + str(self.bonus2level) + "\n"
        if self.bonus3type:
            skills += bonuses[self.bonus3type] + " lvl:" + str(self.bonus3level) + "\n"
        if self.bonus4type:
            skills += bonuses[self.bonus4type] + " lvl:" + str(self.bonus4level) + "\n"
        return self.name + " id:" + self.index + " slot:" + str(self.position) + "\n" + skills


class RelicInfo(object):

    def __init__(self, gs):

        self.gs = gs
        self.relics = []
        self.skill_order = [17, 19, 25, 5]

    def load(self):

        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        Debug = False

        if Debug:
            with open ("f:/documents/clickerHeroSave.txt") as f:
                data = f.read()

        ANTI_CHEAT_CODE = "Fe12NAfA3R6z4k0z"
        SALT = "af0ik392jrmt0nsfdghy0"

        if ANTI_CHEAT_CODE in data:
            parts = data.split(ANTI_CHEAT_CODE)
            m = hashlib.md5()
            blah = ""
            for i in range(len(parts[0])):
                if i%2 == 0:
                    blah += parts[0][i]
            m.update(blah.encode('utf-8'))
            m.update(SALT.encode('utf-8'))
            if m.hexdigest() == parts[1]:
                savedata = json.loads(base64.b64decode(blah).decode('utf-8'))
                for itemindex in savedata["items"]["items"]:
                    itemraw = savedata["items"]["items"][itemindex]
                    item = Relic(itemindex, itemraw, savedata["items"]["slots"], self.gs)
                    self.relics.append(item)
                # print(json.dumps(savedata, indent=4))
            else:
                print("bad parse")

    def move_relics(self):

        if len(self.relics) <= 4:
            return 1
        i = 0
        for relic in sorted(self.relics, reverse=True):
            i += 1
            if i < 5:
                if relic.position != i:
                    # print(relic, "should be position", i, relic.get_pos(i), "it is", relic.position, relic.get_pos(relic.position))
                    self.gs.window.drag(start_loc=relic.get_pos(relic.position), end_loc=relic.get_pos(i))
                    bad = relic.position
                    for temp in self.relics:
                        if temp.position == i:
                            temp.position = bad
                            break
                    relic.position = i
                    return 0
            else:
                return 1

    def score_relics(self):

        self.click_tab()

        while True:
            if self.move_relics():
                break

    def collect_relics(self):

        self.gs.window.click(self.gs.window.settings_coord)
        self.gs.window.click((self.gs.window.box[0] + 420, self.gs.window.box[1] + 150))
        time.sleep(.2)
        gui.press('esc')
        time.sleep(.1)
        self.gs.window.click((self.gs.window.box[0] + 1375, self.gs.window.box[1] + 61))

        self.load()

    def click_tab(self):

        self.gs.window.click((self.gs.window.box[0] + 553, self.gs.window.box[1] + 171))
        time.sleep(.1)

    def destroy_relics(self):

        self.click_tab()
        # junk relics
        destroy = True
        if len(self.relics) <= 4:
            destroy = False
        elif len(self.relics) <= 10:
            self.gs.window.click((self.gs.window.box[0] + 425, self.gs.window.box[1] + 650))
            time.sleep(.2)
        elif len(self.relics) <= 16:
            self.gs.window.click((self.gs.window.box[0] + 425, self.gs.window.box[1] + 750))
            time.sleep(.2)
        # This might be wrong... i didnt take a screen cap at this number of relics
        elif len(self.relics) <= 22:
            self.gs.window.click((self.gs.window.box[0] + 425, self.gs.window.box[1] + 850))
            time.sleep(.2)
        else:
            self.gs.window.scroll(-48)
            self.gs.window.click((self.gs.window.box[0] + 425, self.gs.window.box[1] + 880))
        if destroy:
            # confirm
            self.gs.window.click((self.gs.window.box[0] + 723, self.gs.window.box[1] + 598))
            time.sleep(.2)
        self.gs.hero.click_tab()
        # since tab switching resets the menu position
        self.gs.window.update_screen()
        self.gs.hero.collect_visible_heroes(force=True)

    def manage_relics(self):

        print("collecitng relics")
        self.collect_relics()
        print("scoring and moving desired relics")
        self.score_relics()
        print("trashing all remaining relics")
        self.destroy_relics()
