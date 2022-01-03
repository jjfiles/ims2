import pyfmodex
from pyfmodex.flags import MODE

import os
import time

from chordDict import chords


class chordBuilder:
    def __init__(self):
        
        self.system = pyfmodex.System()
        self.system.init(maxchannels=32)
        self.master = self.system.master_channel_group
        self.mainChord = None
        self.volume = 0.5
        self.playing = False
        
        self.base = os.getcwd()
        self.chordPath = os.path.join(self.base, "Chords")
        self.notesPath = os.path.join(self.base, "Notes")
        self.chordDict = chords
        
        self.chordFiles = [f for f in os.listdir(self.chordPath) if os.path.isfile(os.path.join(self.chordPath, f))]
        self.chordFiles.pop(0)
        self.selectedChord = None
        self.notes = []
    
    def assign(self):

        # set master chord
        os.chdir(self.chordPath)
        self.master = self.system.create_sound(self.chords[self.selectedChord])
        
        os.chdir(self.notesPath)
        c = self.chordFiles[self.selectedChord].split("")[2]
        self.mainChord = chords[c]
        
        for row in self.mainChord:   
            for note in row:
                self.notes.append(self.system.ceate_sound(note + ".mp3"))
        
        
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def incVol(self):
        pass
    
    def decVol(self):
        pass
    
    def toggleMute(self):
        pass

    
