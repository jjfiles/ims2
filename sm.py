#testing fmod integration with already constructed wrapper https://github.com/tyrylu/pyfmodex
#Something is wrong with the path to the FMOD Engine installation, cannot test until that is fiexed...
import pyfmodex

system.pyfmodex.System()
system.init()
sound = system.create_sound("Instrument Tracks/Cello.wav")
channel = sound.play()

while channel.is_playing():
    pass