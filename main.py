#This is the prototype detection method using edge detecion.
#Seems to work really well in moderate lighting. Needs testing in dim / bright lighting
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
w = int(cap.get(3))
h = int(cap.get(4))

#should try to support 2, 4, 8, 16, 32
#HAVE to have 8 for sure
#starting with 2, 4
NUM_QUADS = 2

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

def detect(base, new, quad):

    global h, w, NUM_QUADS
    # #testing only new white pixles
    # base = base[base != 0]
    # new = new[new != 0]
    
    #1x1 horizontal
    if NUM_QUADS == 2:
        for each in NUM_QUADS:
            pass
    pass

base = imgManip(cap)
# change this later (this is only for the 1x1)
base4d = tilify(base, ((int(h/2), int(w))))

print(base4d)

while True:
    data = imgManip(cap)
    test = tilify(data, ((int(h/2), int(w))))
    cv2.imshow('Video feed', data)
    
    if cv2.waitKey(1) == 13:
        break


cap.release()
cv2.destroyAllWindows()