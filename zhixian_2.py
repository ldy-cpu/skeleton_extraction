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

def find_point(image):
    img_with = image.copy()  # Making copy to protect original image
    points = []
    rows, columns = img_with.shape
    for x in range (rows):
        for y in range(columns):
            if (img_with[x][y] == 0):
                point = (x,y)
                points.append(point)
    return  points




path ="D:\project\stroke_segmentation\image\完美骨架已完成\凰_SKp"
# f=os.listdir(path)
# for i in f:
#     filename = i
# path ="D:/xiong/test/"
filename ="/凰"
filename_open = path + filename+"_SKp.png"
img = Image.open(filename_open).convert('L')
img = np.array(img)
for i in range(img.shape[0]):      #反色
    for j in range(img.shape[1]):
        if img[i][j] > 128:
            img[i][j] = 0        #0黑色，255白色
        else:
            img[i][j] = 1
# a=find_point(img)
# for x,y in a:
#     n = neighbours(x, y, img)
#     if (img[x][y] == 1 and sum(n) == 2 and n[5]==1 and n[7]==1):
#         img[x][y]=0
#         img[x-1][y]=1
#         #n[6]=0
#     if (img[x][y] == 1 and sum(n) == 2 and n[1]==1 and n[3] == 1):
#         img[x][y] = 0
#         img[x+1][y]=1
#         #n[2] =0
rows, columns = img.shape
for x in range(1, rows - 1):
    for y in range(1, columns - 1):
        n = neighbours(x, y, img)
        if (img[x][y] == 1 and sum(n) == 2 and n[5]==1 and n[7]==1): #右换到左
            img[x][y]=0
            img[x][y-1] = 1
            continue
            #n[6]=1
        if (img[x][y] == 1 and sum(n) == 2 and n[1]==1 and n[3] ==1):#左换到右
            img[x][y] = 0
            img[x][y+1] = 1
            continue
            #n[2] =1
        if (img[x][y] == 1 and sum(n) == 2 and n[3] == 1 and n[5] == 1):#上到下
            img[x][y] = 0
            img[x + 1][y] = 1
            continue
        if (img[x][y] == 1 and sum(n) == 2 and n[1] == 1 and n[7] == 1):#下到上
            img[x][y] = 0
            img[x - 1][y] = 1
            continue
        if (img[x][y] == 1 and img[x+2][y-1] ==1 and sum(n) == 2 and img[x-1][y-1] == 1 and img[x+1][y] == 1):  # 右到左，两个像素宽
            img[x][y] = img[x+1][y] = 0
            img[x][y-1] = img[x+1][y-1] = 1
            continue
        if (img[x][y] == 1 and img[x+2][y+1] ==1 and sum(n) == 2 and img[x-1][y+1] == 1 and img[x+1][y] == 1):  # 右到左，两个像素宽
            img[x][y] = img[x+1][y] = 0
            img[x][y+1] = img[x+1][y+1] = 1
            continue

for i in range(img.shape[0]):    #颜色返回来
    for j in range(img.shape[1]):
        if img[i][j] > 0:
            img[i][j] =0
        else:
            img[i][j] = 255
img2 = Image.fromarray(img)    #实现array到image的转换
#img = img.convert('L')


path2="D:\project\stroke_segmentation\image\完美骨架已完成\凰_SKp"
filename_skeleton = path2 + filename +"_直线.png"
img2.save(filename_skeleton)
plt.imshow(img2)
# plt.show()