from soundManager import SoundManager
from visionManager import VisionManager
from timer import Timer

import cv2

# TODO
# - Show fmod logo so i dont get sued
# - change sound folder on command
# - then restart sound system?

# global list to manipulate quadrant cooldown timers
t = []

def initCooldowns(quads: int):
    """initialize a list of cooldowns based off the number of quadrants

    Args:
        quads (int): number of timers to intialize
    Returns:
        list: list of timer objects
    """   

    global t
    t = []
   
    # for each quadrant set a new timer 
    for i in range(quads):
        i = Timer()
        i.start()
        t.append(i)

    return t

def onCooldown(t: Timer):
    """checks if a sound group should be allowed to transition its on/off state

    Args:
        t (Timer): timer object for a specific sound group 

    Returns:
        bool: returns True if the group can transtition
    """
    
    # if a groups cooldown period is over restart it's timer
    if t.check():
        t.start()
        return True
    
    # otherwise do nothing
    else:    
        return False

def parseCommands(v: VisionManager, s: SoundManager, cap, k: int):
    """parse non-exit keyboard commands

    Args:
        v (VisionManager): instance of vision management system
        s (SoundManager): instance of sound management system
        cap (cv2 video frame): frame from cv2 video capture
        k (int): keycode sent this loop
    """
    global t
    
    ## --- VISION ---
    # debug commands
    if k == ord('d'):
        v.toggleDebug()
    elif k == ord('i'):
        v.toggleInfo()
    elif k == ord('o'):
        v.toggleOverlay()
    elif k == ord('p'):
        v.togglePercentage()
    
    # reset base image command
    elif k == ord('r'):
        v.base = v.imgManip(cap)
    
    # change number of quadrants
    elif k == ord('1'):
        # update number of quadrants in VisionManager
        v.updateNumQuads(2)
        # retile the base image based on the new number of quadrants
        v.base4d = v.tilify(v.base)
        # stop the SoundManger
        s.stop()
        # restart SoundManager
        SoundManager.__init__(s)
        # assign new sounds
        s.assign(v.NUM_QUADS)
        # initialize new cooldowns
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('2'):
        v.updateNumQuads(4)
        v.base4d = v.tilify(v.base) 
        s.stop()
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('3'): 
        v.updateNumQuads(8)
        v.base4d = v.tilify(v.base) 
        s.stop()
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('4'): 
        v.updateNumQuads(16)
        v.base4d = v.tilify(v.base) 
        s.stop()
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        t = initCooldowns(v.NUM_QUADS)

    ## --- SOUND ---
    # volume controls
    elif k == ord('='):
        s.incVol()
    elif k == ord('-'):
        s.decVol()
    elif k ==ord('m'):
        s.toggleMasterMute()

    # playback controls
    elif k == ord(" "):
        if not s.playing:
            s.start(v.NUM_QUADS)

def sync(v: VisionManager, s: SoundManager, t: list):
    """syncs the vision, sound, and timer systems

    Args:
        v (VisionManager): instance of the vision system
        s (SoundManager): instance of the sound system
        t (list): list of timer objects
    """    
    
    # for each quadrant
    for idx in range(len(v.comp)):
        # check if the sound system should cange on/off state
        if v.comp[idx]:
            # check if that quadrant is off cooldown
            if onCooldown(t[idx]):
                # turn volume on
                s.groupFadein(s.groups[idx])
        else:
            # check if that quardant is off cooldown
            if onCooldown(t[idx]):
                # turn volume off
                s.groupFadeout(s.groups[idx])

def main():
    """main controller for IMS2
    """
   
    # start video playback, get frame height and width
    cap = cv2.VideoCapture(0)
    w = int(cap.get(3))
    h = int(cap.get(4))
    
    # show fmod logo so no one sues me
    # i = cv2.imread("Images/FMOD.png", 2)
    # cv2.imshow("Powered by FMOD", i)
    
    # Initialize vision manager
    v = VisionManager(h, w)
    v.base = v.imgManip(cap)
    v.base4d = v.tilify(v.base)
    
    # Initialize sound manager
    s = SoundManager()
    s.assign(v.NUM_QUADS)
    
    # Initialize cooldown timers
    global t 
    t = initCooldowns(v.NUM_QUADS)

    # main loop
    while True:
        
        # grab each new frame and pass it through edge detection
        v.curr = v.imgManip(cap)
        # reorganize the image into tiles
        v.curr4d = v.tilify(v.curr)
        # compare differences in the original image and the current frame
        v.comp = v.detect(v.base4d, v.curr4d)
        # draw rectangles on the current frame
        v.final = v.drawRect(v.curr, v.comp)
        
        # show image to screen
        cv2.imshow('IMS2', v.final)
                
        # update activley audible sounds
        sync(v, s, t)

        # wait for keyboard commands
        k = cv2.waitKey(1)
        
        if k == 13:
            break
        else:
            parseCommands(v, s, cap, k)
    
        # update sound system
        s.system.update()
    
    # stopping video feed and sound playback. freeing resources
    s.stop()
    cap.release()
    cv2.destroyAllWindows()
    t.clear()
    del t[:]
        
if __name__ == '__main__':
    main()