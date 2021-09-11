from soundManager import SoundManager
from visionManager import VisionManager
from timer import Timer

import cv2

# TODO
# - Show fmod logo so i dont get sued
# - Test with blank background. Diff changer is in placec

def dontSueMe():
    img = cv2.imread('Images/FMOD.png', 1)
    cv2.imshow("Powered by FMOD", img)
    print("Starting shortly...")
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

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

def gaugeDiff(v: VisionManager, cap):
    """scale the difference setting based of of recent images

    Args:
        v (VisionManager): instance of the vision manager
        cap (cv2 video frame)): [description]

    Returns:
        float: average of the captured differences over 5 frames of data
    """        
    
    #set locals
    grp = 0
    diff = [None] * 5
    
    # for 5 frames grab the next frame, grab the comparison percentages and update the base image
    for i in range(5):
        v.curr = v.imgManip(cap)
        v.curr4d = v.tilify(v.curr)
        _, diff[i] = v.detect(v.base4d, v.curr4d)
        v.base = v.curr
        v.base4d = v.curr4d
        
    # for each set of percentages in each of the 5 frames, grab the total average
    for each in diff:
        idv = 0
        for e in each:
            idv += e
        idv /= len(each) 
        grp += idv
    grp /= len(diff)

    # debug output new diff
    if v.DEBUG:
        print(f"new diff: {(grp * 100):.2f}%")
    return grp

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
        if v.DEBUG:
            print("resetting base image...")
        v.base = v.imgManip(cap)
        v.base4d = v.tilify(v.base)
    
    # change number of quadrants
    elif k == ord('1'):
        # update number of quadrants in VisionManager
        v.updateNumQuads(2)
        if v.DEBUG:
            print("Set number of quadrants to 2")
        # retile the base image based on the new number of quadrants
        v.setDiff(gaugeDiff(v, cap))
        # stop the SoundManger
        s.stop()
        print("Stopping playback...")
        # restart SoundManager
        SoundManager.__init__(s)
        # assign new sounds
        s.assign(v.NUM_QUADS)
        print("Sound system restarted!")
        # initialize new cooldowns
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('2'):
        v.updateNumQuads(4)
        if v.DEBUG:
            print("Set number of quadrants to 4")
        v.setDiff(gaugeDiff(v, cap))
        s.stop()
        print("Stopping playback...")
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        print("Sound system restarted!")
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('3'): 
        v.updateNumQuads(8)
        if v.DEBUG:
            print("Set number of quadrants to 8")
        v.setDiff(gaugeDiff(v, cap))
        s.stop()
        print("Stopping playback...")
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        print("Sound system restarted!")
        t = initCooldowns(v.NUM_QUADS)
    elif k == ord('4'): 
        v.updateNumQuads(16)
        if v.DEBUG:
            print("Set number of quadrants to 16")
        v.setDiff(gaugeDiff(v, cap))
        s.stop()
        print("Stopping playback...")
        SoundManager.__init__(s)
        s.assign(v.NUM_QUADS)
        print("Sound system restarted!")
        t = initCooldowns(v.NUM_QUADS)

    ## --- SOUND ---
    # volume controls
    elif k == ord('='):
        s.incVol()
    elif k == ord('-'):
        s.decVol()
    elif k == ord('m'):
        s.toggleMasterMute()

    # playback controls
    elif k == ord(" "):
        print("Starting playback...")
        if not s.playing:
            s.start(v.NUM_QUADS)
        print("Please enjoy!")

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

    # please don't sue me
    dontSueMe()
   
    # start video playback, get frame height and width
    print("Camera loading....")
    cap = cv2.VideoCapture(0)
    w = int(cap.get(3))
    h = int(cap.get(4))
    print("Camera started!")
    
    # show fmod logo so no one sues me
    # i = cv2.imread("Images/FMOD.png", 2)
    # cv2.imshow("Powered by FMOD", i)
    
    # Initialize vision manager
    print("Vision system starting...")
    v = VisionManager(h, w)
    v.base = v.imgManip(cap)
    v.base4d = v.tilify(v.base)
    print("Vision system started!")
    
    # Initialize sound manager
    print("Sound system starting...")
    s = SoundManager()
    s.assign(v.NUM_QUADS)
    print("Sound system started!")
    
    # Initialize cooldown timers
    print("Intizalizing cooldown timers...")
    global t 
    t = initCooldowns(v.NUM_QUADS)
    print("Cooldowns initialized!")
    
    print("Calculating comparison percentages...")
    v.setDiff(gaugeDiff(v, cap))
    print("Comparison percentages set!")

    # main loop
    while True:
        
        # grab each new frame and pass it through edge detection
        v.curr = v.imgManip(cap)
        # reorganize the image into tiles
        v.curr4d = v.tilify(v.curr)
        # compare differences in the original image and the current frame
        v.comp, _ = v.detect(v.base4d, v.curr4d)
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
    print("All systems shutdown.")
    print("Thanks you!")
        
if __name__ == '__main__':
    main()