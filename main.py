import cv2
import numpy as np

# start video capture and grab video height and width
cap = cv2.VideoCapture(0)
w = int(cap.get(3))
h = int(cap.get(4))

# user controlled inputs
NUM_QUADS = 4
DIFF = 0.09

# debug flags
DEBUG = True
INFO = True
OVERLAY = True
PERCENTAGE = True

# color values
WHITE = (255, 255, 255)

# define tile dimensions
# num of quadrants: (numTileHeight, numTileWidth, tileHeight, tileWidth)
# or (rows, columns, yMax, xMax)
quads = {
    2: (2, 1, int(h/2), int(w)),
    4: (2, 2, int(h/2), int(w/2)),
    8: (4, 2, int(h/4), int(w/2)),
    16: (4, 4, int(h/4), int(w/4)),
    32: (8, 8, int(h/8), int(w/8)) 
}

# TODO:
# - connect to sounds
# - percentage comparison should scale off of NUM_QUADS
# - turn this mf into a class

def imgManip(cap):
    """takes a video capture frame and passes it through filters for easier manipulation

    Args:
        cap (cv2 image): frame from video capture

    Returns:
        np.array: the manipulated frame data as an np.array
    """
    
    # read frame data
    _, img = cap.read()
    
    # gray scale -> blur -> canny -> threshhold pass
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 10, 17)
    _, mask = cv2.threshold(canny, 70, 255, cv2.THRESH_BINARY)

    return np.asarray(mask)

def tilify(image: np.ndarray, tile_size: tuple):
    """splits an image into tiled chunks of a specified size

    Args:
        image (np.ndarray): cv2 frame data in array form
        tile_size (tuple): tuple of ints declaring the number of rows and columns of tiles

    Returns:
        np.ndarray: frame data rearranged into tiled chunks
    """    
    
    # get sizes for tiles and height / width of image
    global h, w
    th, tw = tile_size
    
    # reshape the frame data into tiled chunks
    tiled_array = image.reshape(
        h // th,
        th,
        w // tw,
        tw 
        # you can add another element for color channels here, 
        # but since we are using black and white 
        # we do not need one
    )
    
    tiled_array = tiled_array.swapaxes(1, 2)

    # this returns a 4d array.
    # we can use this to manage quadrants and do math
    # but we cannot show this image
    return tiled_array

def detect(base: np.ndarray, new: np.ndarray):
    """detects the percentage difference between two tiled frames

    Args:
        base (np.ndarray): base tiled frame for comparison
        new (np.ndarray): current tiled frame

    Returns:
        np.ndarray: bool for each quadrant denoting if it was over the given trigger percentage
    """ 
    
    #grab globals
    global h, w, NUM_QUADS, quads

    # empty np array to keep track of the comparison bools
    info = np.empty((NUM_QUADS))
    qc = 0

    # ittr through tiled old frame and new 
    for z, x in zip(base, new):
        for b, n in zip(z, x):
            
            # compare difference percentage between the two tiles
            percent = np.mean(b != n)
            
            # debug output of the percentage difference
            if DEBUG and PERCENTAGE:
                print(f'comparison: {(percent * 100):.2f}%')
                
            # add bool to info array
            if percent > DIFF:
                info[qc] = True
                qc += 1
            else:
                info[qc] = False
                qc += 1

    # debug output bool array
    if DEBUG and INFO:
        print(f'quad info: {info}')
    
    return info

def drawRect(image: np.ndarray, info: np.ndarray):
    """draw rectangles over each quadrant

    Args:
        image (np.ndarray): tiled image to draw over
        info (np.ndarray): array of quadrant bool data

    Returns:
        np.ndarray: image with quadrant overlays
    """    
    
    #grab globals
    global WHITE, NUM_QUADS, quads
    
    # set locals
    tup = quads[NUM_QUADS]
    x1, y1 = 0, 0
    y2 = tup[2]
    x2 = tup[3]
    qc = 0

    # for each row
    for i in range(0, tup[1]):
        # for each column
        image = cv2.rectangle(image, (x1,y1), (x2,y2), WHITE, 3)
        # debug output text
        if DEBUG and OVERLAY:
            image = cv2.putText(
                image,
                f'{"On" if info[qc] else "Off"}',
                (x1 + 60, y1 + 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                WHITE,
                3,
                cv2.LINE_AA
            )
        qc += 1
        for j in range(0, tup[0] - 1):
            # shift starting y
            y1 += tup[2]
            # shift ending y
            y2 += tup[2]
            # add rect to image
            image = cv2.rectangle(image, (x1,y1), (x2,y2), WHITE, 3)
            # debug output text
            if DEBUG and OVERLAY:
                image = cv2.putText(
                    image,
                    f'{"On" if info[qc] else "Off"}',
                    (x1 + 60, y1 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    WHITE,
                    3,
                    cv2.LINE_AA
            )
            qc += 1
            
        # reset y
        y1 = 0
        y2 = tup[2]
        
        # shift starting x
        x1 += tup[3]
        # shift ending x
        x2 += tup[3]
                   
    return image

# base image
base = imgManip(cap)
# change this later (this is only for the 1x1)
base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))

while True:
    
    # use edge detection on frame
    data = imgManip(cap)
    # reorganize the image into tiles
    data4d = tilify(data, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))
    # compare differences in original image and current frame
    comp = detect(base4d, data4d)
    # draw rectangles on frame
    withRect = drawRect(data, comp)
    
    # show image on screen
    cv2.imshow('IMS2', withRect)
    
    # keyboard commands
    k = cv2.waitKey(1)
    
    # quit on enter
    if k == 13:
        break

    # toggle debug
    elif k == ord('d'):
        DEBUG = not DEBUG
    elif k == ord('i'):
        INFO = not INFO
    elif k == ord('p'):
        PERCENTAGE = not PERCENTAGE
    elif k == ord('o'):
        OVERLAY = not OVERLAY
    
    # recapture base image
    elif k == ord('r'):
        base = imgManip(cap)
        
    # switch through quadrants
    elif k == ord("1"):
        NUM_QUADS = 2
        base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))
    elif k == ord("2"):
        NUM_QUADS = 4
        base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))
    elif k == ord("3"):
        NUM_QUADS = 8
        base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))
    elif k == ord("4"):
        NUM_QUADS = 16
        base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))
    elif k == ord("5"):
        NUM_QUADS = 32
        base4d = tilify(base, ((quads[NUM_QUADS][2], quads[NUM_QUADS][3])))


# release camera 
cap.release()
cv2.destroyAllWindows()