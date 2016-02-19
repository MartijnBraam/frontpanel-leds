import serial
import math
from cobs import cobs
from time import sleep
import psutil
import argparse


def write_packet(packet):
    data = cobs.encode(bytearray(packet))
    ser.write(data + b"\0")


def write_frame(frame):
    if flip_horisontal:
        frame = frame[::-1]
    if flip_vertical:
        old_frame = frame
        frame = []
        for col in old_frame:
            frame.append(col[::-1])
    flat_frame = [item for sublist in frame for item in sublist]
    write_packet(flat_frame)


def paint(frame):
    pass


def render_system_usage_bars(cpu, mem, netin, netout):
    frame = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    frame = render_bar(frame, 0, cpu)
    frame = render_bar(frame, 2, mem)
    frame = render_bar(frame, 4, netin)
    frame = render_bar(frame, 6, netout)
    return frame


def render_bar(frame, col, value):
    dots = int((value * 6) + 0.5)
    if dots > 5:
        dots = 5

    for i in range(0, dots):
        frame[col][5 - i] = 1

    if dots > 0:
        frame[col][6 - dots] = 1

    return frame


while False:
    sleep(0.3)

    cpu = psutil.cpu_percent() / 100.0

    val = int((cpu * 6) + 0.5)
    if val > 5:
        val = 5

    val = 5 - val

    row = [0] * 6

    for j in range(val, 6):
        row[j] = 10
    row[val] = 1

    write_packet(row)


def mode_bars():
    while True:
        cpu = psutil.cpu_percent() / 100.0
        mem = psutil.virtual_memory().percent / 100.0
        netin = 0.5
        netout = 0.5
        frame = render_system_usage_bars(cpu, mem, netin, netout)
        write_frame(frame)
        sleep(0.3)


def mode_demo():
    i = 0
    while True:
        i += 30
        sleep(0.1)
        pos = math.sin(math.radians(i))
        val = int((pos * 3) + 3)
        if val == 6:
            val = 5
        row = [0] * 6

        for j in range(val, 6):
            row[j] = 10
        row[val] = 1

        write_packet(row)


def main(device, mode, hflip=False, vflip=False):
    global ser, flip_horisontal, flip_vertical
    ser = serial.Serial(device, 115200)
    flip_horisontal = hflip
    flip_vertical = vflip

    if mode == 'demo':
        mode_demo()
    elif mode == 'bars':
        mode_bars()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frontpanel led controller")
    parser.add_argument('--hflip', help="Flip the display output on the horisontal axis", action="store_true")
    parser.add_argument('--vflip', help="Flip the display output on the vertical axis", action="store_true")
    parser.add_argument('device', help="Path to the serial port", default="/dev/frontpanel")
    parser.add_argument('mode', help="Chooses what to display", choices=['bars', 'graph', 'demo'])
    args = parser.parse_args()
    main(args.device, args.mode, args.hflip, args.vflip)
