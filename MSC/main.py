import pygame.midi
import sys
import time
import bridge

debug = not True

cm = ""

buttons = [*range(16, 23 + 1), 64]
dials = [*range(1, 8 + 1)]
dialdata = {}

named_buttons = {
    16: "STOP",
    17: "PLAY",
    18: "RECORD",
    19: "UP",
    20: "DOWN",
    21: "RIGHT",
    22: "LEFT",
    23: "SELECT",
    64: "SUSTAIN"
}

modes = ["manual", "hsv", "rgb", "hsi"]

stime = 0
position = 0
last_fill = [-1, -1, -1, -1]

def dial_handler(event):
    pos = event[2] / 127 
    pos = pos if event[1] <= 4 else (pos * (1 / 127)) - (1 / 127 / 2)
    print(f"Dial {event[1]} at position {round(pos, 10)}")
    dialdata[event[1]] = pos

def send_data():
    global stime
    global last_fill
    global position
    global modes
    ptime = int(round(time.time() * 1000)) - stime
    if (cm and ptime > 10):
        fill = [-1, -1, -1, -1]
        for i in range(1, 4 + 1):
            fdata = dialdata.get(i, -1)
            if (fdata == -1):
                continue
            total = fdata + dialdata.get(i + 4, 0.)
            total = total if total <= 1 else 1
            total = total if total >= 0 else 0
            fill[i - 1] = total
        if (fill == last_fill):
            return
        last_fill = fill
        bridge.send_command(cm, "set", [modes[position], *fill])
        stime = int(round(time.time() * 1000))

def button_handler(event):
    state = "released"
    if (event[2] == 127):
        state = "pressed"
    if (event[1] in named_buttons.keys()):
        name = named_buttons[event[1]]
        print(f"{name} {state}")
        global position
        global modes
        if (name == "LEFT" and state == "released"):
            position = position - 1 if position - 1 >= 0 else len(modes) - 1
            print(f"Mode set to: {modes[position]}")
        elif (name == "RIGHT" and state == "released"):
            position = position + 1 if position + 1 < len(modes) else 0
            print(f"Mode set to: {modes[position]}")
    else:
        print(f"Button {event[1]} {state}")

def readInput(input_device):
    while True:
        if input_device.poll():
            event = input_device.read(1)[0][0]
            if (event[0] != 176): 
                if (debug or event[0] not in [144,]):
                    print (event)
                continue
            if (event[1] in dials):
                dial_handler(event)
            elif (event[1] in buttons):
                button_handler(event)
            else:
                print (f"ID: {event[1]}, State: {round(event[2]/127,2)}")
        send_data()

def print_devices():
    devices = []
    for n in range(pygame.midi.get_count()):
        info = pygame.midi.get_device_info(n)
        if (info[2]):
            print (n,info[1])
            devices.append(n)
    return devices

def select_device(devices):
    while True:
        device_id = input("ID: ")
        try:
            device_id = int(device_id)
        except ValueError:
            continue
        if (device_id in devices):
            return device_id

def main():
    pygame.midi.init()
    devices = print_devices()
    device_id = select_device(devices)
    print(f"Opening device {device_id}:")
    my_input = pygame.midi.Input(device_id)
    try:
        readInput(my_input)
    except KeyboardInterrupt:
        my_input.close()
        print("Returning to device selection!")
        main()

if __name__ == '__main__':
    bc = bridge.open_listener()
    ip = bridge.await_controller(bc)
    cm = bridge.open_sender(ip)
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting!")
        sys.exit()
