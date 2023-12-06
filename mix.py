import os
from PIL import Image
import numpy as np

path = r'./image/所有单字'
f = os.listdir(path)
n = 0
for k in f:
    print(n)
    n += 1
    img = Image.open(path + '/' + k + '/' + k + '_skeleton.png')
    img = np.array(img)
    for i in range(15):
        img = np.insert(img, img.shape[0], True, axis=0)
        img = np.insert(img, 0, True, axis=0)
        img = np.insert(img, 0, True, axis=1)
        img = np.insert(img, img.shape[1], True, axis=1)
    img = Image.fromarray(img)
    img.save(path + '/' + k + '/' + k + '_skeleton.png')






