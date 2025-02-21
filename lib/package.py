import time
import usb_hid
import usb_hid_map as usb
from adafruit_hid.keyboard import Keyboard
import board
import busio
import supervisor
import digitalio
import os
import json
import storage
import microcontroller

special_keys_upper = {k.upper(): v for k, v in usb.special.items()}
command_keys =  usb.fkeys | special_keys_upper | usb.keys

kbd = Keyboard(usb_hid.devices)
uart = busio.UART(board.GP0, board.GP1, baudrate=9600, timeout=0)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def send(this_input, sleep=0.05):
    for item in this_input:
        if type(item) is str:
            print(item)
            args = item.split(" ")
            if args[0] == "delay":
                time.sleep(float(args[1]))
        elif type(item) is list:
            kbd.send(*item)
        else:
            kbd.send(item)
    time.sleep(sleep)

def compare_dicts(dict1, dict2):
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    for key in dict1:
        if type(dict1[key]) is not type(dict2[key]):
            return False

    return True

def process_commands(buf : str):
    if len(buf) < 1: return [], ["Buffer too short!\n"]
    elif buf[-1] != ";": return [], ["Bad message\n"]
    
    commands = buf.split(";")
    commands = [cmd for cmd in commands if cmd != ""]
    payload = []
    
    errors = []
    
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
                    else: errors.append(f"INVALID STROKE: {stroke}")
            
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
                else: errors.append(f"INVALID STROKE: {stroke}")
        # special commands
        elif command.startswith("!!"):
            args = command[2:].split(" ")
            # Delay command
            if args[0] == "delay" and len(args) == 2:
                payload = []
                
                ms = None
                try:
                    ms = int(args[1])  
                    payload.append(f"delay {ms / 1000}")
                    
                except:
                    errors.append("INVALID DELAY")
            # Hex command
            elif args[0] == "hex" and len(args) == 2:
                hex_string = args[1]
                if hex_string.lower().startswith("0x"):
                    try:
                        val = int(hex_string, 16)
                        payload.append(val)
                    except:
                        errors.append(f"INVALID HEX: {args[1]}")
            else:
                errors.append(f"INVALID COMMAND: {args[0]}")
        # custom text
        else:
            payload += usb.get_sequence(command)
    
    return payload, errors