from soundManager import SoundManager
from visionManager import VisionManager

import cv2

# TODO
# - need some kind of delay system to prevent on off spamming


def parseCommands(v: VisionManager, s: SoundManager, cap, k: int):
    """parse non-exit keyboard commands

    Args:
        v (VisionManager): instance of vision management system
        s (SoundManager): instance of sound management system
        cap (cv2 video frame): frame from cv2 video capture
        k (int): keycode sent this loop
    """
    
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
        v.updateNumQuads(2)
        v.base4d = v.tilify(v.base) 
    elif k == ord('2'):
        v.updateNumQuads(4)
        v.base4d = v.tilify(v.base) 
    elif k == ord('3'): 
        v.updateNumQuads(8)
        v.base4d = v.tilify(v.base) 
    elif k == ord('4'): 
        v.updateNumQuads(16)
        v.base4d = v.tilify(v.base) 
    elif k == ord('5'): 
        v.updateNumQuads(32)
        v.base4d = v.tilify(v.base) 
        
    ## --- SOUND ---
    # group manual fadeouts
    elif k == ord('z'):
        s.groupFadeout(s.groups[0])
    elif k == ord('x'):
        s.groupFadeout(s.groups[1])
    elif k == ord('c'):
        s.groupFadeout(s.groups[2])
    elif k == ord('v'):
        s.groupFadeout(s.groups[3])
    
    # group manual fadeins
    elif k == ord('a'):
        s.groupFadeout(s.groups[0])
    elif k == ord('s'):
        s.groupFadeout(s.groups[1])
    elif k == ord('d'):
        s.groupFadeout(s.groups[2])
    elif k == ord('f'):
        s.groupFadeout(s.groups[3])
    
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
            s.start()

def sync(v: VisionManager, s: SoundManager):
    for idx in range(len(v.comp)):
        if v.comp[idx]:
            s.groupFadein(s.groups[idx])
        else:
            s.groupFadeout(s.groups[idx])

def main():
    """main controller for IMS2
    """
    
    # start video playback, get frame height and width
    cap = cv2.VideoCapture(0)
    w = int(cap.get(3))
    h = int(cap.get(4))
    
    # Initialize vision manager
    v = VisionManager(h, w)
    v.base = v.imgManip(cap)
    v.base4d = v.tilify(v.base)
    
    # Initialize sound manager
    s = SoundManager()
    s.assign()
    
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
        sync(v, s)
        
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
        
if __name__ == '__main__':
    main()