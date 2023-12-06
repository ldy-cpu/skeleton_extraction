import math

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import sys
from sympy import *


def clockwise_angle(v1, v2):
 x1,y1 = v1
 x2,y2 = v2
 dot = x1*x2+y1*y2
 det = x1*y2-y1*x2
 theta = np.arctan2(det, dot)
 theta = theta if theta>0 else 2*np.pi+theta
 theta = theta * 180 / np.pi
 # theta = int(theta)
 if theta > 180:
     theta = (360 - theta)
 return theta





def derivation(poly_para,t):   ##  求x或y对t的导数
    f = 0
    for i in range(0,poly_para.shape[0]-1):
        iso = poly_para[i]*(poly_para.shape[0]-1-i)
        for j in range(1,poly_para.shape[0]-1-i):
            iso = iso * t
        f = f + iso

    return f





def curvature(t,diff,poly_x,poly_y,num):    ########   微分diff长度的弧两端的切线夹角，除以diff长度，得到近似曲率
    dy_t = derivation(poly_y, t)
    dx_t = derivation(poly_x, t)  ###防止dx_t = 0做分母
    diff_per = 0.00027 * num
    dy_t_diff = derivation(poly_y, t + diff_per )
    dx_t_diff = derivation(poly_x, t + diff_per )
    # dy_x = dy_t/dx_t       ###   斜率
    angle = clockwise_angle([dx_t, dy_t], [dx_t_diff, dy_t_diff])  ###  和x轴夹角
    curve = math.fabs(angle)/diff
    print(curve)
    return curve



def getcurve(ori_s,ori_x,ori_y,pixel,num,lxl):
    deg = 7
    # path = r'D:\project\stroke_segmentation\image\弯钩_skeleton\弯钩_skeleton_skeleton.png'
    # img = Image.open(path)
    # img = np.array(img)
    # ori_s = []
    # ori_x = []
    # ori_y = []


    # strokes(img)



    # for i in range(img.shape[0]):
    #     for j in range(img.shape[1]):
    #         if img[i][j] == False:
    #             ori_x.append(j)
    #             ori_y.append(i)
    # ori_x = np.array(ori_x)
    # ori_y = np.array(ori_y)


    ##############     x,y 曲线
    # poly = np.polyfit(ori_x, ori_y, deg=4)
    # z = np.polyval(poly,ori_x)
    # plt.plot(ori_x, ori_y, 'o')
    # plt.plot(ori_x, z)
    ####################

    #################   ds,x 曲线
    poly = np.polyfit( ori_s,ori_x, deg=7)
    z = np.polyval(poly,ori_s)
    plt.plot(ori_s,ori_x, 'o')
    plt.plot(ori_s, z)
    ################

    #################   ds,y 曲线
    poly = np.polyfit(ori_s, ori_y, deg=7)
    z = np.polyval(poly,ori_s)
    plt.plot(ori_s, ori_y, 'o')
    plt.plot(ori_s, z)
    # #########################

    ####################    参数方程x,y曲线
    poly_x = np.polyfit(ori_s,ori_x, deg = deg)
    z = np.polyval(poly_x,ori_s)
    poly_y = np.polyfit(ori_s, ori_y, deg = deg)
    v = np.polyval(poly_y,ori_s)
    plt.plot(ori_x, ori_y, 'o')
    plt.plot(z, v)
    ##################

    # pixel = 124

    y = np.polyval(poly_y,pixel)
    x = np.polyval(poly_x,pixel)

    # angle = angle_with_horizon(pixel)
    curve = curvature(pixel,0.02,poly_x,poly_y,num)

    # plt.plot(x,y,'x')
    # plt.text(x,y,'{}'.format(angle))
    #
    # plt.plot(ori_x[pixel],ori_y[pixel],'x')
    # plt.text(ori_x[pixel],ori_y[pixel],'{}'.format(angle))
#################################################
    plt.plot(x,y,'x')
    plt.text(x,y,"{}".format(curve))
    plt.text(x+10, y+10, "{}".format(lxl))



    plt.grid()
    plt.gca().set_aspect(1)
    # plt.show()
##############################################
    return curve


