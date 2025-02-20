"""
USB Rubber ducky clone using a regular RPI Pico, with an HC-05 bluetooth module connected to SERIAL_1 on GPIO
HC-05 is powered by the VBUS pin for stable USB 5v.

Credits to Circuitpython for providing adafruit library bundle and python SDK

Credits to treguly on github for providing a repository to help me build this project, https://github.com/treguly/pico-hid

Syntax:
Commands must be seperated with ;
Payload must always end with ; to confirm it's integrity

Commands:
Key commands, prefixed with !, combine multiple keys with + operator, example:  !lcontrol+lalt+del;
Special commands, prefixed with !!, usually have an argument, which is seperated by a whitespace, example: !!delay 200; example: !!hex 0x15;
Generic text, No prefix needed, just type away, example:  i hackz into yur compoter;

Example Payload: Rick roll:

!lgui+r;https://www.youtube.com/watch?v=E4WlUXrJgy4;!enter;


KEYS:

lcontrol : Left Control
lshift : Left Shift
lalt : Left Alt
lgui : Left GUI (Windows Key)
rcontrol : Right Control
rshift : Right Shift
ralt : Right Alt
rgui : Right GUI
enter : Enter
esc : Escape
backspace : Backspace
tab : Tab
space : Space
prtscr : Print Screen
pause : Pause
insert : Insert
home : Home
pageup : Page Up
del : Delete
end : End
pagedown : Page Down
rightarrow : Right Arrow
leftarrow : Left Arrow
downarrow : Down Arrow
uparrow : Up Arrow

F1 : Function Key 1
F2 : Function Key 2
F3 : Function Key 3
F4 : Function Key 4
F5 : Function Key 5
F6 : Function Key 6
F7 : Function Key 7
F8 : Function Key 8
F9 : Function Key 9
F10 : Function Key 10
F11 : Function Key 11
F12 : Function Key 12
F13 : Function Key 13
F14 : Function Key 14
F15 : Function Key 15
F16 : Function Key 16
F17 : Function Key 17
F18 : Function Key 18
F19 : Function Key 19
F20 : Function Key 20
F21 : Function Key 21
F22 : Function Key 22
F23 : Function Key 23
F24 : Function Key 24

SPECIAL COMMANDS:

delay, Waits for milliseconds, usage: !!delay 200;
hex,  Types a custom hex key, usage: !!hex 0x15;

... more coming soon.
"""
import usb_hid
import time
import usb_hid_map as usb

from adafruit_hid.keyboard import Keyboard

import board
import busio
import supervisor
import digitalio

kbd = Keyboard(usb_hid.devices)
uart = busio.UART(board.GP0, board.GP1, baudrate=9600, timeout=0)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def delay(delay_ms : int):
    time.sleep(delay_ms / 1000)

def send(this_input, sleep=0.25):
    for item in this_input:
        if type(item) is list:
            kbd.send(*item)
        else:
            kbd.send(item)
    time.sleep(sleep)
    
def process_commands(buf : str):
    if len(buf) < 1: return
    elif buf[-1] != ";": return
    
    commands = buf.split(";")
    commands = [cmd for cmd in commands if cmd != ""]
    payload = []
    
    for command in commands:
        # key commands
        if command.startswith("!") and not command.startswith("!!"):
            if "+" in command:
                strokes = []
                
                # multiple strokes
                for stroke in command[1:].split("+"):
                    s = stroke
                    if len(stroke) > 1:
                        s = stroke.upper()

                    k = command_keys.get(s, None)
                    
                    if type(k) == list:
                        strokes += k
                    elif type(k) == int:
                        strokes.append(int(k))
                    else: uart.write(f"INVALID STROKE: {stroke}\n")
            
                payload.append(strokes)
            # single stroke
            else:
                stroke = command[1:]
                if len(stroke) > 1:
                    stroke = stroke.upper()
                
                k = command_keys.get(stroke, None)
                
                if type(k) == list:
                    payload += k
                elif type(k) == int:
                    payload.append(k)
                else: uart.write(f"INVALID STROKE: {stroke}\n")
        # special commands
        elif command.startswith("!!"):
            args = command[2:].split(" ")
            # Delay command
            if args[0] == "delay" and len(args) == 2:
                ms = None
                try:
                    ms = int(args[1])
                    delay(ms)
                except:
                    uart.write("INVALID DELAY\n")
            # Hex command
            elif args[0] == "hex" and len(args) == 2:
                hex_string = args[1]
                if hex_string.lower().startswith("0x"):
                    try:
                        val = int(hex_string, 16)
                        payload.append(val)
                    except:
                        uart.write("INVALID HEX\n")
            else:
                uart.write(f"INVALID COMMAND: {args[0]}\n")
        # custom text
        else:
            payload += usb.get_sequence(command)
    
    send(payload)


# preprocessing
special_keys_upper = {k.upper(): v for k, v in usb.special.items()}
command_keys =  usb.fkeys | special_keys_upper | usb.keys

buffer : str = ""

print("Pico ducky initiated. MADE WITH CIRCUITPYTHON.")
while True:
    data = uart.read(32)  # read up to 32 bytes

    if data:
        decoded = data.decode()
        if decoded == "\n":
            led.value = True
            
            buffer = buffer.strip().split("\n")[0]
            
            process_commands(buffer)
            
            print(f"RECIEVED: {buffer}")
            uart.write("OK\n")
            
            led.value = False
            buffer = ""
        else: buffer += decoded
            
        
        
        
