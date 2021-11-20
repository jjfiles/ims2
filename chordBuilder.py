import pyfmodex
from pyfmodex.flags import MODE

import os
import time

from chordDict import chords


class chordBuilder:
    def __init__(self):
        
        self.system = pyfmodex.System()
        self.system.init(maxchannels=32)
        self.groups = [] # do i need thi?
        self.master = self.system.master_channel_group
        self.volume = 0.5
        self.playing = False
        
        self.base = os.getcwd()
        self.chordPath = os.path.join(self.base, "Chords")
        self.notesPath = os.path.join(self.base, "Notes")
        
        self.selectedChord = None
        self.notes = None
        
        