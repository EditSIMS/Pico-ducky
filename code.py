"""
USB Rubber ducky clone using a regular RPI Pico, with an HC-05 bluetooth module connected to SERIAL_1 on GPIO
HC-05 is powered by the VBUS pin for stable USB 5v.

Credits to Circuitpython for providing adafruit library bundle and python SDK
Credits to treguly on github for providing a repository to help me build this project, https://github.com/treguly/pico-hid

Github repo: https://github.com/EditSIMS/Pico-ducky/tree/main
"""

from package import *

print("Pico ducky initiated. MADE WITH CIRCUITPYTHON. REPO: https://github.com/EditSIMS/Pico-ducky/tree/main")

# open payload.json
payload_filename = "payload.json"
placeholder = {
    "payload" : []
}

def get_payload_size(obj):
    global payload_size
    payload_size = 0
    for item in obj:
        if type(item) is int:
            payload_size += 28
        elif type(item) is str:
            payload_size += 49 + len(item)
        elif type(item) is list:
            get_payload_size(item)

payload_corrupted = False
payload_size = 0

if payload_filename in os.listdir():
    try:
        with open(payload_filename, "r") as f:
            data = json.load(f)
        
        valid = compare_dicts(data, placeholder)
        
        if not valid:
            raise ValueError
        elif valid and len(data["payload"]) > 0:
            get_payload_size(data["payload"])
            print(f"PAYLOAD SIZE: {payload_size} bytes\nRUNNING PAYLOAD NOW")
            led.value = True
            time.sleep(0.3)
            send(data["payload"])
            led.value = False
            print("FINISHED RUNNING PAYLOAD")

    except (ValueError, OSError):
        payload_corrupted = True
        with open(payload_filename, "w") as f:
            json.dump(placeholder, f)
else:
    payload_corrupted = True
    with open(payload_filename, "w") as f:
        json.dump(placeholder, f)

buffer : str = ""



if payload_corrupted:
    print(f"{payload_filename} not found or corrupted, PAYLOAD HAS BEEN RESET AND WILL NOT RUN")
    
while True:
    data = uart.read(32)  # read up to 32 bytes

    if data:
        try:
            decoded = data.decode()
        except:
            print(f"DECODED BAD BYTE: {data}")
            
        if decoded == "\n":
            led.value = True
            
            buffer = buffer.strip().split("\n")[0]
            
            print(f"RECIEVED: {buffer}")
            if buffer.startswith("SET_PAYLOAD"):
                uart.write("OK\n")
                commands = buffer[len("SET_PAYLOAD") + 1:]
                payload, errors = process_commands(commands)
                
                if len(errors) > 0:
                    uart.write(", ".join(errors))
                else:
                    get_payload_size(payload)
                    data = {
                        "payload" : payload
                    }
                    
                    with open(payload_filename, "w") as f:
                        json.dump(data, f)
                
                    uart.write(f"PAYLOAD SIZE: {payload_size} bytes\nPAYLOAD SUCCESSFULLY SET\n")
            
            elif buffer == "RESET_PAYLOAD":
                uart.write("OK\n")
                with open(payload_filename, "w") as f:
                    json.dump(placeholder, f)
                
                uart.write("PAYLOAD DELETED SUCCESSFULLY\n")
            elif buffer == "RESET":
                uart.write("OK\n")
                microcontroller.reset()
            elif buffer[-1] == ";":
                uart.write("OK\n")
                payload, errors = process_commands(buffer)
                
                
                
                if len(errors) > 0:
                    uart.write(", ".join(errors))
                else:
                    get_payload_size(payload)
                    uart.write(f"PAYLOAD SIZE: {payload_size} bytes\n")
                    
                    send(payload)
                    
                    uart.write("DONE\n")
            else:
                uart.write("INVALID COMMAND/PAYLOAD\n")
            
            led.value = False
            buffer = ""
        else:
            buffer += decoded
