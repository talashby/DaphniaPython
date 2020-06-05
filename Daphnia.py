
import logging
from tkinter import *
import keyboard  # using module keyboard

# creating tkinter window
from ObserverClient import g_observer_client
from ServerProtocol import CommonParams, EtherColor

root = Tk()

canvas = Canvas(width=1280, height=720, bg='black')
canvas.pack(expand=YES, fill=BOTH)

# init eye color array
eye_color_array = []
rect_canvas_array = []
for yy in range(CommonParams.OBSERVER_EYE_SIZE):
    row_color = []
    rect = []
    for xx in range(CommonParams.OBSERVER_EYE_SIZE):
        row_color.append(EtherColor(0, 0, 0))
        rect.append(canvas.create_rectangle(xx*31, yy*31, xx*31+30, yy*31+30, width=5, fill='red'))
    eye_color_array.append(row_color)
    rect_canvas_array.append(rect)

def func():
    eye_texture = g_observer_client.get_eye_texture()
    for yy in range(CommonParams.OBSERVER_EYE_SIZE):
        for xx in range(CommonParams.OBSERVER_EYE_SIZE):
            if eye_texture[yy][xx] != eye_color_array[yy][xx]:
                cc = eye_texture[yy][xx]
                color_rgb = (cc.m_colorR * cc.m_colorA // 256) * 65536 + (cc.m_colorG * cc.m_colorA // 256) * 256 + (cc.m_colorB * cc.m_colorA // 256)
                hex_str = '#' + hex(color_rgb)[2:].zfill(6)
                canvas.itemconfig(rect_canvas_array[yy][xx], fill=hex_str)


    try:  # used try so that if user pressed other than the given key error will not be shown
        left = keyboard.is_pressed('left')
        g_observer_client.set_is_left(left)
        right = keyboard.is_pressed('right')
        g_observer_client.set_is_right(right)
        up = keyboard.is_pressed('up')
        g_observer_client.set_is_up(up)
        down = keyboard.is_pressed('down')
        g_observer_client.set_is_down(down)
        forward = keyboard.is_pressed('space')
        g_observer_client.set_is_forward(forward)
        backward = keyboard.is_pressed('/')
        g_observer_client.set_is_backward(backward)
    except Exception as e:
        logging.exception(e)
    root.after(20, func)


root.after(20, func)
g_observer_client.start_simulation()

mainloop()
