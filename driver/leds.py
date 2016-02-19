import serial
import math
from cobs import cobs
from time import sleep
import psutil
import argparse
import datetime

interval = 0.5
netmax = 10 * 1024


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


def write_column(column):
    if flip_vertical:
        column = column[::-1]
    write_packet(column)


def scale_to_leds(value, min, max):
    value = (value - min) / max
    leds = int((value * 6) + 0.5)
    if leds > 5:
        leds = 5
    return leds


def render_graph_point(value, min=0, max=100):
    val = scale_to_leds(value, min, max)

    val = 5 - val

    row = [0] * 6

    for j in range(val, 6):
        row[j] = 10
    row[val] = 1

    write_column(row)


def render_bar(frame, col, value, min=0, max=100):
    dots = scale_to_leds(value, min, max)
    for i in range(0, dots):
        frame[col][5 - i] = 1

    if dots > 0:
        frame[col][6 - dots] = 1

    return frame


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
    frame = render_bar(frame, 4, netin, max=netmax)
    frame = render_bar(frame, 6, netout, max=netmax)
    return frame


def mode_bars():
    while True:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        netin = psutil.net_io_counters(pernic=False).bytes_recv / 1024
        netout = psutil.net_io_counters(pernic=False).bytes_sent / 1024
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

        write_column(row)


def mode_graph_cpu():
    while True:
        sleep(interval)
        cpu = psutil.cpu_percent()
        render_graph_point(cpu, 0, 100)


def mode_graph_memory():
    while True:
        sleep(interval)
        mem = psutil.virtual_memory().percent
        render_graph_point(mem, 0, 100)


def mode_clock():
    while True:
        sleep(1)
        now = datetime.datetime.now()
        seconds = now.second % 2
        frame = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, seconds],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
        write_frame(frame)


def main(device, mode, hflip=False, vflip=False):
    global ser, flip_horisontal, flip_vertical
    ser = serial.Serial(device, 115200)
    flip_horisontal = hflip
    flip_vertical = vflip

    if mode == 'demo':
        mode_demo()
    elif mode == 'bars':
        mode_bars()
    elif mode == 'graph-cpu':
        mode_graph_cpu()
    elif mode == 'graph-memory':
        mode_graph_memory()
    elif mode == 'clock':
        mode_clock()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frontpanel led controller")
    parser.add_argument('--hflip', help="Flip the display output on the horisontal axis", action="store_true")
    parser.add_argument('--vflip', help="Flip the display output on the vertical axis", action="store_true")
    parser.add_argument('--interval', '-i', help="Update interval for chart modes in seconds", type=float, default=0.5)
    parser.add_argument('--netmax', '-n',
                        help="The scaling for network usage. Defines the maximum value in KB/s (default 10 MB/s)",
                        default=10 * 1024, type=int)
    parser.add_argument('device', help="Path to the serial port", default="/dev/frontpanel")
    parser.add_argument('mode', help="Chooses what to display", choices=['bars', 'graph-cpu', 'graph-memory', 'demo', 'clock'])
    args = parser.parse_args()
    interval = args.interval
    netmax = args.netmax
    main(args.device, args.mode, args.hflip, args.vflip)
