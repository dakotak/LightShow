
import machine
import neopixel
from utime import sleep_ms

from led_controller import Controller

LED_COUNT = 50
NP_PIN = 27
LOOP_SLEEP_MS = 250


np = neopixel.NeoPixel(machine.pin(NP_PIN), LED_COUNT)
controller = Controller(LED_COUNT)

def update_leds():
    for i in range(LED_COUNT):
        np[i] = controller._leds[i].rgb
    np.write()


def run_show():
    while True:
        controller.event_loop()
        update_leds()
        sleep_ms(LOOP_SLEEP_MS)
