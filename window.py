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

import time
import datetime

import PIL
from PIL import ImageGrab
import pyautogui as gui

from win32con import MOUSEEVENTF_WHEEL
import win32api
import win32gui


class Window(object):

    def __init__(self, gs):

        self.gs = gs
        self.screen = None
        # left, top, right, bottom
        self.box = (0, 0, 0, 0)
        self.desiredsize = (1662, 942)
        self.infocus = False


    def find_window(self):

        xbox = self.find_x()
        if xbox is None:
            return 0, 0, 0, 0
        # self.image.crop(xbox).show()

        left, top, right, bottom = xbox
        left = self.find_top_window_line(xbox)
        right += 7
        # titlebarbox = (left, top, right, bottom)
        bottom = self.find_right_window_line(right, bottom)

        return left, top, right, bottom

    def find_top_window_line(self, xbox):

        # skip over the other buttons
        x = xbox[0] - 60

        while x > 0:
            x -= 1

            new_pix = (x, xbox[1] + 1)
            r, g, b = self.screen.getpixel(new_pix)

            if r < 200 or g < 200 or b < 200:
                return x - 5

    def find_right_window_line(self, x, y):

        max_x, max_y = self.screen.size

        while y < max_y - 1:
            y += 1

            new_pix = (x-2, y)
            r, g, b = self.screen.getpixel(new_pix)

            if r < 200 or g < 200 or b < 200:
                return y + 6

    def find_x(self):

        # the x is 46 pixels wide and is 252, 252, 252 on rgb
        # the whole x is about 49x20

        max_x, max_y = self.screen.size

        refference_color = (252, 252, 252)

        pixelskip = 40

        for x in range(max_x//pixelskip):
            for y in range(max_y):
                if self.screen.getpixel((x*pixelskip, y)) == refference_color:
                    # print(x*pixelskip, y)
                    yplusone = self.screen.getpixel((x*pixelskip, y+1))
                    if yplusone != refference_color and yplusone[0] > 150:
                        xbox = self.find_x_line((x*pixelskip, y), refference_color)
                        if xbox:
                            return xbox

    def find_x_line(self, point, rc):

        myx, myy = point

        start = 0
        end = 0
        for x_mod in range(46):
            if not start and self.screen.getpixel((myx-x_mod, myy)) != rc:
                start = myx-x_mod
            if not end and self.screen.getpixel((myx+x_mod, myy)) != rc:
                end = myx+x_mod
            if start and end:
                if end-start == 47:
                    box = (start, myy-1, end+1, myy+19)
                    # print(box)
                    return box

    def adjust_size(self):
        c = 0

        while True:
            hwnd = win32gui.GetForegroundWindow()
            if win32gui.GetWindowText(hwnd) == "Clicker Heroes":
                rect = win32gui.GetWindowRect(hwnd)
                x = rect[0]
                y = rect[1]
                w = rect[2] - x
                h = rect[3] - y
                if (w, h) == self.desiredsize:
                    print("\rClicker Heroes located and is sized correctly                                     ", end="")
                    break
                else:
                    win32gui.SetWindowPos(hwnd, 0, x, y, self.desiredsize[0], self.desiredsize[1], 0)
            else:
                print("\rplease bring the clicker hero window into focus(make it the active window)", c, end="")

            time.sleep(.1)
            c += 1
        print()

    def collect_screen(self):

        self.screen = PIL.ImageGrab.grab()
        if self.gs.idle:
            return
        hwnd = win32gui.GetForegroundWindow()
        if win32gui.GetWindowText(hwnd) == "Clicker Heroes":
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            if (w, h) != self.desiredsize:
                win32gui.SetWindowPos(hwnd, 0, x, y, self.desiredsize[0], self.desiredsize[1], 0)
            else:
                self.box = rect
            self.infocus = True
        else:
            self.infocus = False

    def update_screen(self):

        self.screen = PIL.ImageGrab.grab()

    def scroll(self, amount):

        if amount < 120:
            amount *= 120

        currentMouseX, currentMouseY = gui.position()
        win32api.mouse_event(MOUSEEVENTF_WHEEL, currentMouseX, currentMouseY, amount, 0)
        # there is visual lag, prevent further processing until the lag completes
        time.sleep(.3)

    def click(self, coord):

        currentMouseX, currentMouseY = gui.position()
        gui.click(coord[0], coord[1])
        gui.moveTo(currentMouseX, currentMouseY)

if __name__ == "__main__":

    start = datetime.datetime.now()
    for i in range(100):
        PIL.ImageGrab.grab()
    print(datetime.datetime.now()-start)
    hwnd = win32gui.GetForegroundWindow()
    if win32gui.GetWindowText(hwnd) == "Clicker Heroes":
        nextstart = datetime.datetime.now()
        for i in range(100):
            hwnd2 = win32gui.GetForegroundWindow()
            win32gui.GetWindowText(hwnd2)
            rect = win32gui.GetWindowRect(hwnd2)
            PIL.ImageGrab.grab(rect)
        print(datetime.datetime.now()-nextstart)
