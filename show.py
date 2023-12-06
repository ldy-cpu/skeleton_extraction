import sys
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os

pathf = "D:/project/stroke_segmentation/image/完美骨架已完成"
fil = os.listdir(pathf)
# for k in fil:
k = '暇_SKp'
path = pathf + '/' + k + '/stroke'
f = os.listdir(path)
stroke = Image.open(path + "/" + f[0])
stroke = np.array(stroke)
sp1 = stroke.shape[0]
sp2 = stroke.shape[1]
img = np.ones((stroke.shape[0], stroke.shape[1]), bool)
img = Image.fromarray(img)
img = img.convert('RGB')
img = np.array(img)
np.random.seed(4)
for i in range(len(f)):
    color = np.random.randint(20, high=200, size=(1,3), dtype='l')
    stroke = Image.open(path + "/" + f[i])
    stroke = np.array(stroke)
    for p in range(sp1):
        for q in range(sp2):
            if stroke[p][q] == False:
                img[p][q] = color
                # img[p][q] = False
img = Image.fromarray(img)
# img.show()
img.save(pathf + '/' + k + '/' + k + '_color_2.png')
# stroke = Image.open(path)

