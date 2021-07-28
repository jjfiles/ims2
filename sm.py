#testing fmod integration with already constructed wrapper https://github.com/tyrylu/pyfmodex

#Fixed aforementioned fmod wrapper. pyfmodex.py change line 6 to 
# _dll = WinDLL(r'C:\Program Files (x86)\FMOD SoundSystem\FMOD Studio API Windows\api\core\lib\x64\fmod.dll')
import pyfmodex
from pyfmodex.flags import MODE

import os

system = pyfmodex.System()
system.init(maxchannels=16)
sounds = []

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
    
group0 = system.create_channel_group("Group 0")
group1 = system.create_channel_group("Group 1")
group2 = system.create_channel_group("Group 2")
group3 = system.create_channel_group("Group 3")

groupMaster = system.master_channel_group
# groupMaster.add_group(group0)
# groupMaster.add_group(group1)
# groupMaster.add_group(group2)
# groupMaster.add_group(group3)

for idx, sound in enumerate(sounds):
    system.play_sound(sound, channel_group=group0 if idx < 3 else group1 if (idx > 3 and idx < 7) else group2 if (idx > 7 and idx < 11) else group3)

group0.volume = 0.5
group1.volume = 0.5
group2.volume = 0.5
group3.volume = 0.5

while group0.is_playing:
    pass