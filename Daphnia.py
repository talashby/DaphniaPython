import logging
import tkinter as tk
import keyboard  # using module keyboard
import simpleaudio

# creating tkinter window
from ObserverClient import g_observer_client
from ServerProtocol import CommonParams, EtherColor

root = tk.Tk()

canvas = tk.Canvas(width=1280, height=720, bg='black')
canvas.pack(expand=tk.YES, fill=tk.BOTH)

statistic_text = canvas.create_text(550, 50, fill="white", font="Times 20 italic bold", anchor="nw")

# init eye color array
eye_color_array = []
rect_canvas_array = []
for yy in range(CommonParams.OBSERVER_EYE_SIZE):
    row_color = []
    rect = []
    for xx in range(CommonParams.OBSERVER_EYE_SIZE):
        row_color.append(EtherColor(0, 0, 0))
        rect.append(canvas.create_rectangle(xx * 31, yy * 31, xx * 31 + 30, yy * 31 + 30, width=5, fill='red'))
    eye_color_array.append(row_color)
    rect_canvas_array.append(rect)


def func():
    eye_texture = g_observer_client.get_eye_texture()
    for yy in range(CommonParams.OBSERVER_EYE_SIZE):
        for xx in range(CommonParams.OBSERVER_EYE_SIZE):
            if eye_texture[yy][xx] != eye_color_array[yy][xx]:
                cc = eye_texture[yy][xx]
                color_rgb = (cc.m_colorR * cc.m_colorA // 255) * 65536 + (cc.m_colorG * cc.m_colorA // 255) * 256 + (
                        cc.m_colorB * cc.m_colorA // 255)
                hex_str = '#' + hex(color_rgb)[2:].zfill(6)
                canvas.itemconfig(rect_canvas_array[yy][xx], fill=hex_str)

    # check crumb eaten
    outPosition, outMovingProgress, outLatitude, outLongitude, outIsEatenCrumb = g_observer_client.get_state_ext_params()
    if outIsEatenCrumb:
        g_observer_client.grab_eaten_crumb_pos()
        filename = 'bubble_pop.wav'
        wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()

    # statistics
    quantumOfTimePerSecond, universeThreadsNum, tickTimeMusAverageUniverseThreadsMin, \
    tickTimeMusAverageUniverseThreadsMax, tickTimeMusAverageObserverThread, \
    clientServerPerformanceRatio, serverClientPerformanceRatio = g_observer_client.get_statistics_params()
    strOut = "STATISTICS:"
    strOut += "\nFPS (quantum of time per second): " + str(quantumOfTimePerSecond)
    strOut += "\nUniverse threads count: " + str(universeThreadsNum)
    if universeThreadsNum > 0:
        strOut += "\nTick time(ms). Observer thread: " + str(tickTimeMusAverageObserverThread / 1000.0)
        strOut += "\nTick time(ms). Fastest universe thread: " + str(tickTimeMusAverageUniverseThreadsMin / 1000.0)
        strOut += "\nTick time(ms). Slowest universe thread: " + str(tickTimeMusAverageUniverseThreadsMax / 1000.0)
    strOut += "\nClient-Server performance ratio: " + str(clientServerPerformanceRatio / 1000.0)
    strOut += "\nServer-Client performance ratio: " + str(serverClientPerformanceRatio / 1000.0)
    strOut += "\nPosition: (" + str(outPosition.m_posX) + ", " + str(outPosition.m_posY) + ", " + str(
        outPosition.m_posZ) + ")"
    strOut += "\nLattitude: " + str(outLatitude)
    strOut += "\nLongitude: " + str(outLongitude)
    canvas.itemconfig(statistic_text, text=strOut)

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


def on_closing():
    g_observer_client.stop_simulation()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
tk.mainloop()
