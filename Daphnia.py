
import logging
from tkinter import *
import keyboard  # using module keyboard

# creating tkinter window
from ObserverClient import g_observer_client

root = Tk()

canvas = Canvas(width=1280, height=720, bg='black')
canvas.pack(expand=YES, fill=BOTH)

canvas.create_rectangle(0, 0, 50, 50, width=5, fill='red')


def func():
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            canvas.create_rectangle(30, 30, 80, 80, width=0, fill='blue')
            print('You Pressed A Key!')
    except Exception as e:
        logging.exception(e)
    root.after(10, func)


root.after(10, func)
g_observer_client.start_simulation()

mainloop()
