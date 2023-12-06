# import cv2,time
# import numpy as np
#
#
#
# def Three_element_add(array):
#     array0 = array[:]
#     array1 = np.append(array[1:],np.array([0]))
#     array2 = np.append(array[2:],np.array([0, 0]))
#     arr_sum = array0 + array1 + array2
#     return arr_sum[:-2]
#
#
# def VThin(image, array):
#     NEXT = 1
#     height, width = image.shape[:2]
#     for i in range(1,height):
#         M_all = Three_element_add(image[i])
#         for j in range(1,width):
#             if NEXT == 0:
#                 NEXT = 1
#             else:
#                 M = M_all[j-1] if j<width-1 else 1
#                 if image[i, j] == 0 and M != 0:
#                     a = np.zeros(9)
#                     if height-1 > i and width-1 > j:
#                         kernel = image[i - 1:i + 2, j - 1:j + 2]
#                         a = np.where(kernel == 255, 1, 0)
#                         a = a.reshape(1, -1)[0]
#                     NUM = np.array([1,2,4,8,0,16,32,64,128])
#                     sumArr = np.sum(a*NUM)
#                     image[i, j] = array[sumArr] * 255
#                     if array[sumArr] == 1:
#                         NEXT = 0
#     return image
#
#
# def HThin(image, array):
#     height, width = image.shape[:2]
#     NEXT = 1
#     for j in range(1,width):
#         M_all = Three_element_add(image[:,j])
#         for i in range(1,height):
#             if NEXT == 0:
#                 NEXT = 1
#             else:
#                 M = M_all[i-1] if i < height - 1 else 1
#                 if image[i, j] == 0 and M != 0:
#                     a = np.zeros(9)
#                     if height - 1 > i and width - 1 > j:
#                         kernel = image[i - 1:i + 2, j - 1:j + 2]
#                         a = np.where(kernel == 255, 1, 0)
#                         a = a.reshape(1, -1)[0]
#                     NUM = np.array([1, 2, 4, 8, 0, 16, 32, 64, 128])
#                     sumArr = np.sum(a * NUM)
#                     image[i, j] = array[sumArr] * 255
#                     if array[sumArr] == 1:
#                         NEXT = 0
#     return image
#
#
# def Xihua(binary, array, num=10):
#     binary_image = binary.copy()
#     image = cv2.copyMakeBorder(binary_image, 1, 0, 1, 0, cv2.BORDER_CONSTANT, value=0)
#     for i in range(num):
#         VThin(image, array)
#         HThin(image, array)
#     return image
#
#
# array = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,\
#          1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1,\
#          0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,\
#          1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1,\
#          1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\
#          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\
#          1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1,\
#          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\
#          0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,\
#          1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1,\
#          0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,\
#          1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,\
#          1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\
#          1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,\
#          1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0,\
#          1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0]
#
#
# if __name__ == '__main__':
#     image = cv2.imread(r'Test/73.jpg', 0)
#     ret, binary = cv2.threshold(image, 70, 255, cv2.THRESH_BINARY)
#     cv2.imshow('image', image)
#     cv2.imshow('binary', binary)
#     cv2.waitKey(0)
#
#     t1 = time.time()
#
#     iThin = Xihua(binary, array)
#     t2 = time.time()
#     print('cost time:',t2-t1)
#     cv2.imshow('iThin', iThin)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
'''
cost time: 7.425575494766235
'''

# 导入库
import os.path
import sys

import matplotlib
import matplotlib.pyplot as plt
import skimage.io as io
import cv2 as cv
import numpy as np

# 将图像转为灰度图像
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


# Zhang-Suen 细化算法
def zhangSuen(image):
    Image_Thinned = image.copy()  # Making copy to protect original image
    changing1 = changing2 = 1
    while changing1 or changing2:  # Iterates until no further changes occur in the image
        # Step 1
        changing1 = []
        rows, columns = Image_Thinned.shape
        for x in range(1, rows - 1):
            for y in range(1, columns - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, Image_Thinned)
                if (Image_Thinned[x][y] == 1 and  # Condition 0: Point P1 in the object regions
                        2 <= sum(n) <= 6 and  # Condition 1: 2<= N(P1) <= 6
                        transitions(n) == 1 and  # Condition 2: S(P1)=1
                        P2 * P4 * P6 == 0 and  # Condition 3
                        P4 * P6 * P8 == 0):  # Condition 4
                    changing1.append((x, y))
        for x, y in changing1:
            Image_Thinned[x][y] = 0
        # Step 2
        changing2 = []
        for x in range(1, rows - 1):
            for y in range(1, columns - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, Image_Thinned)
                if (Image_Thinned[x][y] == 1 and  # Condition 0
                        2 <= sum(n) <= 6 and  # Condition 1
                        transitions(n) == 1 and  # Condition 2
                        P2 * P4 * P8 == 0 and  # Condition 3
                        P2 * P6 * P8 == 0):  # Condition 4
                    changing2.append((x, y))
        for x, y in changing2:
            Image_Thinned[x][y] = 0
    return Image_Thinned



path = r"./image"
zilei = r'/字区分/左中右结构，如：湖，脚，溅，谢，做，粥'
f = os.listdir(path + zilei)
##################################################################
for fi in f:

    name = fi
    if '.png' in name:
        name = name[0:-4]
    if '.jpg' in name:
        name = name[0:-4]
    if not os.path.exists(path + '/所有单字/' + name):
        os.mkdir(path + '/所有单字/' + name)

    filename = '/' + fi
    filename_open = path + zilei + filename
    filename_save = path + filename + "_1.png"
    # img = Image.open("zheng.JPG").convert('L')
    # img = Image.open("Test/yi2.JPG").convert('L')
    # img.save('Test/91.jpg')
    img = Image.open(filename_open).convert('L')
    img.save(filename_save)

    # 读取灰度图像
    Img_Original = io.imread(filename_save)
    os.remove(filename_save)

    # 对图像进行预处理，二值化
    from skimage import filters
    from skimage.morphology import disk

    # 中值滤波
    # Img_Original = filters.median(Img_Original, disk(5))
    # 二值化
    BW_Original = Img_Original < 130
    # plt.show(BW_Original)

    # 对染色体图像应用Zhang-Suen细化算法
    BW_Skeleton = zhangSuen(BW_Original)
    txt_skeleton = path + filename + "_skeleton.txt"
    # np.savetxt(txt_skeleton, BW_Skeleton, fmt='%d')
    # print(BW_Skeleton.shape)
    txt_original = path + filename + "_original.txt"
    # np.savetxt(txt_original, BW_Original, fmt='%d')
    BW_Skeleton = np.invert(BW_Skeleton)
    # np.savetxt('./image/skeleton2.txt', BW_Skeleton, fmt='%d')

    # plt.imshow(BW_Original, cmap=plt.cm.gray)
    # plt.axis('off')
    # plt.show()

    # 显示细化结果
    # plt.imshow(BW_Skeleton, cmap=plt.cm.gray)
    # plt.axis('off')
    # plt.show()

    # # plt.savefig('Test/01.jpg')
    # fig, ax = plt.subplots(1, 2)
    # ax1, ax2 = ax.ravel()
    # ax1.imshow(img, cmap=plt.cm.gray)
    # ax1.set_title('Original binary image')
    # ax1.axis('off')
    # ax2.imshow(BW_Skeleton, cmap=plt.cm.gray)
    # ax2.set_title('Skeleton of the image')
    # ax2.axis('off')

    # filename_fig = path + filename + "_fig.png"
    # plt.savefig(filename_fig)
    img2 = Image.fromarray(BW_Skeleton)

    filename_skeleton = path + '/所有单字/' + name + "/" + name +"_skeleton.png"
    img2.save(filename_skeleton)
    # plt.show()
#######################################################################################
# filename = "/竖折折钩_skeleton"
# if not os.path.exists(path+filename):
#     os.mkdir(path+filename)
#
# filename_open = path + "/单笔画" + filename + ".png"
# filename_save = path + filename + "_1.png"
# # img = Image.open("zheng.JPG").convert('L')
# # img = Image.open("Test/yi2.JPG").convert('L')
# # img.save('Test/91.jpg')
# img = Image.open(filename_open).convert('L')
# img.save(filename_save)
#
# # 读取灰度图像
# Img_Original = io.imread(filename_save)
# os.remove(filename_save)
#
# # 对图像进行预处理，二值化
# from skimage import filters
# from skimage.morphology import disk
#
# # 中值滤波
# # Img_Original = filters.median(Img_Original, disk(5))
# # 二值化
# BW_Original = Img_Original < 130
# # plt.show(BW_Original)
#
# # 对染色体图像应用Zhang-Suen细化算法
# BW_Skeleton = zhangSuen(BW_Original)
# txt_skeleton = path + filename + "_skeleton.txt"
# # np.savetxt(txt_skeleton, BW_Skeleton, fmt='%d')
# # print(BW_Skeleton.shape)
# txt_original = path + filename + "_original.txt"
# # np.savetxt(txt_original, BW_Original, fmt='%d')
# BW_Skeleton = np.invert(BW_Skeleton)
# # np.savetxt('./image/skeleton2.txt', BW_Skeleton, fmt='%d')
#
# plt.imshow(BW_Original, cmap=plt.cm.gray)
# plt.axis('off')
# # plt.show()
#
# # 显示细化结果
# plt.imshow(BW_Skeleton, cmap=plt.cm.gray)
# plt.axis('off')
# # plt.show()
#
# # plt.savefig('Test/01.jpg')
# fig, ax = plt.subplots(1, 2)
# ax1, ax2 = ax.ravel()
# ax1.imshow(img, cmap=plt.cm.gray)
# ax1.set_title('Original binary image')
# ax1.axis('off')
# ax2.imshow(BW_Skeleton, cmap=plt.cm.gray)
# ax2.set_title('Skeleton of the image')
# ax2.axis('off')
#
# filename_fig = path + filename + "_fig.png"
# # plt.savefig(filename_fig)
# img2 = Image.fromarray(BW_Skeleton)
#
# filename_skeleton = path + filename + filename +"_skeleton.png"
# img2.save(filename_skeleton)
# # plt.show()
#################################################################################################
