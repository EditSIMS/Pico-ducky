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
            args = item.split(" ")
            if args[0] == "delay":
                time.sleep(int(args[1]) / 1000)
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

def get_key(key : str):
    
    payload = []
    errors = []

    if "+" in key:
        strokes = []
                
        # multiple strokes
        for stroke in key[1:].split("+"):
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
        stroke = key[1:]
        if len(stroke) > 1:
            stroke = stroke.upper()
                
        k = command_keys.get(stroke, None)
                
        if type(k) == list:
            payload += k
        elif type(k) == int:
            payload.append(k)
        else: errors.append(f"INVALID STROKE: {stroke}")
    
    return payload, errors

def process_commands(buf : str):
    if len(buf) < 1: return [], ["Buffer too short!\n"]
    elif buf[-1] != ";": return [], ["Bad message\n"]
    
    commands = buf.split(";")
    commands = [cmd.strip() for cmd in commands if cmd != ""]
    payload = []
    
    errors = []
    
    for command in commands:
        # key commands
        
        
        if command.startswith("!") and not command.startswith("!!"):
            k_payload, k_errors = get_key(command)
        
            payload += k_payload
            
            errors += k_errors
        elif command.startswith("!!"):
            args = command[2:].split(" ")
            # Delay command
            if args[0] == "delay" and len(args) == 2:
                payload = []
                
                ms = None
                try:
                    ms = int(args[1])  
                    payload.append(f"delay {ms}")
                    
                except:
                    errors.append("INVALID DELAY")
            # Hex command
            elif args[0] == "hex" and len(args) == 2:
                hex_string = args[1]
                if hex_string.lower().startswith("0x"):
                    try:
                        val = int(hex_string, 16)
                        payload.append(val)
                    except ValueError:
                        errors.append(f"INVALID HEX: {args[1]}")
            elif args[0] == "repeat" and len(args) == 4:
                delay = None
                repetitions = None
                try:
                    repetitions = int(args[1])
                except ValueError:
                    errors.append(f"INVALID REPETITIONS: {arg[1]}")
                    
                try:
                    delay = int(args[2])
                except ValueError:
                    errors.append(f"INVALID DELAY: {arg[2]}")
                
                if delay and repetitions:
                    rep_commands = args[3]
                    
                    rep_commands = rep_commands.split(";")
                    rep_commands = [cmd.strip() for cmd in rep_commands if cmd != ""]
                    
                    rep_payload = []
                    
                    for r_command in rep_commands:
                        if r_command.startswith("!") and not r_command.startswith("!!"):
                            k_payload, k_errors = get_key(r_command)
                            
                            rep_payload += k_payload
                            rep_payload.append(f"delay {delay}")
                            errors += k_errors
                        else:
                            rep_payload += usb.get_sequence(r_command)
                            rep_payload.append(f"delay {delay}")
                                
                    payload += (rep_payload * repetitions)[:-1]
            else:
                errors.append(f"MISSING ARGUMENT FOR {arg[0]}")
        # custom text
        else:
            payload += usb.get_sequence(command)
    
    return payload, errors
