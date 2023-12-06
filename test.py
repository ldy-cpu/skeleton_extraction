from PIL import Image
import numpy as np
# from segmentation import ineighbor,point_class
# path = r'D:\project\stroke_segmentation\image'
# ori = r'\笔画降_skeleton'
# img = Image.open(path + ori + '.png')
# img = np.array(img)
#
# x = point_class(img,28,27)
# print(x)


# import numpy as np
# def clockwise_angle(v1, v2):
#  x1,y1 = v1
#  x2,y2 = v2
#  dot = x1*x2+y1*y2
#  det = x1*y2-y1*x2
#  theta = np.arctan2(det, dot)
#  theta = theta if theta>0 else 2*np.pi+theta
#  theta = theta * 180 / np.pi
#  theta = int(theta)
#  if theta > 182:
#      theta = 360 - theta
#  return theta
#
#
# v1 = [0,1]
# v2 = [0,1]
# theta = clockwise_angle(v1,v2)
#
# print(theta) # 24.77

# path = r'D:\project\stroke_segmentation\image'
# ori = r'\笔降_skeleton'
# img = Image.open(path + ori + '.png')
# img = np.array(img)
# np.savetxt(path+ori+'.txt', img ,fmt="%d")

