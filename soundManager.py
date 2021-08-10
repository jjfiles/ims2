import pyfmodex
from pyfmodex.flags import MODE

import os
import time

# TODO
# - connect to main
# - add more control methods
# - decide how to organize sounds
# - comments and docstrings


# create instance -> 
# assign() -> 
# start() -> 
# (in while loop instance.system.update() ->
# time.sleep(0.1)) ->
# release()
class soundManager:
    def __init__(self):
        # fmod setup
        self.system = pyfmodex.system()
        self.sounds = []
        self.groups = []
        self.master = self.system.master_channel_group
        self.volume = 0.5
        self.playing = False
        
        # path setup
        base = os.getcwd()
        self.path = os.path.join(base, "Instrument Tracks")
        os.chdir(self.path)
        
    def assign(self):
        # assign sounds
        for entry in os.listdir(self.path):
            file = os.path.join(self.path, entry)
            self.sounds.append(
                self.system.create_sound(
                    os.path.join(self.path, entry),
                    mode=MODE.LOOP_NORMAL
                )
            )
        
        # assign base groups and master 
        for i in range(4):
            self.groups.append(self.system.create_channel_group(f"Group {i}"))
            self.master.add_group(self.groups[i], propagate_dsp_clock=False)
    
    def start(self):
        for idx, sound in enumerate(self.sounds):
            self.system.play_sound(
                sound,
                channel_group=self.groups[0] if idx <3
                    else self.groups[1] if (idx > 3 and idx < 7)
                    else self.groups[2] if (idx > 7 and idx < 11)
                    else self.groups[3]
            )

        for i in range(4):
            self.groups[i].volume = self.volume
            
        self.playing = True
            
    def fadeout(self, group):
        if not group.mute:
            fadeout_sec = 3
            volume = group.volume
        
            for _ in range(10 * fadeout_sec):
                group.volume = volume
                volume -= 1 / (10 * fadeout_sec)
                
                self.system.update()
                time.sleep(0.1)
            
            group.mute = not group.mute
            
    def fadein(self, group):
        if group.mute:
            group.mute = not group.mute

            fadein_sec = 3
            volume = group.volume
            
            while group.volume < self.volume:
                group.volume = volume
                volume += 1 / (10 * fadein_sec)
                
                self.system.update()
                time.sleep(0.1)
            
        
    def release(self):
        for sound in self.sounds:
            sound.release()
        
        for group in self.groups:
            group.release()
            
        self.master.release()
        self.system.release()
    
    def stop(self):
        for group in self.groups:
            if not group.mute:
                self.fadeout(group) 
        
        self.release()