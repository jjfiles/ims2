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
os.chdir("B:\Code\ims2\Instrument Tracks")
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
group0 = system.create_channel_group("Group 0")
group1 = system.create_channel_group("Group 1")
group2 = system.create_channel_group("Group 2")
group3 = system.create_channel_group("Group 3")

#master group
groupMaster = system.master_channel_group
groupMaster.add_group(group0, propagate_dsp_clock=False)
groupMaster.add_group(group1, propagate_dsp_clock=False)
groupMaster.add_group(group2, propagate_dsp_clock=False)
groupMaster.add_group(group3, propagate_dsp_clock=False)

#start the sounds together
for idx, sound in enumerate(sounds):
    system.play_sound(
        sound, 
        channel_group=group0 if idx < 3 
            else group1 if (idx > 3 and idx < 7) 
            else group2 if (idx > 7 and idx < 11) 
            else group3
    )
print(groupMaster)

#set starting volume
group0.volume = 0.5
group1.volume = 0.5
group2.volume = 0.5
group3.volume = 0.5

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
            group0.mute = not group0.mute
        elif keypress == "1":
            group1.mute = not group1.mute
        elif keypress == "2":
            group2.mute = not group2.mute
        elif keypress == "3":
            group3.mute = not group3.mute
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
if not (groupMaster.mute or group0.mute or group1.mute or group2.mute or group3.mute):
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
    
group0.release()
group1.release()
group2.release()
group3.release()
groupMaster.release()

system.release()