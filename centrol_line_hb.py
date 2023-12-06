import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.ndimage as ndimg
from numba import jit
import cv2
from scipy.ndimage import label, generate_binary_structure
from PIL import Image
from time import time

#求图像的字高和字宽
def project_img(image):
    (_, thresh) = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # 形态学处理:定义矩形结构
    image= cv2.erode(thresh, kernel_2, iterations=1)  # 闭运算：迭代1次
    height, width = image.shape[:2]
    w=0
    h=0
    # 垂直投影：统计并存储每一列的黑点数
    vertical = np.zeros(width,dtype=np.int32)
    for x in range(0, width):
        for y in range(0, height):
            if image[y, x] == 0:
                vertical[x]+=1
        if vertical[x] != 0:
            w+=1
   # print("字宽为：",w)

    # 水平投影  #统计每一行的黑点数
    horizontal = np.zeros(height,dtype=np.int32)
    for y in range(0, height):
        for x in range(0, width):
            if image[y, x] == 0:
                horizontal[y] += 1
        if horizontal[y] != 0:
            h+=1
    #print("字高为：",h)
    return w,h

 # check whether this pixel can be removed检查是否要删除这个像素
def check(n):  #n=6    110
    a = [(n >> i) & 1 for i in range(8)]    # >>是右移，右移i位相当于除以2的i次方。
    a.insert(4, 0)  # make the 3x3 unit   九宫格
    # if up, down, left, right all are 1, you cannot make a hole
    # if a[1] & a[3] & a[5] & a[7]:return False不能删
    a = np.array(a).reshape((3, 3))
    # segments
    n = label(a, strc)[1]
    # print(n)
    # if sum is 0, it is a isolate point, you cannot remove it.
    # if number of segments > 2, you cannot split them.
    return n < 2       # n<2返回true 否则返回false
   #  return a.sum() > 1 and n < 2
   #  if a.sum() == 1 or n > 2: return 2
   #  if a.sum() > 1 and n < 2: return 1


strc = np.ones((3, 3), dtype=np.bool)
lut = np.array([check(n) for n in range(256)])
lut = np.dot(lut.reshape((-1, 8)), [1, 2, 4, 8, 16, 32, 64, 128]).astype(np.uint8)
# 点积，比如np.dot([1,2,3],[4,5,6]) = 1*4 + 2*5 + 3*6  = 32 或者矩阵相乘
'''
33 lut = np.array([200, 206, 220, 204, 0, 207, 0, 204, 0, 207, 221, 51, 1, 207, 221, 51,
34        0, 0, 221, 204, 0, 0, 0, 204, 1, 207, 221, 51, 1, 207, 221, 51], dtype=np.int8)
35 '''
# lut=[223 207 221 204   1 207   0 204   1 207 221 255   1 207 221 255   1   0
# 221 204   0   0   0 204   1 207 221 255   1 207 221 255]


@jit
def skel2dp(data, idx, lup):
    h, w = data.shape
    data = data.ravel()  # 把多维的数组降为1维
    for id in idx:
        if data[id] == 0: continue  # 距离为0，就是背景点
        i2 = id - w
        i8 = id + w
        i1 = i2 - 1
        i3 = i2 + 1      #  i1  i2  i3
        i4 = id - 1      #  i4  id  i6
        i6 = id + 1      #  i7  i8  i9
        i7 = i8 - 1
        i9 = i8 + 1     # | 是按位或  &是按位与
        c = (data[i1] > 0) << 0 | (data[i2] > 0) << 1 \
            | (data[i3] > 0) << 2 | (data[i4] > 0) << 3 \
            | (data[i6] > 0) << 4 | (data[i7] > 0) << 5 \
            | (data[i8] > 0) << 6 | (data[i9] > 0) << 7
        #  << 是左移，左移i位相当于乘以2的i次方。
        if (lup[c // 8] >> c % 8) & 1:  # //：两个数相除，结果为向下取整的整数
            data[id] = 0  # 删掉这个点
        sum = (data[i1] > 0)+(data[i2] > 0)+(data[i3] > 0)+(data[i4] > 0)+\
                 (data[i6] > 0)+(data[i7] > 0)+(data[i8] > 0)+(data[i9] > 0)
        if sum == 1:
            data[id] = 1  # 端点不删
        # if (data[i1]&data[i7]==1 and sum==2):
        #     data[id]=0
        #     data[i4]=1
        # if (data[i3]&data[i9]==1 and sum==2):
        #     data[id]=0
        #     data[i4]=6
    return 0

def mid_axis(img):
    dis = ndimg.distance_transform_edt(img)
    idx = np.argsort(dis.flat, kind='heapsort').astype(np.int32)
    skel2dp(dis, idx, lut)
    return dis


def neighbours(x, y, image):
    x_1, y_1, x1, y1 = x - 1, y - 1, x + 1, y + 1
    return [image[x_1][y], image[x_1][y1], image[x][y1], image[x1][y1],  # P2,P3,P4,P5
            image[x1][y], image[x1][y_1], image[x][y_1], image[x_1][y_1]]  # P6,P7,P8,P9

# 计算邻域像素从0变化到1的次数
def transitions(neighbours):
    n = neighbours + neighbours[0:1]  # P2,P3,...,P8,P9,P2
    return sum((n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]))  # (P2,P3),(P3,P4),...,(P8,P9),(P9,P2)

# path = "C:/Users/11603/PycharmProjects/xiong/images/"
path = "D:/xiong/字区分/左上包围结构，如：庙、病、房、尼、眉、历/"
# path ="D:/xiong/test/"
# f = os.listdir(path)
# for i in f:
#     filename = i
#     (name, suffix) = os.path.splitext(filename)
filename ="座"
filename_open = path + filename+".jpg"
img = Image.open(filename_open).convert('L')
img = np.array(img)
# h,w= project_img(img)
# print("中轴线细化前的高和宽：",h,",",w)
for i in range(img.shape[0]):      #反色
    for j in range(img.shape[1]):
        if img[i][j] > 128:
            img[i][j] = 0        #0黑色，255白色
        else:
            img[i][j] = 255
img = Image.fromarray(img)    #实现array到image的转换
img = img.convert('L')
#img = cv2.imread('123.jpg')
#img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#ret2, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
dis = ndimg.distance_transform_edt(img)  #计算图像中非零点到最近背景点（即0）的距离
#plt.imshow(dis)
# plt.show()
idx = np.argsort(dis.flat, kind='heapsort').astype(np.int32)
#argsort()函数是将x中的元素从小到大排列，提取其对应的index(索引)，然后输出到y。快速排序，是一种不稳定的排序算法
#kind : {‘quicksort’, ‘mergesort’, ‘heapsort’, ‘stable’} 快速排序，合并排序，堆排序，稳定排序
#astype()函数可用于转化dateframe某一列的数据类型
a = skel2dp(dis, idx, lut)
#mid_axis(img.copy())
#t1 = time()    #返回UTC时间1970年1月1日至今有多少秒
a = mid_axis(img)
#t2 = time()
#print(t2 - t1) #提取骨架运行时间
img = np.array(a)
rows, columns = img.shape
for x in range(1, rows - 1):
    for y in range(1, columns - 1):
        n = neighbours(x, y, img)
        if img[x][y] == 1 and sum(n) == 2 and n[5] == 1 and n[7] == 1:  #右换到左
            img[x][y] = 0
            img[x][y-1] = 1
            continue
        if img[x][y] == 1 and sum(n) == 2 and n[1] == 1 and n[3] == 1:  #左换到右
            img[x][y] = 0
            img[x][y+1] = 1
            continue
        if img[x][y] == 1 and sum(n) == 2 and n[3] == 1 and n[5] == 1:  #上到下
            img[x][y] = 0
            img[x + 1][y] = 1
            continue
        if img[x][y] == 1 and sum(n) == 2 and n[1] == 1 and n[7] == 1:  #下到上
            img[x][y] = 0
            img[x - 1][y] = 1
            continue
        if img[x][y] == 1 and img[x+2][y-1] == 1 and sum(n) == 2 and n[4] == 1 and n[7] == 1:  # 右到左，两个像素宽
            m = neighbours(x + 1, y, img)
            if sum(m) == 2:
                img[x][y] = img[x+1][y] = 0
                img[x][y-1] = img[x+1][y-1] = 1
                continue
        if img[x][y] == 1 and img[x+2][y+1] == 1 and sum(n) == 2 and n[1] == 1 and n[4] == 1:  # 左到右，两个像素宽
            m = neighbours(x + 1, y, img)
            if sum(m) == 2:
                img[x][y] = img[x+1][y] = 0
                img[x][y+1] = img[x+1][y+1] = 1
                continue
        if img[x][y] == 1 and img[x-1][y+2] == 1 and sum(n) == 2 and n[2] == 1 and n[7] == 1:  # 下到上，两个像素宽
            m = neighbours(x, y+1, img)
            if sum(m) == 2:
                img[x][y] = img[x][y+1] = 0
                img[x-1][y] = img[x-1][y+1] = 1
                continue
        if img[x][y] == 1 and img[x + 1][y + 2] == 1 and sum(n) == 2  and n[2] == 1 and n[5] == 1:  # 上到下，两个像素宽
            m = neighbours(x, y+1, img)
            if sum(m) == 2:
                img[x][y] = img[x][y+1] = 0
                img[x + 1][y+1] = img[x + 1][y] = 1
                continue
for i in range(img.shape[0]):    #颜色返回来
    for j in range(img.shape[1]):
        if img[i][j] > 0:
            img[i][j] = 0
        else:
            img[i][j] = 255
# height,width= project_img(a)
# print("中轴线细化后的高和宽：",height,",",width)
img2 = Image.fromarray(img)
img2 = img2.convert('L')
path2 = "D:/gujia_zhong/z测试/2/"
filename_skeleton = path2 + filename +"1.png"
img2.save(filename_skeleton)
#plt.imshow(a)
# plt.show()
