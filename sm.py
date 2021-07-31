#testing fmod integration with already constructed wrapper https://github.com/tyrylu/pyfmodex

#Fixed aforementioned fmod wrapper. pyfmodex.py change line 6 to 
# _dll = WinDLL(r'C:\Program Files (x86)\FMOD SoundSystem\FMOD Studio API Windows\api\core\lib\x64\fmod.dll')

import pyfmodex
from pyfmodex.flags import MODE

import os
import time
import curses

#pyfmodex setup
system = pyfmodex.System()
system.init(maxchannels=16)
sounds = []

#create sounds for each track
# os.chdir("B:\Code\ims2\Instrument Tracks")
os.chdir("C:\\Users\\Jeffery\\projects\\ims2\\Instrument Tracks")
basepath = os.getcwd()

for entry in os.listdir(basepath):
    file = os.path.join(basepath, entry)
    sounds.append(
        system.create_sound(
            os.path.join(basepath, entry)
            , mode=MODE.LOOP_NORMAL
        )
    )

#create groups    
groups = []
for i in range(4):
    groups.append(system.create_channel_group(f"Group {i}"))

#master group
groupMaster = system.master_channel_group
for i in range(4):
    groupMaster.add_group(groups[i], propagate_dsp_clock=False)

#start the sounds together
for idx, sound in enumerate(sounds):
    system.play_sound(
        sound, 
        channel_group=groups[0] if idx < 3 
            else groups[1] if (idx > 3 and idx < 7) 
            else groups[2] if (idx > 7 and idx < 11) 
            else groups[3]
    )

#set starting volume
for i in range(4):
    groups[i].volume = 0.5

#initialize curses
stdscr = curses.initscr()
stdscr.clear()
stdscr.nodelay(True)

#command menu
stdscr.addstr(
    "=======================\n"
    "Channel Groups Example.\n"
    "=======================\n"
    "\n"
    "Press 0 to mute/unmute group 0\n"
    "Press 1 to mute/unmute group 1\n"
    "Press 2 to mute/unmute group 2\n"
    "Press 3 to mute/unmute group 3\n"
    "Press m to mute/unmute master group\n"
    "Press q to quit"
)

#number of channels playing
stdscr.addstr(f"Channels playing: {system.channels_playing['channels']}\n")

#loop for input controls
while True:
    try:
        keypress = stdscr.getkey()
        if keypress == "0":
            groups[0].mute = not groups[0].mute
        elif keypress == "1":
            groups[1].mute = not groups[1].mute
        elif keypress == "2":
            groups[2].mute = not groups[2].mute
        elif keypress == "3":
            groups[3].mute = not groups[3].mute
        elif keypress == "m":
            groupMaster.mute = not groupMaster.mute
        elif keypress == "q":
            break
    except curses.error as cerr:
        if cerr.args[0] != "no input":
            raise cerr
    
    system.update()
    time.sleep(50/1000)

#fadeout on loop break
if not (groupMaster.mute or groups[0].mute or groups[1].mute or groups[2].mute or groups[3].mute):
    pitch = 1.0
    volume = 1.0
    
    fadeout_sec = 3
    for _ in range(10 * fadeout_sec):
        groupMaster.pitch = pitch
        groupMaster.volume = volume
        
        volume -= 1 / (10 * fadeout_sec)
        pitch -= 0.25 / (10 * fadeout_sec)
        
        system.update()
        time.sleep(.1)
        
#release objects because we aren't monsters
for sound in sounds:
    sound.release()
    
for group in groups:
    group.release()

groupMaster.release()

system.release()