############1.遍历tar的每个笔画段，读取tar.txt，找到笔画段两个端点（端点坐标在point_in_point.npy数组中存的点）在tar.txt中的
# 索引，根据索引找到对应的变换后的坐标，然后找到变换后坐标在src.txt中距离最近的点，并通过这两个最近的点在src_stroke.npy中代表的笔画号，写入
# 对应的图片
import math
import sys

from PIL import Image
import numpy as np
import os

def remove_from_array(base_array, test_array):
    for index in range(len(base_array)):
        if np.array_equal(base_array[index], test_array):
            base_array.pop(index)
            break

def clockwise_angle(v1, v2):
 x1,y1 = v1
 x2,y2 = v2
 dot = x1*x2+y1*y2
 det = x1*y2-y1*x2
 theta = np.arctan2(det, dot)
 theta = theta if theta>0 else 2*np.pi+theta
 theta = theta * 180 / np.pi
 theta = int(theta)
 if theta > 182:
     theta = 360 - theta
 return theta



def ineighbor(img,x,y):
    if img[y][x] == True:
        print("中心点不是黑色像素i")
        print(x,y)
        sys.exit(0)
    i1 = {'img':img[y-1][x],'y+':-1,'x+':0}     # y+和x+是领接点对于中心点的相对坐标
    i2 = {'img':img[y-1][x+1],'y+':-1,'x+':1}
    i3 = {'img':img[y][x+1],'y+':0,'x+':1}
    i4 = {'img':img[y+1][x+1],'y+':1,'x+':1}
    i5 = {'img':img[y+1][x],'y+':1,'x+':0}
    i6 = {'img':img[y+1][x-1],'y+':1,'x+':-1}
    i7 = {'img':img[y][x-1],'y+':0,'x+':-1}
    i8 = {'img':img[y-1][x-1],'y+':-1,'x+':-1}

    inside = [i1,i2,i3,i4,i5,i6,i7,i8]
    inside_b = []
    p = -999     #记录上一个的名字
    u = 1      #记录紧挨的个数
    one = 0      #记录1领域是否有像素
    name = []
    for i in range(8):
        if inside[i]['img'] == False:
            if i == 0:
                one = 1
            a = (inside[i]['y+'],inside[i]['x+'])
            inside_b.append(a)
            if p != -999:
                if i + 1 - p == 1:
                    u = u + 1
            p = i + 1
            name.append(p)
            if (i == 7)and(one == 1):
                u = u + 1
    return inside_b,u,name


def point_class(img,x,y,iso = 0):
    inside,u,name = ineighbor(img,x,y)
    inside = np.array(inside)
    if inside.shape[0] == 0:
        # if iso == 0:
            # print("存在孤点")
            # print(x,y)
            # sys.exit(0)
        return 0
    if inside.shape[0] == 1:  #端点
        return 1
    if (inside.shape[0] == 2)and(u<2):  #一般点
        return 2
    if (inside.shape[0] == 2)and(u==2):
        return 1
    if (inside.shape[0] == 3)and(u<2):
        return 3     #交叉点
    if (inside.shape[0] == 4)and(u<3):
        return 3
    return 2


name = "/扳"
path = r"./image"
tar_txt = np.loadtxt(path + name + "_tar/tar.txt")      #tar笔画段要去对应的对应点原位置
point_in_point = np.load(path + name + "_tar/point_in_point.npy")   #tar笔画段端点里映射的对应点
src_txt = np.loadtxt(path + name + "/src.txt")      #src的对应点
tar_trans_txt = np.loadtxt(path + name + "_tar/tar_trans.txt")      #匹配后的tar的对应点坐标
src_stroke = np.load(path + name + "/src_stroke.npy",allow_pickle=True)      #src对应点和笔画的分配
src_stroke = src_stroke.tolist()
print()

def find_pip(x,y): #找到端点映射的对应点
    yy = point_in_point[y][x][0]
    xx = point_in_point[y][x][1]
    print(point_in_point[y][x][1],point_in_point[y][x][0])
    if xx == 0 and yy == 0:
        print("1.笔画端点未存入!",x,y)
        # sys.exit(0)
    yy = int(yy)
    xx = int(xx)
    return xx,yy

def distance(ori,matched,src,set):  #找到距离最近的src对应点     ori:原本所有关键点     set:每个笔画段的两个端点   matched: tar_trans
    tag = 0
    s = [0,0]
    s[1],s[0] = find_pip(set[1],set[0])
    for i in range(ori.shape[0]):       ##找到索引
        if ori[i][0] == s[1] and ori[i][1] == s[0]:
            tag = 1
            break
    if tag == 0:                   ##通过索引找到转换后的tar坐标
        print("2.未在tar.txt中找到此端点!")
        # sys.exit(0)
    changed_setY = matched[i][1]
    changed_setX = matched[i][0]

    min = 40000
    index = -999
    for i in range(src.shape[0]):      ##通过转换后tar坐标找到最邻近src点索引
        if (changed_setY - src[i][1])**2 + (changed_setX - src[i][0])**2 < min :
            min = (changed_setY - src[i][1])**2 + (changed_setX - src[i][0])**2
            index = i
    return index  ##src中索引



def find_stroke(src_index1,src_index2,src_stroke):  #根据和src对应点的匹配情况，找到匹配的笔画
    # o = []
    #     # # print(src_stroke[src_index1][src_index2])
    #     # if src_index1 == src_index2:
    #     #     print("==")
    #     #     for i in range(src_stroke.shape[0]):
    #     #         if src_stroke[src_index1][i] > 0:
    #     #             o.append(src_stroke[src_index1][i])
    #     # elif src_stroke[src_index1][src_index2] > 0:
    #     #     o.append(src_stroke[src_index1][src_index2])
    #     # else:##################################################################################如没有对应笔画则按照角度划分（暂时没写）
    #     #     print(src_index1,src_index2)
############################################################3
    o = []
    # print(src_stroke[src_index1][src_index2])
    if src_index1 == src_index2:
        print("3.==")
        for i in range(src_stroke[src_index1].__len__()):
            if src_stroke[src_index1][i].__len__() > 0:
                o.append(src_stroke[src_index1][i][0])
    else:
        for i in range(src_stroke[src_index1][src_index2].__len__()):
            o.append(src_stroke[src_index1][src_index2][i])




        # else:  ##################################################################################如没有对应笔画则按照角度划分（暂时没写）
        #     print(src_index1, src_index2)
######################################################################

    return o






max = 0  ##记录笔画个数
for i in range(src_stroke.__len__()):
    for j in range(src_stroke[i].__len__()):
        for r in range(src_stroke[i][j].__len__()):

            if src_stroke[i][j][r] > max:
                max = int(src_stroke[i][j][r])

img = Image.open(path + name + "_tar/stroke/1_1.png")
img = np.array(img)
strokes = []
for i in range(1,max+1):
    stroke = np.ones((img.shape[0], img.shape[1]), bool)
    for q in range(img.shape[0]):
        for m in range(img.shape[1]):
            stroke[q][m] = np.True_
    strokes.append(stroke)


nm = []  #用来存储第一次没有匹配的笔画的对比点
nmimg = []
f = os.listdir(path + name + "_tar/stroke")
for n in f:
    stroke = Image.open(path + name + "_tar/stroke/" + n)
    stroke = np.array(stroke)
    o = (-999, -999)
    num = 0
    ori_points = []
    for y in range(stroke.shape[0]):       ####找两个端点
        for x in range(stroke.shape[1]):
            if stroke[y][x] == False:
                if point_class(stroke, x, y) == 1:
                    o = (y,x)
                    ori_points.append(o)
                    num += 1
                if point_class(stroke, x, y) == 0:
                    o = (y,x)
                    ori_points.append(o)
                    num += 1
            # if num == 2:
            #     break
        # if num == 2:
        #     break
    if num == 0:
        os.remove(path + name + "_tar/stroke/" + n)
        continue

    if num >2: ################################################################解决一个笔画段因一堆像素点聚集产生超过两个端点
        maxlen = 0
        for i in range(ori_points.__len__()):
            for j in range(i+1,ori_points.__len__()):
                if (ori_points[i][0]-ori_points[j][0])**2 + (ori_points[i][1]-ori_points[j][1])**2 >maxlen:
                    ori_two = []
                    ori_two.append(ori_points[i])
                    ori_two.append(ori_points[j])
                    maxlen = (ori_points[i][0]-ori_points[j][0])**2 + (ori_points[i][1]-ori_points[j][1])**2
        ori_points = []
        ori_points.append(ori_two[0])
        ori_points.append(ori_two[1])

    if o == (-999, -999):
        print("存在空笔画段")
    index1 = distance(tar_txt,tar_trans_txt,src_txt,ori_points[0])
    index2 = distance(tar_txt,tar_trans_txt,src_txt,ori_points[1])
    stroke_num = find_stroke(index1,index2,src_stroke)    ##这段笔画段在几个笔画上
    print("4.端点：",ori_points)
    print("5.",stroke_num)
    for i in range(stroke_num.__len__()):
        for y in range(stroke.shape[0]):
            for x in range(stroke.shape[1]):
                if stroke[y][x] == False:
                    strokes[int(stroke_num[i]-1)][y][x] = False
    if stroke_num.__len__() != 0:
        os.remove(path + name + "_tar/stroke/" + n)   ####################
    else:
        nmimg.append(stroke)
        nm.append([index1,index2])



i = 0
tag = 0  #有组合起来的笔画，就从头再遍历
while True:   ############可以优化  ####把未匹配的笔画段重新组合，角度大于130才可以组合，直到剩余的全部不能组合然后匹配
    if i >=nm.__len__()-1:
        break
    j = i + 1
    while True:
        if j>=nm.__len__():
            break
        if nm[i][0] == nm[j][0] and clockwise_angle((src_txt[nm[i][1]][0] - src_txt[nm[i][0]][0],src_txt[nm[i][1]][1] - src_txt[nm[i][0]][1]),(src_txt[nm[j][1]][0] - src_txt[nm[j][0]][0],src_txt[nm[j][1]][1] - src_txt[nm[j][0]][1]))>130:
                nm[j][0] = nm[i][1]
                for y in range(nmimg[i].shape[0]):
                    for x in range(nmimg[i].shape[1]):
                        if nmimg[i][y][x] == False:
                            nmimg[j][y][x] = False
                stroke_num = find_stroke(nm[j][0],nm[j][1],src_stroke)
                for i in range(stroke_num.__len__()):
                    for y in range(nmimg[j].shape[0]):
                        for x in range(nmimg[j].shape[1]):
                            if nmimg[j][y][x] == False:
                                strokes[int(stroke_num[i] - 1)][y][x] = False
                if stroke_num.__len__() != 0:
                    nm.remove(nm[j])
                    # nmimg.remove(nmimg[j].all())
                    remove_from_array(nmimg, nmimg[j])
                nm.remove(nm[i])
                # nmimg.remove(nmimg[i].all())
                remove_from_array(nmimg, nmimg[i])
                tag = 1
                break
        elif nm[i][0] == nm[j][1] and clockwise_angle((src_txt[nm[i][1]][0] - src_txt[nm[i][0]][0],src_txt[nm[i][1]][1] - src_txt[nm[i][0]][1]),(src_txt[nm[j][0]][0] - src_txt[nm[j][1]][0],src_txt[nm[j][0]][1] - src_txt[nm[j][1]][1]))>130:
            nm[j][1] = nm[i][1]
            for y in range(nmimg[i].shape[0]):
                for x in range(nmimg[i].shape[1]):
                    if nmimg[i][y][x] == False:
                        nmimg[j][y][x] = False
            stroke_num = find_stroke(nm[j][0], nm[j][1], src_stroke)
            for i in range(stroke_num.__len__()):
                for y in range(nmimg[j].shape[0]):
                    for x in range(nmimg[j].shape[1]):
                        if nmimg[j][y][x] == False:
                            strokes[int(stroke_num[i] - 1)][y][x] = False
            if stroke_num.__len__() != 0:
                nm.remove(nm[j])
                # nmimg.remove(nmimg[j].all())
                remove_from_array(nmimg, nmimg[j])
            nm.remove(nm[i])
            # nmimg.remove(nmimg[i].all())
            remove_from_array(nmimg, nmimg[i])
            tag = 1
            break
        elif nm[i][1] == nm[j][0] and clockwise_angle((src_txt[nm[i][0]][0] - src_txt[nm[i][1]][0],src_txt[nm[i][0]][1] - src_txt[nm[i][1]][1]),(src_txt[nm[j][1]][0] - src_txt[nm[j][0]][0],src_txt[nm[j][1]][1] - src_txt[nm[j][0]][1]))>130:
            nm[j][0] = nm[i][0]
            for y in range(nmimg[i].shape[0]):
                for x in range(nmimg[i].shape[1]):
                    if nmimg[i][y][x] == False:
                        nmimg[j][y][x] = False
            stroke_num = find_stroke(nm[j][0], nm[j][1], src_stroke)
            for i in range(stroke_num.__len__()):
                for y in range(nmimg[j].shape[0]):
                    for x in range(nmimg[j].shape[1]):
                        if nmimg[j][y][x] == False:
                            strokes[int(stroke_num[i] - 1)][y][x] = False
            if stroke_num.__len__() != 0:
                nm.remove(nm[j])
                # nmimg.remove(nmimg[j].all())
                remove_from_array(nmimg, nmimg[j])
            nm.remove(nm[i])
            # nmimg.remove(nmimg[i].all())
            remove_from_array(nmimg, nmimg[i])
            tag = 1
            break
        elif nm[i][1] == nm[j][1] and clockwise_angle((src_txt[nm[i][0]][0] - src_txt[nm[i][1]][0],src_txt[nm[i][0]][1] - src_txt[nm[i][1]][1]),(src_txt[nm[j][0]][0] - src_txt[nm[j][1]][0],src_txt[nm[j][0]][1] - src_txt[nm[j][1]][1]))>130:
            nm[j][1] = nm[i][0]
            for y in range(nmimg[i].shape[0]):
                for x in range(nmimg[i].shape[1]):
                    if nmimg[i][y][x] == False:
                        nmimg[j][y][x] = False
            stroke_num = find_stroke(nm[j][0], nm[j][1], src_stroke)
            for i in range(stroke_num.__len__()):
                for y in range(nmimg[j].shape[0]):
                    for x in range(nmimg[j].shape[1]):
                        if nmimg[j][y][x] == False:
                            strokes[int(stroke_num[i] - 1)][y][x] = False
            if stroke_num.__len__() != 0:
                nm.remove(nm[j])
                # nmimg.remove(nmimg[j].all())
                remove_from_array(nmimg, nmimg[j])
            nm.remove(nm[i])
            # nmimg.remove(nmimg[i].all())
            remove_from_array(nmimg, nmimg[i])
            tag = 1
            break
        j += 1

    i += 1
    if tag == 1:
        i = 0
        tag = 0
        continue


f = os.listdir(path + name + "_tar/stroke")
for n in f:   ###删除原来的笔画段
    if "_" in n:
        os.remove(path + name + "_tar/stroke/" + n)

times = 1
for i in strokes:
    img = i
    img = Image.fromarray(img)
    img.save(path +  name + "_tar/stroke/{}.png".format(times))
    times += 1
