# Omar Metwally, MD
# A N A L O G  L A B S 
# omar@analog.earth
# License: Analog Labs License (analog.earth)

import threading
from queue import Queue
import epd2in7b
from PIL import Image, ImageFont, ImageDraw
import RPi.GPIO as GPIO
from time import sleep

q = Queue()

COLORED = 1
UNCOLORED = 0
GPIO.setmode(GPIO.BCM)
key1 = 5
key2 = 6
key3 = 13
key4 = 19

GPIO.setup(key1,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key2,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key3,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key4,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def update_2in7epd(text_string,image_path=None, sleep_sec=1):
    epd = epd2in7b.EPD()
    epd.init()

    # clear the frame buffer
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 14)

    print(text_string)

    if image_path:
        frame_black = epd.get_frame_buffer(Image.open(image_path))
    if text_string:
            epd.draw_string_at(frame_black, 4, 4, text_string, font, COLORED)
            epd.display_frame(frame_black, frame_red)
            sleep(sleep_sec)


class epdUpdater(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    
    def run(self):
        print("Starting "+self.name)

        while True:
            if q.empty():
                #print("Queue is empty")
                pass
            else:
                z = q.get(block=False)
                if 'exit' in z:
                    exit(0)
                elif 'key1' in z:
                    print('Key1 was pressed')
                    with q.mutex:
                        q.queue.clear()
                    update_2in7epd('Key1 was pressed',sleep_sec=1)
                elif 'key2' in z:
                    print('Key2 was pressed')
                    with q.mutex:
                        q.queue.clear()

                    update_2in7epd('Key2 was pressed',sleep_sec=1)

                elif 'key3' in z:
                    print('Key3 was pressed')
                    update_2in7epd('Key3 was pressed',sleep_sec=1)

                elif 'key4' in z:
                    print('Key4 was pressed')
                    update_2in7epd('Key4 was pressed',sleep_sec=1)
                    exit(0)

                elif 'greet' in z:
                    print("Hello, World!")
                    update_2in7epd(text_string="Hello, World!")

class keypadReader(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        print('initializing keypadReader thread')

    def run(self):
        while True:
            key1state = GPIO.input(key1)
            key2state = GPIO.input(key2)
            key3state = GPIO.input(key3)
            key4state = GPIO.input(key4)

            #z = input("Press a key: ")
            if not key1state and key2state and key3state and key4state:
                q.put('key1')
            if not key2state and key1state and key3state and key4state:
                q.put('key2')
            if not key3state and key1state and key2state and key4state:
                q.put('key3')
            if not key4state and key1state and key2state and key3state:
                q.put('key4')


thread2 = keypadReader(2, "Keypad-Thread",5)
thread1 = epdUpdater(1, "Screen-Thread",5)

thread1.start()
thread2.start()


