import serial
import math
from cobs import cobs
from time import sleep
import psutil

ser = serial.Serial('/dev/ttyUSB0', 115200)
sleep(1)


def write_packet(packet):
    data = cobs.encode(bytearray(packet))
    ser.write(data + b"\0")


def write_frame(frame):
    frame = reversed(frame)
    flat_frame = [item for sublist in frame for item in sublist]
    write_packet(flat_frame)


def render_bars(cpu, mem, netin, netout):
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
    cpu = psutil.cpu_percent() / 100.0
    mem = psutil.virtual_memory().percent / 100.0
    netin = 0.5
    netout = 0.5
    frame = render_bars(cpu, mem, netin, netout)
    write_frame(frame)
    sleep(0.3)

while False:
    sleep(1)
    write_packet([1])
    sleep(1)
    write_packet([2])
    sleep(1)
    write_packet([3])
    sleep(1)
    write_packet([4])

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

while True:
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