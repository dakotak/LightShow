
import time
from tkinter import *
from tkinter.ttk import *


from led_controller import Controller

LED_COUNT = 25
ROW_WIDTH = 5

controller = Controller(LED_COUNT)

led_widgets = []


def create_circle(x, y, r, canvas): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1)


class LEDCell(Frame):

    def __init__(self, parent, led):
        Frame.__init__(self, parent)
        self.led = led

        # String Vars
        self.hsv_v = IntVar()
        

        # Make the innder frame to show the status:
        # is_off = Red
        # is_on = Green
        # in_transition = Yellow

        self._init_canvas()

        self.alphaP = Progressbar(self, orient=VERTICAL, length=50, mode='determinate', variable=self.hsv_v)
        self.alphaP.pack(side=LEFT)

        Label(self, text='LED').pack()
        self._dlabel = Label(self, textvariable=self.hsv_v)
        self._dlabel.pack()

        self._update_icon()
        self._update_vars()

    def _init_canvas(self):
        # Create the canvas for the status icon
        self.canvas = Canvas(self, width=50, height=50)
        self.canvas.pack(side=LEFT)
        # Draw a circle in it
        self.status_ring = create_circle(25, 25, 20, self.canvas)
        self.color_icon = create_circle(25, 25, 15, self.canvas)

    def _update_icon(self):
        self.canvas.itemconfig(self.color_icon, fill="#%02x%02x%02x" % self.led.rgb)
        # Update the ring color
        # Green: On
        # Red: Off
        # Yellow: Transition
        if self.led.in_transition:
            color='yellow'
        elif self.led.is_on:
            color='green'
        elif self.led.is_off:
            color='red'
        else:
            color='orange'
        self.canvas.itemconfig(self.status_ring, fill=color)


    def _update_vars(self):
        a = int(self.led.hsv[2]*100)
        self.hsv_v.set(a)


    def update(self):
        self._update_vars()
        self._update_icon()





root = Tk()

info_frame = Frame(root)
info_frame.pack()


pct_on = StringVar()
pct_off = StringVar()
pct_trans = StringVar()

label_pct_on = Label(info_frame, textvariable=pct_on)
label_pct_off = Label(info_frame, textvariable=pct_off)
label_pct_trans = Label(info_frame, textvariable=pct_trans)


def update(times, sleep=None):
    def inner():
        nonlocal times
        # Check if times is a Var
        if type(times) is not int and hasattr(times, 'get'):
            times = int(times.get())
        for _ in range(times):
            controller.event_loop()
            for l in led_widgets:
                l.update()
            # Update the Info Labels
            pct_on.set(f'ON: {int(controller.percent_on * 100)}%')
            pct_off.set(f'OFF: {int(controller.percent_off * 100)}%')
            pct_trans.set(f'Transitioning {int(controller.percent_transitioning * 100)}%')
            root.update()
            if sleep != None:
                time.sleep(sleep)
        #     print('.', end='')
        print('----- Done -----')
    return inner



update_count = Entry(info_frame)
update_count.insert(0, '5000')
update_button = Button(info_frame, text="Update", command=update(10))
update_button_slow = Button(
    info_frame,
    text="Update Slow",
    command=update(update_count, 0.05)
)
update_button.pack(side=LEFT)
update_count.pack(side=LEFT)
update_button_slow.pack(side=LEFT)




label_pct_on.pack()
label_pct_off.pack()
label_pct_trans.pack()


led_frame = Frame(root)
led_frame.pack()

for i in range(LED_COUNT):
    x, y = i % ROW_WIDTH, int(i / ROW_WIDTH)

    w = LEDCell(led_frame, controller._leds[i])
    w.grid(row=y, column=x, padx=5, pady=5)
    led_widgets.append(w)


root.mainloop()
