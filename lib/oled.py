import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

class oled:
    def __init__(self, type):
        self._error = ''
        self._initflag = False
        self._type = type
        # init oled
        self._init_oled()

    def get_errorinfi(self):
        return self._error

    def _init_oled(self):
        # Raspberry Pi pin configuration:
        RST = None     # on the PiOLED this pin isnt used
        # Note the following are only used with SPI:
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        if 'i2c-128*32' == self._type:
            # 128x32 display with hardware I2C:
            self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        elif 'i2c-128*64' == self._type:
            # 128x64 display with hardware I2C:
            self._disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
        else:
            self._initflag = False
            self._error =  'no this type : %s,just i2c-128*32/iwc-128*64'%self._type
            return False

        # Initialize library.
        self._disp.begin()

        # Clear display.
        self._disp.clear()
        self._disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self._width = self._disp.width
        self._height = self._disp.height
        self._image = Image.new('1', (self._width, self._height))

        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)

        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self._width,self._height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        self._top = padding
        bottom = self._height-padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self._x = 0

        # Load default font.
        self._font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        # font = ImageFont.truetype('Minecraftia.ttf', 8)
        return True

    def flush(self, data):
        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self._width, self._height), outline=0, fill=0)

        # Write two lines of text.
        self._draw.text((self._x, self._top),       data[0],  font=self._font, fill=255)
        self._draw.text((self._x, self._top+8),     data[1],  font=self._font, fill=255)
        self._draw.text((self._x, self._top+16),    data[2],  font=self._font, fill=255)
        self._draw.text((self._x, self._top+24),    data[3],  font=self._font, fill=255)
        if 'i2c-128*64' == self._type:
            self._draw.text((self._x, self._top+32),    data[4],  font=self._font, fill=255)
            self._draw.text((self._x, self._top+40),    data[5],  font=self._font, fill=255)
            self._draw.text((self._x, self._top+48),    data[6],  font=self._font, fill=255)
            self._draw.text((self._x, self._top+56),    data[7],  font=self._font, fill=255)
        # Display image.
        self._disp.image(self._image)
        self._disp.display()

        return True
