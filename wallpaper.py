__author__ = 'Joel'

import os
import sys

from PIL import Image
from PIL import ImageDraw

limit = 1000


clickable = (45,50)


sizes = [(640,480), (800,600), (1024,768), (1152,864), (1280,960), (1280,1024), (1344,1008), (1400,1050), (1600,1200), (1280,720), (1280,800), (1280,900), (1680, 1050), (1920,1080), (1920,1200),
         (2048,1536), (2560, 1440), (2560,1600), (1920*3,1080), (1920*3,1200), (1080*3,1920), (1200*3,1920), (2560*3,1440), (2560*3, 1600), (1440*3,2560), (1600*3,2560), (960,600), (1024,640),
         (1280,480), (1344,840), (1440,900), (1600,600), (1600,1000), (2048,768), (2304,864), (2560,960), (2560,1024), (3200,1200)]



sortedsizes = [(640, 480, 126), (800, 600, 216), (960, 600, 252), (1280, 480, 252), (1024, 640, 276), (1024, 768, 345),
               (1280, 720, 392), (1600, 600, 432), (1152, 864, 442), (1280, 800, 448), (1344, 840, 480), (1280, 900, 504),
               (1280, 960, 532), (1280, 1024, 560), (1440, 900, 576), (1344, 1008, 600), (1400, 1050, 651), (2048, 768, 690),
               (1600, 1000, 720), (1680, 1050, 777), (1600, 1200, 864), (2304, 864, 867), (1920, 1080, 903), (1920, 1200, 1032),
               (2560, 960, 1083), (2560, 1024, 1140), (2048, 1536, 1380), (2560, 1440, 1596), (3200, 1200, 1704), (2560, 1600, 1824),
               (5760, 1080, 2688), (3240, 1920, 2736), (3600, 1920, 3040), (5760, 1200, 3072), (7680, 1440, 4788), (4320, 2560, 4896),
               (4800, 2560, 5457), (7680, 1600, 5472)]


shortsizes = [(640, 480, 126)]

masked_file = r"F:\Documents\Python\heroclicker\source\masked_final.bmp"
masked = Image.open(masked_file)


SaveDirectory = r'F:\Documents\Python\heroclicker\clean_fish'
cleanlist = os.listdir(SaveDirectory)



for desired in sortedsizes:
    output = Image.new(masked.mode, (desired[0], desired[1]))
    output.putpixel((0, 0), (255,255,255))
    ImageDraw.floodfill(image=output, xy=(0, 0), value=(255, 255, 255))

    width = int(desired[0]/clickable[0] + .5)
    height = int(desired[1]/clickable[1] + .5)
    total = width * height
    if total > limit:
        reuse = total / limit
    else:
        reuse = 0
    print("Resolution:", str(desired[0]) + "x" + str(desired[1]), "width:", width, "Height:", height, "Clickables:", width*height, "reuse:", str(reuse)[:3])
    currentx = 0
    currenty = 0
    fishcounter = 0
    while True:
        if fishcounter == len(cleanlist):
            fishcounter = 0
        freshfishname = cleanlist[fishcounter]

        # print("working on", freshfishname)

        # if fishcounter > desired[2]:
        if currenty >= desired[1]:
            output.save("wallpaper/" + str(desired[0]) + "x" + str(desired[1]) + ".png")
            break
        filename = "\\".join((SaveDirectory, freshfishname))
        freshfish = Image.open(filename)
        maxx, maxy = freshfish.size
        for y in range(maxy):
            for x in range(maxx):
                if currenty <= desired[1] -1 and currentx <= desired[0] -1:
                    # print(currenty, currentx)
                    currentdata = freshfish.getpixel((x, y))
                    try:
                        output.putpixel((currentx, currenty), currentdata)
                    except IndexError:
                        print(currentx, currenty)
                        output.save("wallpaper/" + str(desired[0]) + "x" + str(desired[1]) + ".png")
                        sys.exit(0)
                currentx += 1
            currenty += 1
            currentx -= 45
        # -------- fish done ---------
        # print("where in the row am i", currentx, desired[0] -1)
        if currentx <= desired[0] -1:
            # if i still have space left on the current row move one pixel to the right to start the next image
            currentx += 45
            # reset the y to the top of the row
            currenty -= 50
            # print("next image same row", currentx, currenty)
        else:
            # reset x to 0
            currentx = 0
            # print("next image new row", currentx, currenty)
        fishcounter += 1
