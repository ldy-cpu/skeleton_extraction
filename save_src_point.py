import os.path
import sys
import pickle
from PIL import Image
import numpy  as np

path = r'D:\project\stroke_segmentation\image\TEST\match_point'
ori = r'\matches_丑_src'
img = Image.open(path + ori + '.png')
img = np.array(img)
points = []
for i in range(img.shape[0]):  ######将src点以列表存储，在列表中位置代表点的id
    for j in range(img.shape[1]):
        if img[i][j] >10:
            points.append((j,i)) #############保存的点列表用（x,y）形式保存


name = "/丑"
point_path = path + name + "/src_point.bin"   ###点id

# if not os.path.exists(point_path):
#     os.mkdir(point_path)

with open(point_path, "wb") as output:
    pickle.dump(points, output)

