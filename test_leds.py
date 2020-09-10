
import unittest

from led_controller import Controller, LED, hsv_to_rgb, turn_off, turn_on


class Test_RGB_HSV_Conversion(unittest.TestCase):

    def _test_color(self, hsv, rgb):
        hsv = (hsv[0]/360, *hsv[1::])
        converted = hsv_to_rgb(*hsv)
        converted = tuple([int(i*255) for i in converted])
        self.assertEqual(converted, rgb)

    def test_green(self):
        self._test_color((120, 1, 1), (0, 255, 1))
        

class TestLED(unittest.TestCase):

    def test_off(self):
        l = LED()
        self.assertTrue(l.is_off)
        self.assertFalse(l.is_on)

    def test_on(self):
        l = LED()
        l._hsv = (1, 1, 1)
        self.assertTrue(l.is_on)
        self.assertFalse(l.is_off)

    def test_transition_turn_on(self):
        COUNT = 100
        l = LED()

        self.assertFalse(l.is_on)
        self.assertTrue(l.is_off)
        self.assertIsNone(l._transition_generator)
        l._transition_generator = turn_on(COUNT)
        self.assertIsNotNone(l._transition_generator)
        self.assertTrue(l.is_off)
        self.assertFalse(l.is_on)

        l.update()
        self.assertTrue(l.is_on)
        self.assertFalse(l.is_off)

        [l.update() for _ in range(COUNT)]

        self.assertTrue(l.is_on)
        self.assertFalse(l.is_off)
        self.assertIsNone(l._transition_generator)

    # def test_rgb_output(self):
    #     colors = [
    #         # HSV, RGB
    #         ((120, 1, 1), (0, 255, 0)), # Green
    #         ((100, 1, 1), (85, 255, 0)), # Bright Green
    #     ]
    #     l = LED()

    #     self.assertEqual(l.rgb, (0, 0, 0))

    #     for hsv, rgb in colors:
    #         l._hsv = hsv
    #         self.assertEqual(l.rgb, rgb)






class TestController(unittest.TestCase):

    def test_on_off_leds(self):
        TOTAL = 30
        c = Controller(TOTAL)

        on = c.get_on_leds()
        off = c.get_off_leds()

        # Ensure we get a list back from each method
        self.assertIsInstance(on, list)
        self.assertIsInstance(off, list)

        self.assertEqual(len(on), 0)
        self.assertEqual(len(off), TOTAL)

        

    def test_get_leds_turn_on(self):
        TOTAL = 30
        TURN_ON = 10
        c = Controller(TOTAL)

        # On LEDS should be an empty list
        self.assertEqual(c.get_on_leds(), [])
        self.assertFalse(c.get_on_leds())

        self.assertEqual(len(c.get_off_leds()), TOTAL)
        # Turn on 10 of the LEDs
        for i in range(TURN_ON):
            c._leds[i]._hsv = (1, 1, 1)
        
        self.assertEqual(len(c.get_on_leds()), TURN_ON)
        self.assertEqual(len(c.get_off_leds()), TOTAL-TURN_ON)

    def get_controller(self, total, on, transitions=[], func=turn_on):
        c = Controller(total)
        for i in on:
            c._leds[i]._hsv = (1, 1, 1)

        for i in transitions:
            c._leds[i]._transition_generator = func()

        return c

    def test_get_leds_transitions(self):
        

        c = self.get_controller(30, range(15), range(10, 20))

        on = c.get_on_leds()
        on_t = c.get_on_leds(in_transition=True)
        off = c.get_off_leds()
        off_t = c.get_off_leds(in_transition=True)

        self.assertEqual(len(on), 10)
        self.assertEqual(len(on_t), 15)
        self.assertEqual(len(off), 10)
        self.assertEqual(len(off_t), 15)

    def test_transition(self):
        pass


# class TestTransitions(unittest.TestCase):

#     def test_turn_on(self):
#         COUNT = 100
#         t = turn_on(COUNT)

        

        

if __name__ == '__main__':
    unittest.main()
