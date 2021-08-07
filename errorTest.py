import numpy as np

a = np.array([0, 0, 0, 1, 1, 1, 1, 1, 0, 0])
b = np.array([1, 0, 0, 1, 1, 1, 1, 1, 0, 0])
error = np.mean( a != b)
print(error)

c = np.arange(1,25, dtype=('uint8')).reshape(6,4)
print(c)
print(c.strides)

d = np.lib.stride_tricks.as_strided(c, shape=(2, 6, 2), strides=(2, 4, 1))
print(d)
print(d.shape)
print(d.strides)

e = np.lib.stride_tricks.as_strided(d, shape=(3, 2, 2, 2), strides=(8, 2, 4, 1))
print(e)
print(e.shape)
print(e.strides)

# SHAPE = ((IMG_HEIGHT / TILE_HEIGHT), (IMG_WIDTH, TILE_WIDTH), TILE_HEIGHT, TILE_WIDTH)
# STRIDES = ((IMG_WIDTH x TILE_HEIGHT x BYTESIZE, TILE_WIDTH x BYTSIZE, IMG_WIDTH x BYTESIZE, BYTESIZE))
