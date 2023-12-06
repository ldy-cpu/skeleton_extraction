import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import filters
from pylab import *

# 读入图像并转化为float类型，用于传递给harris函数
filename = './image/电1/电1_skeleton.png'
img = Image.open(filename)
img = np.array(img)
# for i in range(img.shape[0]):
#     for j in range(img.shape[1]):
#         if img[i][j] == True:
#             img[i][j] = 255
#         else:img[i][j] = 0
gray_img = np.float32(img)

# 对图像执行harris
Harris_detector = cv2.cornerHarris(gray_img, 8, 3, 0.1)
# print(Harris_detector)
# 膨胀harris结果
dst = cv2.dilate(Harris_detector, None)

# 设置阈值
thres = 0.01 * dst.max()
gray_img[dst > thres] = [255]
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if Harris_detector[i][j]>0:
            print(j,i)
            gray_img[i][j] = 255
# cv2.imwrite('./image/TEST/harris.png',gray_img)
cv2.imshow('show', gray_img)
cv2.waitKey()


# def compute_harris_response(im, sigma=3):
#     """ Compute the Harris corner detector response function
#         for each pixel in a graylevel image. """
#
#     # derivatives
#     imx = zeros(im.shape)
#     filters.gaussian_filter(im, (sigma, sigma), (0, 1), imx)
#     imy = zeros(im.shape)
#     filters.gaussian_filter(im, (sigma, sigma), (1, 0), imy)
#
#     # compute components of the Harris matrix
#     Wxx = filters.gaussian_filter(imx * imx, sigma)
#     Wxy = filters.gaussian_filter(imx * imy, sigma)
#     Wyy = filters.gaussian_filter(imy * imy, sigma)
#
#     # determinant and trace
#     Wdet = Wxx * Wyy - Wxy ** 2
#     Wtr = Wxx + Wyy
#
#     return Wdet / Wtr
#
#
# im = np.array(Image.open("D:\project\stroke_segmentation\image/弹_centrol.png").convert('L'))
# q = compute_harris_response(im,sigma=3)
# p = np.zeros((q.shape[0],q.shape[1]))
# for i in range(q.shape[0]):
#     for j in range(q.shape[1]):
#         if q[i][j]>0.33:
#             p[i][j] = q[i][j] * 10000
# p = Image.fromarray(p)
# p = p.convert('L')
# p.show()
