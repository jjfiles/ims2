import pyfmodex
from pyfmodex.flags import MODE

import os
import time

# TODO
# - plan how to group sounds (indv?)

# create instance -> 
# assign() -> 
# start() -> 
# (in while loop instance.system.update() ->
# time.sleep(0.1)) ->
# release()
class SoundManager:
    def __init__(self):
        """initialize fmod settings and local variables
        """        
        
        # fmod setup
        self.system = pyfmodex.System()
        self.system.init(maxchannels=16)
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
        """create all channels, groups, and sounds
        """        
        
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
        """start playing all sounds and set volumes
        """
        
        # ittr through all sounds and start playing
        for idx, sound in enumerate(self.sounds):
            self.system.play_sound(
                sound,
                channel_group=self.groups[0] if idx <3
                    else self.groups[1] if (idx > 3 and idx < 7)
                    else self.groups[2] if (idx > 7 and idx < 11)
                    else self.groups[3]
            )

        # set volume for each group
        for i in range(4):
            self.groups[i].volume = self.volume
        
        # set playing flag
        self.playing = True
            
    def groupFadeout(self, group):
        """fadeout a currently playing group

        Args:
            group (system.channel_group): a group of sounds
        """        
        
        # if the group is not muted fade volume out over time
        if not group.mute:
            group.mute = not group.mute
            
            fadeout_sec = 1
            volume = group.volume
        
            for _ in range(10 * fadeout_sec):
                group.volume = volume
                volume -= 1 / (10 * fadeout_sec)
                
                self.system.update()
                time.sleep(0.01)
             
    def groupFadein(self, group):
        """fadin a currently muted group

        Args:
            group (sstem.channel_group): a group of sounds
        """        
        
        # if a group is muted fade the volume in over time
        if group.mute:
            group.mute = not group.mute

            fadein_sec = 1
            volume = group.volume
            
            while group.volume < self.volume:
                group.volume = volume
                volume += 1 / (10 * fadein_sec)
                
                self.system.update()
                time.sleep(0.01)
        
    def rel(self):
        """release and destroy all sounds and groups
        """        

        # release sounds
        for sound in self.sounds:
            sound.release()
        
        # release groups
        for group in self.groups:
            group.release()
            
        # release master and system
        self.master.release()
        self.system.release()
    
    def stop(self):
        """fadeout all groups then release
        """    
    
        # mute each group to "stop" playback
        if not self.master.mute:
            self.groupFadeout(self.master)
        
        # release all sounds to terminate session
        self.rel()
        
        self.playing = False

    def incVol(self):
        """increment all volumes by 0.1
        """
        if self.volume <= 1:
            # set new volume
            self.volume += 0.1
            
            # apply new volume to groups
            for i in range(4):
                self.groups[i].volume = self.volume
            
    def decVol(self):
        """decrement all volmes by 0.1
        """        
        
        if self.volume >= 0:
            # set new volume
            self.volume -= 0.1
            
            # apply new volume to groups
            for i in range(4):
                self.groups[i].volume = self.volume

    def toggleMasterMute(self):
        self.master.mute = not self.master.mute