import cv2
import numpy as np

# TODO
# - percentage comparison should scale of NUM_QUADS

class VisionManager:
    def __init__(self, h: int, w: int):
        """initialize variables, flags, and the uad dictionary

        Args:
            h (int): height of image
            w (int): width of image
        """
        
        # image related variables
        self.h = h
        self.w = w
        self.base = None
        self.base4d = None
        self.curr = None
        self.curr4d = None
        self.comp = None
        self.final = None
        
        # quadrant related variables
        self.NUM_QUADS = 4
        self.DIFF = 0.09
        self.quads = {
            2: (2, 1, int(h/2), int(w)),
            4: (2, 2, int(h/2), int(w/2)),
            8: (4, 2, int(h/4), int(w/2)),
            16: (4, 4, int(h/4), int(w/4)),
        }
        
        # debug flags
        self.DEBUG = True
        self.INFO = True
        self.OVERLAY = True
        self.PERCENTAGE = True
        
        # color variables
        self.WHITE = (255, 255, 255)
        
    def imgManip(self, cap):
        """takes a video capture frame and passes it through filters for esaier manipulation

        Args:
            cap (cv2 image): frame from video capture
            
        Returns:
            np.ndarray: manipulated frame data as an np.ndarray
        """
        
        # read frame data
        _, img = cap.read()
        
        # gray scale -> blur -> canny -> threshold pass
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.blur(gray, (5, 5), 0)
        canny = cv2.Canny(blur, 10, 17)
        _, mask = cv2.threshold(canny, 70, 255, cv2.THRESH_BINARY)
        
        return np.asarray(mask)
    
    def tilify(self, image:np.ndarray):
        """splits an image into tiled chunks of a specified size

        Args:
            image (np.ndarray): cv2 frame data in array form

        Returns:
            np.ndarray: frame data rearranged into 4d tiled chunks
        """
        
        # set tile height and width variables 
        th = self.quads[self.NUM_QUADS][2]
        tw = self.quads[self.NUM_QUADS][3]
        
        # reshape frame data into tiled chunks
        tiled_array = image.reshape(
            self.h // th,
            th,
            self.w // tw,
            tw
            # you can add another element for color channels here,
            # but since we are using black and white 
            # we do not need one
        )
        
        tiled_array = tiled_array.swapaxes(1, 2)
        
        # this returns a 4d array
        # we can use this to manage and compare quadrants 
        # but it cannot be shown to the screen
        return tiled_array
    
    def detect(self, base: np.ndarray, curr: np.ndarray):
        """detects the percentage difference between two tiled frames

        Args:
            base (np.ndarray): base tiled frame for comparison
            new (np.ndarray): current tiled frame

        Returns:
            np.ndarray: bool for each quadrant denoting if it was over the given trigger percentage
        """
        
        # empty np array and counter to keep track of the comparison bools
        info = np.empty((self.NUM_QUADS))
        qc = 0
        
        # ittr through tiled old frame and tiled current frame
        for z, x in zip(base, curr):
            for b, c in zip(z, x):
                
                # compare difference percentage between the two tiles
                percent = np.mean(b != c)
                
                # debug output of the percentage difference
                if self.DEBUG and self.PERCENTAGE:
                    print(f'comparison: {(percent * 100):.2f}%')
                
                # add bool to info array
                if percent > self.DIFF:
                    info[qc] = True
                    qc += 1
                else:
                    info[qc] = False
                    qc += 1
        
        # debug output bool array
        if self.DEBUG and self.INFO:
            print(f'quad info: {info}')
        
        return info
    
    def drawRect(self, image: np.ndarray, info: np.ndarray):
        """draw rectangles over each quadrant

        Args:
            image (np.ndarray): tiled image to draw over
            info (np.ndarray): array of quadrant bool data

        Returns:
            np.ndarray: image with quadrant overlays added
        """
        
        # set local variables
        tup = self.quads[self.NUM_QUADS]
        x1, y1, qc = 0, 0, 0
        y2 = tup[2]
        x2 = tup[3]
        
        # for each row
        for i in range(0, tup[1]):
            # draw top rectangle in column
            image = cv2.rectangle(image, (x1,y1), (x2,y2), self.WHITE, 3)

            # debug output text
            if self.DEBUG and self.OVERLAY:
                image = cv2.putText(
                    image,
                    f'{"On" if info[qc] else "Off"}',
                    (x1 + 60, y1 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    self.WHITE,
                    3,
                    cv2.LINE_AA
                )
            # incr which quadrant we are working with
            qc += 1
            
            #for each column
            for j in range(0, tup[0] - 1):
                # shift starting y
                y1 += tup[2]
                # shift ending y
                y2 += tup[2]
                # add next rect to column
                image = cv2.rectangle(image, (x1,y1), (x2,y2), self.WHITE, 3)
                #debug output text
                if self.DEBUG and self.OVERLAY:
                    image = cv2.putText(
                        image,
                        f'{"On" if info[qc] else "Off"}',
                        (x1 + 60, y1 + 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        self.WHITE,
                        3,
                        cv2.LINE_AA
                    )
                # incr which quadrant we are working on
                qc += 1
            
            # reset y
            y1 = 0
            y2 = tup[2]
            
            # shift starting x
            x1 += tup[3]
            # shift ending x
            x2 += tup[3]
        
        return image
    
    def toggleDebug(self):
        """toggle debug flag
        """        
        self.DEBUG = not self.DEBUG
    
    def toggleInfo(self):
        """toggle quadrant info flag
        """    
        self.INFO = not self.INFO
        
    def togglePercentage(self):
        """toggle percentage comparison flag
        """        
        self.PERCENTAGE = not self.PERCENTAGE
    
    def toggleOverlay(self):
        """toggle On/Off overlay flag
        """        
        self.OVERLAY = not self.OVERLAY
        
    def rebase(self, cap):
        """reset the base image used for comparison

        Args:
            cap (np.ndarray): frame data from cv2 video capture
        """        
        self.base = imgManip(cap)
        print(f'reset base image')
        
    def updateNumQuads(self, n: int):
        if n in self.quads:
            self.NUM_QUADS = n

    