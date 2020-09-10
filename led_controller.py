
import random

def hsv_to_rgb(h, s, v):
        if s == 0.0: return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)


def turn_on(count=100):
    for i in range(count):
        # Tween from 0 to 1 in count steps
        value = translate(i+1, 0, count, 0, 1)
        yield (0, 0, value)


def turn_off(count=100):
    for i in range(count):
        value = translate(i+1, 0, count, 1, 0)
        yield (0, 0, value)
    # # Ensure the LED is off all the way
    # yield (0, 0, 0)


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


class LED:

    def __init__(self):
        self._transition_generator = None
        self._hsv = (0, 0.0, 0.0)

    @property
    def rgb(self):
        rbg = hsv_to_rgb(*self._hsv)
        return tuple([int(i*255) for i in rbg])

    @property
    def hsv(self):
        return self._hsv

    @property
    def is_on(self):
        """Return True if the LED is on at all."""
        return self._hsv[2] > 0

    @property
    def is_off(self):
        """Return True if the LED is all the way off."""
        return self._hsv[2] == 0

    @property
    def in_transition(self):
        """Return True if this LED is changing State."""
        return self._transition_generator is not None

    @property
    def value_direction(self):
        p, c = self._previous_hsv[2], self._hsv[2]
        if p == c:
            return 'STALE'
        elif p > c:
            return "DOWN"
        elif p < c:
            return "UP"
    
    def update(self):
        """Update the LED color from the generator.
        
        Returns True if an update was made or False if no update was made.
        """
        #print('LED UPDATING')
        if not self.in_transition:
            #print('LED Not in transition')
            return False
        
        self._previous_hsv = self._hsv
        previous = self._hsv
        try:
            self._hsv = next(self._transition_generator)
        except StopIteration:
            self._transition_generator = None
        
        return previous != self._hsv


class Controller:
    """Controls the LEDs and applies transition functions to them."""

    # Statistics for LEDs
    stats_led_on_min = 0.7
    stats_led_on_max = 0.5
    stats_led_in_transition_max = 0.4
    stats_led_on_chance = 0.2 # Chance of an LED getting turned on after the conditions above are met
    stats_led_off_chance = 0.3 # Chance of an LED getting turned off after the conditions above are met
    stats_change_chance = 0.1
    stats_duration_min = 50
    stats_duration_max = 300
    stats_duration_mode = 100

    def __init__(self, led_count, transition_generators=[]):
        self._led_count = led_count
        self._leds = [LED() for _ in range(led_count)]
        self._transition_generators = transition_generators

    @property
    def stale_leds(self):
        """Returns all LEDs that are not in a transition."""
        return [l for l in self._leds if not l.in_transition]

    def get_on_leds(self, in_transition=False):
        leds = self._leds if in_transition else self.stale_leds
        return list(filter(lambda l: l.is_on, leds))

    def get_off_leds(self, in_transition=False):
        leds = self._leds if in_transition else self.stale_leds
        return list(filter(lambda l: l.is_off, leds))

    def get_transitioning_leds(self):
        return [l for l in self._leds if l._transition_generator is not None]

    def _run_transitions(self):
        """Runs all update functions on LEDs with transitions."""
        for l in self._leds:
            l.update()
        #map(lambda l: l.update(), self.get_transitioning_leds())
    
    @property
    def percent_on(self):
        return len(self.get_on_leds())/self._led_count

    @property
    def percent_off(self):
        return len(self.get_off_leds())/self._led_count

    @property
    def percent_transitioning(self):
        return len(self.get_transitioning_leds())/self._led_count

    def update_leds(self):
        # Update all the LEDs
        for led in self._leds:
            led.update()

    def _attempt_turn_on(self):
        print('ON:', end='')
        if random.random() > self.stats_led_on_chance:
            print('S', end=' ')
            return False

        off = self.get_off_leds()
        # Check if LEDs need to be turned on
        # if self.stats_led_on_min > len(on)/self._led_count and len(off) > 0:
        if self.stats_led_on_min > self.percent_on and len(off) > 0:
            # Turn an LED on
            print('1', end=' ')
            # print('Turning on LED')
            led = random.choice(off)
            duration = int(random.triangular(
                self.stats_duration_min,
                self.stats_duration_max,
                self.stats_duration_mode
            ))
            led._transition_generator = turn_on(duration)
            return True
        else:
            print('0', end=' ')
        return False

    def _attempt_turn_off(self):
        print('OFF:', end='')
        if random.random() > self.stats_led_off_chance:
            print('S', end=' ')
            return False

        on = self.get_on_leds()
        p_on = len(on)/self._led_count
        # print(f'Percent on: {p_on}')
        if self.stats_led_on_max < p_on and len(on) > 0:
            print('1', end=' ')
            # print('Turning off LED')
            led = random.choice(on)
            duration = int(random.triangular(
                self.stats_duration_min,
                self.stats_duration_max,
                self.stats_duration_mode
            ))
            led._transition_generator = turn_off(duration)
            return True
        else:
            print('0', end=' ')
        return False

    def event_loop(self):
        self._event_loop()
        self.update_leds()
        print('>')

    def _event_loop(self):
        """Called eachtime the event loop runs."""

        # Use stats to apply transitions
        if random.random() > self.stats_change_chance:
            print('S', end=' ')
            return
        else:
            print('R', end=' ')
        
        trans = len(self.get_transitioning_leds())

        if self.stats_led_in_transition_max < trans/self._led_count:
            print('T', end=' ')
            return

        self._attempt_turn_on()        
        self._attempt_turn_off()
        

