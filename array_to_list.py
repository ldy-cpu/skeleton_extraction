import os

import numpy as np

path = r"./image/"
f = os.listdir(path)
for k in f:

    stroke = np.load(path + k + "/src_stroke.npy")
    point_to_stroke = []
    for i in range(stroke.shape[0]):
        H = []
        for j in range(stroke.shape[0]):
            L = []
            if stroke[i][j]>0:
                L.append(stroke[i][j])
            H.append(L)
        point_to_stroke.append(H)
    point_to_stroke = np.array(point_to_stroke)
    np.save(path + k + "/src_stroke.npy",arr = point_to_stroke)
