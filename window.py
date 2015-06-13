

class Window(object):

    def __init__(self, image):

        self.image = image

    def find_window(self):

        xbox = self.find_x()
        if xbox is None:
            return (0,0,0,0)
        # self.image.crop(xbox).show()

        left, top, right, bottom = xbox
        left = self.find_top_window_line(xbox)
        right += 7
        # titlebarbox = (left, top, right, bottom)
        bottom = self.find_right_window_line(right, bottom)

        fullwindowbox = (left, top, right, bottom)

        return fullwindowbox

    def find_top_window_line(self, xbox):

        white_pix = (xbox[0] + 1, xbox[1] + 1)

        # skip over the other buttons
        x = xbox[0] - 60


        while x > 0:
            x-=1

            new_pix = (x, xbox[1] + 1)
            r, g, b = self.image.getpixel(new_pix)

            if r < 200 or g < 200 or b < 200:
                return x - 5

    def find_right_window_line(self, x, y):

        max_x, max_y = self.image.size

        while y < max_y - 1:
            y+=1

            new_pix = (x-2, y)
            r, g, b = self.image.getpixel(new_pix)

            if r < 200 or g < 200 or b < 200:
                return y + 6

    def find_x(self):

        # the x is 46 pixels wide and is 252, 252, 252 on rgb
        # the whole x is about 49x20

        max_x, max_y = self.image.size

        refference_color = (252, 252, 252)

        pixelskip = 40

        for x in range(max_x//pixelskip):
            for y in range(max_y):
                if self.image.getpixel((x*pixelskip, y)) == refference_color:
                    # print(x*pixelskip, y)
                    yplusone = self.image.getpixel((x*pixelskip, y+1))
                    if yplusone != refference_color and yplusone[0] > 150:
                        xbox = self.find_x_line((x*pixelskip, y), refference_color)
                        if xbox:
                            return xbox

    def find_x_line(self, point, rc):

        myx, myy = point

        start = 0
        end = 0
        for x_mod in range(46):
            if not start and self.image.getpixel((myx-x_mod, myy)) != rc:
                start = myx-x_mod
            if not end and self.image.getpixel((myx+x_mod, myy)) != rc:
                end = myx+x_mod
            if start and end:
                if end-start == 47:
                    box = (start, myy-1, end+1, myy+19)
                    # print(box)
                    return box