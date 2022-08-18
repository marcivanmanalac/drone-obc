from time import sleep
import threading
import platform
if platform.system() == 'Linux':
    from gpiozero import LED


class LinkLED:

    def __init__(self):
        # blinking LED on GPIO #21
        self.led = LED(21)
        self.normal_blinking_half_period = 1  # s
        self.quick_blinking_half_period = 0.1  # s
        self.thread_reference = None
        self.mode = 0
        self.stop = 0

    def blink(self):
        if self.mode == 0:
            blinking_half_pêriod = self.normal_blinking_half_period
        else:
            blinking_half_pêriod = self.quick_blinking_half_period
        while not self.stop:
            self.led.on()
            # print("on")
            sleep(blinking_half_pêriod)
            self.led.off()
            # print("off")
            sleep(blinking_half_pêriod)

    def start_blink(self, mode):
        try:
            self.mode = mode
            self.thread_reference = threading.Thread(name='ledblink', target=self.blink)
            self.thread_reference.start()
        except :
            print("Error: unable to start blinking thread")

    def stop_blinking(self):
        self.stop = 1
        self.thread_reference.join()

    def reset(self):
        self.stop = 0
