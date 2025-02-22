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
payload_corrupted = False

if payload_filename in os.listdir():
    try:
        with open(payload_filename, "r") as f:
            data = json.load(f)
        
        valid = compare_dicts(data, placeholder)
        
        if not valid:
            raise ValueError
        elif valid and len(data["payload"]) > 0:
            print("RUNNING PAYLOAD NOW")
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
            
            valid = True
            
            print(f"RECIEVED: {buffer}")
            if buffer.startswith("SET_PAYLOAD"):
                commands = buffer[len("SET_PAYLOAD") + 1:]
                payload, errors = process_commands(commands)
                
                if len(errors) > 0:
                    uart.write(", ".join(errors))
                else:
                    data = {
                        "payload" : payload
                    }
                    
                    with open(payload_filename, "w") as f:
                        json.dump(data, f)
                
                    uart.write("PAYLOAD SUCCESSFULLY SET\n")
            
            elif buffer == "RESET_PAYLOAD":        
                with open(payload_filename, "w") as f:
                    json.dump(placeholder, f)
                
                uart.write("PAYLOAD DELETED SUCCESSFULLY\n")
            elif buffer == "RESET":
                microcontroller.reset()
            elif buffer[-1] == ";":
                payload, errors = process_commands(buffer)
                
                if len(errors) > 0:
                    uart.write(", ".join(errors))
                else:
                    send(payload)
                    uart.write("DONE\n")
            else:
                valid = False
                uart.write("INVALID COMMAND/PAYLOAD\n")
                
            if valid:
                uart.write("OK\n")
            
            led.value = False
            buffer = ""
        else:
            buffer += decoded
