USB Rubber ducky clone using a regular RPI Pico, with an HC-05 bluetooth module.

Credits to Circuitpython for providing adafruit library bundle and python SDK, and credits to treguly on github for providing a repository to help me build this project, https://github.com/treguly/pico-hid

# How to use: Setup and wiring
1. Install circuitpython by downloading it from https://circuitpython.org/board/raspberry_pi_pico/
2. Drag and drop the file into your pico's main drive, then wait for it to reboot.
3. Use an IDE such as thonny and make sure you have experience with circuitpython or python in general
4. Connect an HC-05 module or any other blueooth module to the pi, MAKE SURE +Voltage is connected to VBUS for reliable 5v power.
   
![image](https://github.com/user-attachments/assets/633e929d-8b5c-4a35-a41f-546431ce3f35)

![4bun501eqka91-3320441646](https://github.com/user-attachments/assets/9e135ee2-758a-4070-ae13-0753a2d786f6)


5. Paste the code.py into the pico's main directory
6. Paste the lib folder into there as well.

7. Pair your bluetooth module with any bluetooth serial app you prefer. (i reccomend "Serial Bluetooth Terminal" on play store)
8. Follow the syntax and drop payloads!

# How to use: Commands


2 Types of commands: 
- Payloads
- System requests

Payload Syntax:
Commands must be seperated with ;
Payload must always end with ; to confirm it's integrity

Payload Commands:
- Key commands, prefixed with !, combine multiple keys with + operator, example:  !lcontrol+lalt+del;
- Special commands, prefixed with !!, usually have an argument, which is seperated by a whitespace, example: !!delay 200; example: !!hex 0x15;
- Generic text, No prefix needed, just type away, example:  i hackz into yur compoter;

Example Payload: Rick roll

- !lgui+r;https://www.youtube.com/watch?v=E4WlUXrJgy4;!enter;



System requests:

- SET_PAYLOAD [INSERT YOUR PAYLOAD HERE]

This command lets you modify the BOOT payload, paste a regular payload while minding a SPACE after the initial command.
Boot payloads are stored on the main drive as a JSON file, they will run within 300ms of boot time.

- RESET_PAYLOAD

This command resets your boot payload so it does not run
Does not require any arguments.

- PING

Use this to test the bluetooth signal and to make sure the Pi is running without issues.



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
