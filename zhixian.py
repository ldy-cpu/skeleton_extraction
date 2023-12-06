import os
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
# 定义像素点周围的8邻域
#                P9 P2 P3
#                P8 P1 P4
#                P7 P6 P5

def neighbours(x, y, image):
    img = image
    x_1, y_1, x1, y1 = x - 1, y - 1, x + 1, y + 1
    return [img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1],  # P2,P3,P4,P5
            img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1]]  # P6,P7,P8,P9

# 计算邻域像素从0变化到1的次数
def transitions(neighbours):
    n = neighbours + neighbours[0:1]  # P2,P3,...,P8,P9,P2
    return sum((n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]))  # (P2,P3),(P3,P4),...,(P8,P9),(P9,P2)






path ="D:\project\stroke_segmentation\image\完美骨架正确\杆_SKp"
# f=os.listdir(path)
# for i in f:
#     filename = i
# path ="D:/xiong/test/"
filename ="/杆_SKp"
filename_open = path + filename+".png"
img = Image.open(filename_open).convert('L')
img = np.array(img)

# 找直线中不平滑的像素点
img_with = img.copy()  # Making copy to protect original image
rows, columns = img_with.shape

for x in range(1, rows - 1):
    for y in range(1, columns - 1):
        n = neighbours(x, y, img_with)
        if (img_with[x][y] == 0 and sum(n) == 1530 and n[5]==0 and n[7]==0):
            img_with[x][y]=255
            img_with[x][y-1]=0
            #n[6]=0
        if (img_with[x][y] == 255 and sum(n) == 1530 and n[1]==0 and n[3] == 0):
            img_with[x][y] = 255
            img_with[x][y+1]=0
            #n[2] =0
        if (img_with[x][y] == 0 and sum(n) == 1530 and n[3] == 0 and n[6] == 0):
            img_with[x][y] = 255
            img_with[x+1][y] = 0
            # n[6]=0
        if (img_with[x][y] == 255 and sum(n) == 1530 and n[1] == 0 and n[7] == 0):
            img_with[x][y] = 255
            img_with[x-1][y] = 0
            # n[2] =0

img2 = Image.fromarray(img_with)    #实现array到image的转换
#img = img.convert('L')


path2="D:\project\stroke_segmentation\image\完美骨架正确\杆_SKp"
filename_skeleton = path2 + filename +"_直线.png"
img2.save(filename_skeleton)
plt.imshow(img2)
plt.show()