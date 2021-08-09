#This is the prototype detection method using edge detecion.
#Seems to work really well in moderate lighting. Needs testing in dim / bright lighting
from ast import Num
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
w = int(cap.get(3))
h = int(cap.get(4))

NUM_QUADS = 4
DEBUG = True

WHITE = (255, 255, 255)

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
# - fix debug on / off text
# - percentage comparison should scale off of NUM_QUADS
# - connect to sounds

def retileBase(base):
    return 

def imgManip(cap):
    _, img = cap.read()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 10, 17)
    _, mask = cv2.threshold(canny, 70, 255, cv2.THRESH_BINARY)

    return np.asarray(mask)

def tilify(image: np.ndarray, tile_size: tuple):
    # get sizes for tiles and height / width of image
    global h, w
    th, tw = tile_size
    
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

    pass

def detect(base: np.ndarray, new: np.ndarray):
    global h, w, NUM_QUADS, quads
    info = np.empty((NUM_QUADS))
    qc = 0

    for z, x in zip(base, new):
        for b, n in zip(z, x):
            percent = np.mean(b != n)
            if DEBUG:
                print(f'comparison%: {percent}')
            if percent > 0.1:
                info[qc] = True
                qc += 1
            else:
                info[qc] = False
                qc += 1

    if DEBUG:
        print(f'quad info: {info}')
    
    return info

def drawRect(image: np.ndarray, info: np.ndarray):
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
        if DEBUG:
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
            
        for j in range(0, tup[0]):
            # shift starting y
            y1 += tup[2]
            # shift ending y
            y2 += tup[2]
            # add rect to image
            image = cv2.rectangle(image, (x1,y1), (x2,y2), WHITE, 3)
            
            # debug output text
            if DEBUG:
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
    # switch through quadrants?
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


cap.release()
cv2.destroyAllWindows()