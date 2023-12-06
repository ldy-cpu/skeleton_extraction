#####由seg_with_harris改动，拐点用最大距离以及harris共同确定，改为用椭圆斜率
#####当前版本

import cv2
import sys
import matplotlib.pyplot as plt
from PIL import Image,ImageFont,ImageDraw
import numpy as np
import os
import math
from polyfit import getcurve


#      o15  o16 o1  o2  o3
#      o14  i8  i1  i2  o4
#      o13  i7  oo  i3  o5
#      o12  i6  i5  i4  o6
#      o11  o10 o9  o8  o7



def thin(s_path):

    print("thin")
    st = Image.open(s_path)
    st = np.array(st)
    for p in range(st.shape[0]):
        for q in range(st.shape[1]):
            if st[p][q] == False:
                a,u,name = ineighbor(st,q,p)
                num = 0
                if (len(name) == 3)and(u==2) :
                    v = []
                    for h in range(3):
                        # print((a[h][0])**2 + (a[h][1])**2)
                        if (a[h][0])**2 + (a[h][1])**2 == 1:
                            v.append(a[h])
                            # print(a[h])
                    if len(v) == 2:
                        if clockwise_angle(v[0],v[1]) == 90:
                            st[p][q] = True
                if (len(name) == 2):
                    if clockwise_angle(a[0],a[1]) == 90:
                        st[p][q] = True
    st = Image.fromarray(st)
    st.save(s_path)


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
     theta = -(360 - theta)
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
    if(inside.shape[0]) == 5 or (inside.shape[0]) == 6:
        return 3
    return 2


def one(x,y,tiny): ##确保对比点周围没有其他对比点
    for i in range(tiny):
        for j in range(tiny):
            for t in range(-1,2):
                for o in range(-1,2):
                    if (matches[y+t*i][x+o*j][0] != 0) or (matches[y+t*i][x+o*j][1] != 0):
                        b = (matches[y+t*i][x+o*j][0],matches[y+t*i][x+o*j][1])
                        return b  ##如果周围有其他对比点，用其他对比点代表此点去对比
    return (0,0)


def traversal(img,x,y,first,stroke,px = -999,py = -999,ppx = -999,ppy = -999):   #pre
    # print("x,y:",x,y)
    for cross_point in cross_points:      #遇到交叉点则截止
        # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
        if cross_point[0] == y and cross_point[1] == x and first == 0:
            # print(x,y)
            stroke.append((y, x))
            return stroke
        if (pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2) == 1)and(pow(cross_point[0] - py,2) + pow((cross_point[1] - px),2) == 1):
            # print(x,y,px,py)
            stroke.append((cross_point[0], cross_point[1]))
            return stroke
    if point_class(img,x,y) == 0:   #瑕疵点
        stroke.append((y,x))
        for cross_point in cross_points:  # 交叉点分配给每个笔画段
            # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
            if (pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 1) or (pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 2):
                # print(x,y,px,py)
                stroke.append((cross_point[0], cross_point[1]))
                return stroke
        return stroke
    ######## 端点
    if point_class(img,x,y) == 1:
    #     o = one(x,y,tiny)
    #     if o == (0,0):
    #         matches[y][x][0] = y
    #         matches[y][x][1] = x
        # else:
        #     if (o[0]-y)**2+(o[1]-x)**2>2:  ######>2说明不是和交叉点相邻的端点
        #         matches[y][x][0] = o[0]   ##存实际代表此点去对比的点
        #         matches[y][x][1] = o[1]

        if first == 0:              #终点
            stroke.append((y,x))
            for cross_point in cross_points:  # 交叉点分配给每个笔画段
                # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
                if (pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 1) or (
                        pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 2):
                    # print(x,y,px,py)
                    stroke.append((cross_point[0], cross_point[1]))
                    return stroke
            return stroke
        else:                         #起点
            a,b,name = ineighbor(img,x,y)
            if b == 1:
                next = (y + a[0][0],x + a[0][1])  #前y,后x
            else:
                for qq in range(len(name)):
                    if (a[qq][0] == 0)or(a[qq][1] == 0):
                        next = (y + a[qq][0],x + a[qq][1])
                        break
            stroke = traversal(img,next[1],next[0],0,stroke,x,y,px,py)
            stroke.append((y,x))
            for cross_point in cross_points:  # 交叉点分配给每个笔画段
                # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
                if (pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 1) or (
                        pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 2):
                    # print(x,y,px,py)
                    stroke.append((cross_point[0], cross_point[1]))
                    return stroke
            return stroke

    ########### 一般点
    if point_class(img,x,y) == 2:
        a,b,name = ineighbor(img,x,y)  #b和name没用
        a = np.array(a)
        next = (-999,-999)
        if a.shape[0] == 2:   #领域为2的一般点
            if (a[0][0] + y == py)and(a[0][1] + x == px):
                next = (y + a[1][0],x + a[1][1])
                stroke = traversal(img,next[1],next[0],0,stroke,x,y,px,py)
                stroke.append((y,x))
                return stroke
            else:
                next = (y + a[0][0],x + a[0][1])
                stroke = traversal(img,next[1],next[0],0,stroke,x,y,px,py)
                stroke.append((y,x))
                return stroke
        else:              #领域为3或4的一般点
            # print("当前点：",x,y)
            # print("8领域：",a.shape[0])
            # print("领域相连个数：",b)
            arrlist = a.tolist()
            for i in range(a.shape[0]):
                if ((a[i][0] == 0)or(a[i][1] == 0))and((a[i][0] + y != py)or(a[i][1] + x != px)):
                    next = (y + a[i][0], x + a[i][1])
                    # print("bug1")
                    break
####################################################################################################################### 有bug
            if next == (-999,-999):
                for i in range(a.shape[0]):
                    if a.shape[0] == 3:

                        if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
                            next = (y + a[i][0], x + a[i][1])
                            # print("bug2")
                            break
                    else:
                        stroke.append((y, x))
                        return stroke
# ###################################################################################################################################
            # print("下一个：",next[1],next[0])
            # if next[0] == -999:
            #     print(a.shape[0])
            #     print(x,y)
            #     sys.exit(0)
            stroke = traversal(img, next[1], next[0], 0, stroke, x, y, px, py)
            stroke.append((y, x))
            return stroke


                ##################################   有bug
            # elif (a[i][0] != 0)and(a[i][1] != 0):
            #     if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
            #         next = (y + a[i][0], x + a[i][1])
            #         stroke = traversal(img, next[1], next[0], 0, stroke, x, y,px,py)
            #         stroke.append((y, x))
            #         return stroke
                # print(not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist))
            # print("???")
                ##################################
    if point_class(img,x,y) == 3:
        a, b, name = ineighbor(img, x, y)
        next = (y + a[0][0], x + a[0][1])
        stroke = traversal(img, next[1], next[0], 0, stroke, x, y, px, py)
        stroke.append((y, x))
        # for cross_point in cross_points:  # 交叉点分配给每个笔画段
        #     # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
        #     if (pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 1) or (
        #             pow(cross_point[0] - y, 2) + pow((cross_point[1] - x), 2) == 2):
        #         # print(x,y,px,py)
        #         stroke.append((cross_point[0], cross_point[1]))
        #         return stroke
        return stroke



    stroke.append((y,x))   #把笔画断裂的那个点作为笔画了
    return stroke




def count(dots,ct,img,x,y,first,px = -999,py = -999):  #记录每个笔画段长度
    if point_class(img,x,y) == 0:
        ct = ct + 1
        ii = (y, x)
        dots.append(ii)
        return dots, ct
    if point_class(img,x,y) == 1:
        if first == 0:              #终点
            ct = ct + 1
            ii = (y,x)
            dots.append(ii)
            return dots,ct
        else:                         #起点
            a,b,name = ineighbor(img,x,y)
            if b == 1:
                next = (y + a[0][0],x + a[0][1])  #前y,后x
            else:
                for qq in range(len(name)):
                    if (a[qq][0] == 0)or(a[qq][1] == 0):
                        next = (y + a[qq][0],x + a[qq][1])
                        break
            ct = ct + 1
            ii = (y, x)
            dots.append(ii)
            dots,ct = count(dots,ct,img,next[1],next[0],0,x,y)
            return dots,ct
    ########### 一般点
    if point_class(img,x,y) == 2:
        a,b,name = ineighbor(img,x,y)  #b和name没用
        a = np.array(a)
        next = (-999,-999)
        if a.shape[0] == 2:   #领域为2的一般点
            if (a[0][0] + y == py)and(a[0][1] + x == px):
                next = (y + a[1][0],x + a[1][1])
                ct = ct + 1
                ii = (y, x)
                dots.append(ii)
                dots, ct = count(dots, ct, img, next[1], next[0], 0, x, y)
                return dots, ct
            else:
                next = (y + a[0][0],x + a[0][1])
                ct = ct + 1
                ii = (y, x)
                dots.append(ii)
                dots, ct = count(dots, ct, img, next[1], next[0], 0, x, y)
                return dots, ct
        else:              #领域为3或4的一般点
            # print("当前点：",x,y)
            # print("8领域：",a.shape[0])
            # print("领域相连个数：",b)
            arrlist = a.tolist()
            for i in range(a.shape[0]):
                if ((a[i][0] == 0)or(a[i][1] == 0))and((a[i][0] + y != py)or(a[i][1] + x != px)):
                    next = (y + a[i][0], x + a[i][1])
                    # print("bug1")
                    break
            if next == (-999,-999):
                for i in range(a.shape[0]):
                    if a.shape[0] == 3:
                        if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
                            next = (y + a[i][0], x + a[i][1])
                            # print("bug2")
                            break
            # print("下一个：",next[1],next[0])
            ct = ct + 1
            ii = (y, x)
            dots.append(ii)
            dots, ct = count(dots, ct, img, next[1], next[0], 0, x, y)
            return dots, ct
    print("仍有交叉点",x,y)

    # ii = (y, x)
    # dots.append(ii)
    # dots, ct = count(dots, ct, img, next[1], next[0], 0, x, y)
    return dots, ct

def combine(s_path):
    f = os.listdir(s_path)
    nnum = 0
    for i in f:
        nnum += 1
        os.rename(s_path + "/" + i, s_path + '/{}.png'.format(nnum))
    print("start combine")
    ww = len(cross_points)
    le = 0
    while le<ww:   #遍历每个交叉点
        cross_point = cross_points[le]
        if cross_point[0] == -999:
            le = le + 1
            continue
        print("交叉点",cross_point[1],cross_point[0])
        f = os.listdir(s_path)
        rela = []
        name = []
        angle_name = []
        small_name = []
        angles = []
        for i in range(1,len(f)+1):   #遍历每个笔画段
            st = Image.open(s_path + "/{}.png".format(i))
            st = np.array(st)
            tag = 0
            for dot in range(-1,2):
                for pot in range(-1,2):
                    if st[cross_point[0] + dot][cross_point[1] + pot] == False:
                        # print(cross_point[0] + dot, cross_point[1] + pot)
                        tag = 1
                        break
                if tag == 1:
                    break
            if tag == 1:
                rela.append(st)
                name.append(i)
                # print(i)
        # print(name)
        for i in range(len(rela)):  #遍历每个与当前交叉点相关的笔画段
            dots = []
            img = rela[i]
            # hh = Image.fromarray(img)
            # hh.save("D:\project\stroke_segmentation\image\TEST\dfaf.png")
            o = (-999, -999)
            for y in range(img.shape[0]):
                for x in range(img.shape[1]):
                    if img[y][x] == False:
                        if (point_class(img, x, y) == 1)or(point_class(img, x, y) == 0):
                            o = (x, y)
                            break
                if x != img.shape[1] - 1:
                    break
            if o[0] == -999:
                continue
            # print(o)
            dots,num = count(dots,0,img,o[0],o[1],1)
            # print("num:",num)

            if num <= tiny:        #改变数值以适应不同交叉点分裂
                small_name.append(name[i])  #单独记录小于阈值长度的，以便于与所有大于4长度的笔画段相接

            elif num < angle_judge:
                if (pow(o[0]-cross_point[1],2)+pow(o[1]-cross_point[0],2)>2):
                    angles.append(dots[0])   #记录本笔画段对应计算角度的像素坐标,从远离交叉点的地方开始存的,所以取第一个元素
                    angle_name.append(name[i])   #记录本笔画段的文件名
                else:
                    angles.append(dots[num-1])   #从靠近交叉点的地方开始存的,所以取第一个元素
                    angle_name.append(name[i])
            else:
                if (pow(o[0] - cross_point[1], 2) + pow(o[1] - cross_point[0], 2) > 2):
                    for re in range(len(dots)):
                        if dots[re][0] == cross_point[0] and dots[re][1] == cross_point[1]:
                            break
                    if re >= angle_judge - 1:
                        angles.append(dots[re-angle_judge + 1])          #记录本笔画段对应计算角度的像素坐标,同上
                        angle_name.append(name[i])     #记录本笔画段对应计算角度的像素坐标#记录本笔画段的文件名
                    else:
                        angles.append(dots[0])
                        angle_name.append(name[i])
                else:
                    angles.append(dots[angle_judge - 1])
                    angle_name.append(name[i])

        ms = []         #角度最大的向量组  两两成对

        for tt in range(5):     # 5没有什么意义
            max = 0  # 最大的角度
            m1 = -999
            m2 = -999
            for yi in range(len(angle_name)):
                if not(angle_name[yi] in ms):
                    for er in range(len(angle_name)):
                        if not(angle_name[er] in ms):
                            theta = clockwise_angle((angles[yi][0] - cross_point[0],angles[yi][1] - cross_point[1]),(angles[er][0] - cross_point[0],angles[er][1] - cross_point[1]))
                            # print(angles[yi])
                            # print((angles[yi][1],angles[yi][0]),(angles[er][1] ,angles[er][0]))
                            # print(theta)
                            if theta >= angle:   ##angle 为全局变量
                                if theta > max:
                                    max = theta
                                    m1 = angle_name[yi]
                                    m2 = angle_name[er]
            # print(max)
            if m1 != -999:
                ms.append(m1)
                ms.append(m2)
        print(ms)
        if len(small_name) == 1 :
            for rr in range(len(name)):
                new_stroke = rela[rr]
                for gg in range(len(small_name)):
                    small_stroke = rela[name.index(small_name[gg])]
                    for pp in range(small_stroke.shape[0]):
                        for qq in range(small_stroke.shape[1]):
                            if small_stroke[pp][qq] == False:
                                new_stroke[pp][qq] = False
                    new_stroke[cross_point[0]][cross_point[1]] = False
                    news = Image.fromarray(new_stroke)
                    news.save(s_path + "/{}.png".format(name[rr]))
            for gg in range(len(small_name)):
                white = np.ones((img.shape[0], img.shape[1]), bool)
                white = Image.fromarray(white)
                white.save(s_path + "/{}.png".format(small_name[gg]))
                # os.remove(s_path + "/{}.png".format(rela[small_name[gg]]))
                # print("delete small")
        elif len(small_name) > 1:
            cross_points.remove(cross_point)
            cross_points.append(cross_point)
            continue
        else:
            if len(ms) > 0:
                j = 0
                uu = len(ms)/2
                uu = int(uu)
                for i in range(uu):
                    new_stroke = rela[name.index(ms[j])]
                    old_stroke = rela[name.index(ms[j+1])]
                    for pp in range(new_stroke.shape[0]):
                        for qq in range(new_stroke.shape[1]):
                            if old_stroke[pp][qq] == False:
                                new_stroke[pp][qq] = False
                    white = np.ones((img.shape[0],img.shape[1]),bool)
                    white = Image.fromarray(white)
                    white.save(s_path + "/{}.png".format(ms[j+1]))
                    # os.remove(s_path + "/{}.png".format(angle_name[j+1]))
                    # print("delete angle2")
                    new_stroke[cross_point[0]][cross_point[1]] = False
                    news = Image.fromarray(new_stroke)
                    news.save(s_path + "/{}.png".format(ms[j]))
                    # print("save")
                    j = j + 2





        for near in range(len(cross_points)):##如果两交叉点紧挨，则失效一个交叉点
            if (cross_points[near][0] - cross_point[0])**2 + (cross_points[near][1] - cross_point[1])**2 == 1 or (cross_points[near][0] - cross_point[0])**2 + (cross_points[near][1] - cross_point[1])**2 == 2:
                cross_points[near] = (-999,-999)
        le = le + 1
    print("combine done!")
    return 0



n = 1


def circle(img,x,y,start_x,start_y,stroke,px = -999,py = -999): #### 处理无交叉点的真正意义上的封闭笔画   只针对去冗余的骨架
    a,b,name = ineighbor(img,x,y)
    next = (-999,-999)
    a = np.array(a)
    if a.shape[0] == 2:
        if (not px == x + a[0][1]) or (not py == y + a[0][0]):
            next = (y + a[0][0],x + a[0][1])
        else:
            next = (y + a[1][0],x + a[1][1])
    else:
        for i in range(a.shape[0]):
            if ((a[i][0] == 0) or (a[i][1] == 0)) and ((a[i][0] + y != py) or (a[i][1] + x != px)):
                next = (y + a[i][0], x + a[i][1])
                # print("bug1")
                break
        ####################################################################################################################### 有bug
        if next == (-999, -999):
            a1 = (-999,-999)
            for i in range(a.shape[0]):
                if a[i][0] == 0 or a[i][1] == 0:
                    a1 = a[i]
                    # print("有正对的且是pre")
                    break
            for i in range(a.shape[0]):
                if (a[i][0] - a1[0])**2 + (a[i][1] - a1[1])**2 >1 and (a[i][0] - a1[0])**2 + (a[i][1] - a1[1])**2<10:
                    # print((a[i][0] - a1[0])**2 + (a[i][1] - a1[1])**2)
                    # print(x,y)
                    # print(a.shape[0])
                    next = (y + a[i][0], x + a[i][1])
                    break
        if next == (-999,-999):
            print("next还等于-999")


    if next[0] == start_y and next[1] == start_x:
        stroke.append((y,x))
        return stroke
    else:
        stroke = circle(img, next[1], next[0], start_x, start_y, stroke, x, y)
        stroke.append((y, x))
        return stroke



def strokes(img,spath):
    o = (-999,-999)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y][x] == False:
                if point_class(img,x,y) == 1:
                    o = (x,y)
                    break
                if point_class(img,x,y) == 0:
                    o = (x, y)
                    break
                if point_class(img,x,y) == 3:
                    o = (x,y)
                    break
        if x !=img.shape[1]-1:
            break
    global n

    if o == (-999, -999):
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                if img[y][x] == False:
                    o = (x,y)
                    print(o)
                    stroke = []
                    stroke = circle(img,o[0],o[1],o[0],o[1],stroke)
                    white_pic = np.ones((img.shape[0], img.shape[1]), bool)
                    for q in range(img.shape[0]):
                        for m in range(img.shape[1]):
                            white_pic[q][m] = np.True_
                    for dot in stroke:
                        white_pic[dot[0]][dot[1]] = False
                    white_pic = Image.fromarray(white_pic)
                    # path = r"D:/project/stroke_segmentation/image/完美骨架"
                    if not os.path.exists(spath):
                        os.mkdir(spath)
                    # if not os.path.exists(path + "/remain"):
                    #     os.mkdir(path + "/remain")
                    white_pic.save(spath + "/{}.png".format(n))
                    for dot in stroke:
                        img[dot[0]][dot[1]] = True
                    # test_img = Image.fromarray(img)
                    # test_img.save(path + "/remain/{}.png".format(n))
                    n = n + 1
                    # print(n)
                    strokes(img, spath)
                    return 0


    if o == (-999,-999):
        # print(img)
        # img = Image.fromarray(img)
        # img.save(spath + "/{}_last.png".format(n))
        print("segmentation done!")
        return 0
    first = 1
    stroke = []
    stroke = traversal(img,o[0],o[1],first,stroke)
    white_pic = np.ones((img.shape[0],img.shape[1]),bool)
    for q in range(img.shape[0]):
        for m in range(img.shape[1]):
            white_pic[q][m] = np.True_
    for dot in stroke:
        white_pic[dot[0]][dot[1]] = False
    # ###########
    # plt.imshow(img)
    # plt.axis('off')
    # plt.show()
    # ###########
    # #############
    # plt.imshow(white_pic)
    # plt.axis('off')
    # plt.show()
    # ################
    white_pic = Image.fromarray(white_pic)
    # path = r"D:/project/stroke_segmentation/image/test"
    # if not os.path.exists(path + "/stroke"):
    #     os.mkdir(path + "/stroke")
    # if not os.path.exists(path + "/remain"):
    #     os.mkdir(path + "/remain")

    white_pic.save(spath+"/{}.png".format(n))
    for dot in stroke:
        img[dot[0]][dot[1]] = True
    # test_img = Image.fromarray(img)
    # test_img.save(path + "/remain/{}.png".format(n))
    n = n + 1
    # print(n)
    strokes(img,spath)

    return 0



def get_cross(img):
    for p in range(img.shape[0]):
        for q in range(img.shape[1]):
            if img[p][q] == False:
                if point_class(img, q, p) == 3:
                    print("当前交叉点",q,p)
                    # tag = 0
                    # for near in range(len(cross_points)):
                    #     if pow((cross_points[near][0]-p),2) + pow((cross_points[near][1]-q),2) <= 2:
                    #         tag = 1
                    #         break
                    # if tag == 0:
                    cross_points.append((p, q))  # 记录交叉点
                    o = one(q, p, tiny)
                    if o == (0, 0):
                        matches[p][q][0] = p
                        matches[p][q][1] = q
                    else:
                        matches[p][q][0] = o[0]  ##存实际代表此点去对比的点
                        matches[p][q][1] = o[1]
    return 0


def get_end(img):
    for p in range(img.shape[0]):
        for q in range(img.shape[1]):
            if img[p][q] == False:
                if point_class(img, q, p) == 1:
                    print("当前端点",q,p)
                    # tag = 0
                    # for near in range(len(cross_points)):
                    #     if pow((cross_points[near][0]-p),2) + pow((cross_points[near][1]-q),2) <= 2:
                    #         tag = 1
                    #         break
                    # if tag == 0:
                    # o = one(q, p, tiny)

                    end[p][q][0] = p
                    end[p][q][1] = q



def del_stin(img,stin_len):
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y][x] == False:
                if point_class(img,x,y) == 1:
                    stins = []
                    stins = traversal(img,x,y,1,stins)
                    if len(stins)<=stin_len:
                        tag = 0
                        ll = 0
                        o = len(stins)
                        for i in range(o):
                            for cross_point in cross_points:
                                if (cross_point[0] == stins[ll][0])and(cross_point[1] == stins[ll][1]):
                                    tag = 1
                                    print("删除\n",stins[ll])
                                    stins.remove(stins[ll])
                                    ll = ll - 1
                                    break
                            ll = ll + 1
                        if tag == 1:
                            for j in range(len(stins)):
                                print(stins[j])
                                img[stins[j][0]][stins[j][1]] = True
    return img




def get_distance_point2line(point, line):
    """
    Args:
        point: [x0, y0]
        line: [x1, y1, x2, y2]
    """
    line_point1, line_point2 = np.array(line[0:2]), np.array(line[2:])
    vec1 = line_point1 - point
    vec2 = line_point2 - point
    distance = np.abs(np.cross(vec1, vec2)) / np.linalg.norm(line_point1 - line_point2)
    return distance



def del_white(d_path):
    f = os.listdir(d_path)
    for i in f:
        pic = Image.open(d_path + "/" + i)
        pic = np.array(pic)
        tag = 0
        for p in range(pic.shape[0]):
            for q in range(pic.shape[1]):
                if pic[p][q] == False:
                    tag = 1
                    break
            if tag == 1:
                break
        if tag == 0:
            os.remove(d_path + "/" + i)
    return 0


def e_(point,line_point1,line_point2):  ### 求椭圆离心率
    a = (math.sqrt((point[0] - line_point1[0])**2 + (point[1] - line_point1[1])**2) + math.sqrt((point[0] - line_point2[0])**2 + (point[1] - line_point2[1])**2))/2
    c = math.sqrt((line_point1[0] - line_point2[0])**2+(line_point1[1] - line_point2[1])**2)/2
    e = c/a
    return e


# def find_maxdis(img,line_point1,ling_point2):
#     maxset = (-999,-999)
#     max = 0
#     p3 = ling_point2-line_point1
#     two_point_dis = math.hypot(p3[0],p3[1])  ##两端点距离
#
#
#     for y in range(img.shape[0]):
#         for x in range(img.shape[1]):
#             if img[y][x] == False:
#                 distans = dis(np.array([y,x]),line_point1,ling_point2)
#                 if distans>max:
#                     max = distans
#                     maxset = (y,x)
#
#     thr =  ## 设置最大距离阈值与两点距离关系
#     if max >= thr:
#         matches[maxset[0]][maxset[1]][0] = maxset[0]
#         matches[maxset[0]][maxset[1]][1] = maxset[1]
#
#         return True   ########有拐点
#     else:
#         return False  ########## 无拐点了


def find_min_e(img,line_point1,line_point2):   ########## 求椭圆离心率
    closeset = (-999,-999)
    if (line_point1[0] == line_point2[0] and line_point1[1] == line_point2[1]):
        farest = 0
        farest_set = (-999,-999)
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                if img[y][x] == False:
                    if (line_point1[0] - y)**2+(line_point1[1] - x)**2>farest:
                        farest = (line_point1[0] - y)**2+(line_point1[1] - x)**2
                        farest_set = (y,x)
        L_[farest_set[0]][farest_set[1]][0] = farest_set[0]
        L_[farest_set[0]][farest_set[1]][1] = farest_set[1]
        print("增加拐点：",farest_set[1],farest_set[0])
        return True,farest_set


    minset = (-999,-999)
    min = 1



    cross1 = [-999,-999]
    near1 = 9999
    cross2 = [-999, -999]
    near2 = 9999
    not_use = [-999,-999]
    centrol_cross = [-999,-999]
    centrol_near = 9999
    # for y in range(img.shape[0]):  ################ 找到穿插在两端点连线之间的点
    #     for x in range(img.shape[1]):
    #         if img[y][x] == False:
    #             angel2 = clockwise_angle((y-line_point2[0],x-line_point2[1]),(line_point1[0]-line_point2[0],line_point1[1]-line_point2[1]))
    #             angel2 = math.fabs(angel2-90)
    #             angel1 = clockwise_angle((y - line_point1[0], x - line_point1[1]),
    #                                      (line_point2[0] - line_point1[0], line_point2[1] - line_point1[1]))
    #             angel1 = math.fabs(angel1 - 90)
    #             dis1 = math.hypot(line_point1[0]-y,line_point1[1]-x)    ## 1端点到此点距离
    #             dis2 = math.hypot(line_point2[0]-y,line_point2[1]-x)   ## 2 .。。
    #             global non_L_dis
    #             if angel1 > 85 and angel2 > 85  and  dis1>10 and dis2>10 and near1>dis1:    ## 越接近90 越平
    #                 cross1 = [y,x]
    #                 near1 = dis1
    #
    #             if angel1 > 85 and angel2 > 85  and dis2>10 and dis1 > 10 and near2 > dis2:  ## 越接近90 越平
    #                 cross2 = [y, x]
    #                 near2 = dis2

    for y in range(img.shape[0]):  ################ 找到穿插在两端点连线之间的点
        for x in range(img.shape[1]):
            if img[y][x] == False:
                angel2 = clockwise_angle((y-line_point2[0],x-line_point2[1]),(line_point1[0]-line_point2[0],line_point1[1]-line_point2[1]))
                angel2 = math.fabs(angel2-90)
                angel1 = clockwise_angle((y - line_point1[0], x - line_point1[1]),
                                         (line_point2[0] - line_point1[0], line_point2[1] - line_point1[1]))
                angel1 = math.fabs(angel1 - 90)
                dis1 = math.hypot(line_point1[0]-y,line_point1[1]-x)    ## 1端点到此点距离
                dis2 = math.hypot(line_point2[0]-y,line_point2[1]-x)   ## 2 .。。
                centrol_dis = math.hypot((line_point1[0]+line_point2[0])/2-y,(line_point1[1]+line_point2[1])/2-x)
                global non_L_dis
                if angel1 > 88 and angel2 > 88  and  dis1>10 and dis2>10 and centrol_near>centrol_dis:    ## 越接近90 越平
                    centrol_cross = [y,x]
                    centrol_near = centrol_dis
                    print(centrol_cross)


    # if near1 == 9999 and near2 == 9999:   ### 如果不计算穿插点
    #     for y in range(img.shape[0]):
    #         for x in range(img.shape[1]):
    #             if img[y][x] == False:
    #                 e = e_(np.array([y, x]), line_point1, line_point2)
    #                 if e < min:
    #                     min = e
    #                     minset = (y, x)
###################################################################################################################################################
    # if near1 == 9999 and near2 == 9999:   ### 如果不计算穿插点
    #     now = line_point1
    #     pre = [-999,-999]
    #     next = [-999,-999]
    #     cross = line_point2    ## 只是为了和后面的while循环一致，把line_point2命名成cross
    #     start = line_point1
    #
    #
    # else:    ### 计算穿插点
    #     if near1 == 9999:    ### near2 != 9999,所以用cross2 和 line_point2 作为焦点
    #         now = line_point2
    #         pre = [-999,-999]
    #         next = [-999,-999]
    #         cross = cross2
    #         start = line_point2
    #         not_use = line_point1
    #     elif near2 == 9999:
    #         now = line_point1
    #         pre = [-999, -999]
    #         next = [-999, -999]
    #         cross = cross1
    #         start = line_point1
    #         not_use = line_point2
    #     elif near1 > near2:
    #         now = line_point1
    #         pre = [-999, -999]
    #         next = [-999, -999]
    #         cross = cross1
    #         start = line_point1
    #         not_use = line_point2
    #     else:
    #         now = line_point2
    #         pre = [-999, -999]
    #         next = [-999, -999]
    #         cross = cross2
    #         start = line_point2
    #         not_use = line_point1
#################################################################################################################################
    if centrol_near == 9999:   ### 如果不计算穿插点
        now = line_point1
        pre = [-999,-999]
        next = [-999,-999]
        cross = line_point2    ## 只是为了和后面的while循环一致，把line_point2命名成cross
        start = line_point1


    else:    ### 计算穿插点

        now = line_point2
        pre = [-999, -999]
        next = [-999, -999]
        cross = centrol_cross
        start = line_point2
        not_use = line_point1
##########################################################################################################################
    num = 0
    ori_ds = []
    ori_x = []
    ori_y = []
    # angle_with_horizon = []   ##保存每两个像素与水平线的夹角
    pixel = []
    minnum = 0
    min = 1
    while True:                 ### 顺着笔画找e最小的，找到cross点则停止
        x = now[1]
        y = now[0]
        px = pre[1]
        py = pre[0]
        if (now[0] == line_point2[0] and now[1] == line_point2[1])or(now[0] == line_point1[0] and now[1] == line_point1[1]):
            a, b, name = ineighbor(img, x, y)
            if b == 1:
                next = [y + a[0][0], x + a[0][1]]  # 前y,后x
            else:
                for qq in range(len(name)):
                    if (a[qq][0] == 0) or (a[qq][1] == 0):
                        next = [y + a[qq][0], x + a[qq][1]]
                        break
        else:
            a, b, name = ineighbor(img, x, y)  # b和name没用
            a = np.array(a)
            next = [-999, -999]
            if a.shape[0] == 2:  # 领域为2的一般点
                if (a[0][0] + y == py) and (a[0][1] + x == px):
                    next = [y + a[1][0], x + a[1][1]]
                else:
                    next = [y + a[0][0], x + a[0][1]]
            else:  # 领域为3或4的一般点
                # print("当前点：",x,y)
                # print("8领域：",a.shape[0])
                # print("领域相连个数：",b)
                arrlist = a.tolist()
                for i in range(a.shape[0]):
                    if ((a[i][0] == 0) or (a[i][1] == 0)) and ((a[i][0] + y != py) or (a[i][1] + x != px)):
                        next = [y + a[i][0], x + a[i][1]]
                        # print("bug1")
                        break
                if next[0] == -999:
                    for i in range(a.shape[0]):
                        if a.shape[0] == 3:
                            if (not ([a[i][0] + 1, a[i][1]] in arrlist)) and (
                            not ([a[i][0] - 1, a[i][1]] in arrlist)) and (
                            not ([a[i][0], a[i][1] + 1] in arrlist)) and (not ([a[i][0], a[i][1] - 1] in arrlist)):
                                next = [y + a[i][0], x + a[i][1]]
                                # print("bug2")
                                break

        e = e_(now,start,cross)
        # print("e:",e)
        if e < min:
            minnum = num
            min = e
            minset = (y, x)
        # angle = clockwise_angle((next[0]-now[0],next[1]-now[1]),(now[0]-pre[0],now[1]-pre[1]))
        # pixel.append(num)
        # if num == 0:
        #     angleadd = 0
        #     angle_with_horizon.append(angleadd)
        # else:
        #     angleadd = 0.9*angleadd + 0.1*angle
        #     angle_with_horizon.append(angleadd)
        #     # angle_with_horizon.append(angle)
        ori_ds.append(num)
        ori_x.append(x)
        ori_y.append(y)
        num += 1
        pixel.append((y,x))
        if next[0] == cross[0] and next[1] == cross[1]:
            ori_ds.append(num)
            ori_x.append(cross[1])
            ori_y.append(cross[0])
            pixel.append((cross[0],cross[1]))
            break
        pre = now
        now = next





    # for y in range(img.shape[0]):
    #     for x in range(img.shape[1]):
    #         if img[y][x] == False:
    #             e = e_(np.array([y,x]),line_point1,line_point2)
    #             if e<min:
    #                 min = e
    #                 minset = (y,x)

    # else:
    #     print(angel1,angel2)
    #     print(cross1)
    #     for y in range(img.shape[0]):
    #         for x in range(img.shape[1]):
    #             if img[y][x] == False:
    #                 if angel1 <= angel2:
    #                     e = e_(np.array([y,x]),line_point1,cross1)
    #                 else:
    #                     e = e_(np.array([y, x]), line_point2, cross2)
    #                 if e<min:
    #                     min = e
    #                     minset = (y,x)

    # global non_L_dis  ####  设置的多少距离之内则不会有拐点

    global thr1,thr2 ## 设置最大离心率阈值
    # global percent
    print("拟拐点坐标:",pixel[minnum])

    # L_dis = get_distance_point2line(np.array([pixel[minnum][0], pixel[minnum][1]]),
    #                                 np.array([start[0], start[1], cross[0], cross[1]]))  ###拟拐点距离两焦点所确定直线的距离

    # per = num // percent     ####   距离差比例判断是否拐点
    # if minnum - per > 0:
    #     prepix = pixel[minnum - per]  ###按比例找到拟拐点前面的点
    # else:
    #     prepix = pixel[0]
    # if minnum + per <= num:
    #     nextpix = pixel[minnum + per]  ###按比例找到拟拐点后面的点
    # else:
    #     nextpix = pixel[num]

    # dis_minus = math.fabs(L_dis - get_distance_point2line(np.array([prepix[0], prepix[1]]), np.array(
    #     [start[0], start[1], cross[0], cross[1]]))) + math.fabs(L_dis - get_distance_point2line(np.array([nextpix[0], nextpix[1]]),
    #                                                                                  np.array(
    #                                                                                      [start[0], start[1], cross[0],
    #                                                                                       cross[1]])))
    # ###拟拐点距离减去两边一定距离的点到直线距离，做和
    # dis_per = dis_minus / L_dis  ### 做的差的和所占拟拐点到直线距离的比例
    # print("拟拐点比例:", dis_per)
    # global dis_per_thr
    tag = False
    if min <= thr1:

        curve = getcurve(ori_ds,ori_x,ori_y,minnum,num,min)

        if curve > curve_thr:
            tag = True
        if min<=thr2:     ##  如果椭圆已经鼓到某个程度，则无需管曲率，直接算作拐点
            tag = True




    if num > non_L_dis and tag:


        L_[minset[0]][minset[1]][0] = minset[0]
        L_[minset[0]][minset[1]][1] = minset[1]
        # print("拐点....................:",minset)
        # # sub_axix = filter(lambda x: x % 200 == 0, x_axix)
        # plt.title('{}'.format(n))
        # plt.plot(pixel, angle_with_horizon, color='blue', label='angle')
        # plt.legend()  # 显示图例
        #
        # plt.xlabel('pixel')
        # plt.ylabel('angle')
        # plt.show()

        return True,closeset   ########有拐点
    else:
        minset = (-999, -999)
        min = 1
        if not_use[0] == -999:
            return False,closeset
        start = not_use
        now = start
        pre = [-999, -999]
        next = [-999, -999]
        num = 0
        # angle_with_horizon = []   ##保存每两个像素与水平线的夹角
        pixel = []
        ori_ds = []
        ori_x = []
        ori_y = []
        while True:  ### 顺着笔画找e最小的，找到cross点则停止
            x = now[1]
            y = now[0]
            px = pre[1]
            py = pre[0]
            if (now[0] == line_point2[0] and now[1] == line_point2[1]) or (
                    now[0] == line_point1[0] and now[1] == line_point1[1]):
                a, b, name = ineighbor(img, x, y)
                if b == 1:
                    next = [y + a[0][0], x + a[0][1]]  # 前y,后x
                else:
                    for qq in range(len(name)):
                        if (a[qq][0] == 0) or (a[qq][1] == 0):
                            next = [y + a[qq][0], x + a[qq][1]]
                            break
            else:
                a, b, name = ineighbor(img, x, y)  # b和name没用
                a = np.array(a)
                next = [-999, -999]
                if a.shape[0] == 2:  # 领域为2的一般点
                    if (a[0][0] + y == py) and (a[0][1] + x == px):
                        next = [y + a[1][0], x + a[1][1]]
                    else:
                        next = [y + a[0][0], x + a[0][1]]
                else:  # 领域为3或4的一般点
                    # print("当前点：",x,y)
                    # print("8领域：",a.shape[0])
                    # print("领域相连个数：",b)
                    arrlist = a.tolist()
                    for i in range(a.shape[0]):
                        if ((a[i][0] == 0) or (a[i][1] == 0)) and ((a[i][0] + y != py) or (a[i][1] + x != px)):
                            next = [y + a[i][0], x + a[i][1]]
                            # print("bug1")
                            break
                    if next[0] == -999:
                        for i in range(a.shape[0]):
                            if a.shape[0] == 3:
                                if (not ([a[i][0] + 1, a[i][1]] in arrlist)) and (
                                        not ([a[i][0] - 1, a[i][1]] in arrlist)) and (
                                        not ([a[i][0], a[i][1] + 1] in arrlist)) and (
                                not ([a[i][0], a[i][1] - 1] in arrlist)):
                                    next = [y + a[i][0], x + a[i][1]]
                                    # print("bug2")
                                    break

            e = e_(now, start, cross)
            if e < min:
                minnum = num
                min = e
                minset = (y, x)
            # angle = clockwise_angle((next[0]-now[0],next[1]-now[1]),(now[0]-pre[0],now[1]-pre[1]))
            # pixel.append(num)
            # if num == 0:
            #     angleadd = 0
            #     angle_with_horizon.append(angleadd)
            # else:
            #     angleadd = 0.9*angleadd + 0.1*angle
            #     angle_with_horizon.append(angleadd)
            #     # angle_with_horizon.append(angle)
            ori_ds.append(num)
            ori_x.append(x)
            ori_y.append(y)
            num += 1
            pixel.append((y, x))
            if next[0] == cross[0] and next[1] == cross[1]:
                pixel.append((cross[0], cross[1]))
                ori_ds.append(num)
                ori_x.append(cross[1])
                ori_y.append(cross[0])
                break
            pre = now
            now = next

        # for y in range(img.shape[0]):
        #     for x in range(img.shape[1]):
        #         if img[y][x] == False:
        #             e = e_(np.array([y,x]),line_point1,line_point2)
        #             if e<min:
        #                 min = e
        #                 minset = (y,x)

        # else:
        #     print(angel1,angel2)
        #     print(cross1)
        #     for y in range(img.shape[0]):
        #         for x in range(img.shape[1]):
        #             if img[y][x] == False:
        #                 if angel1 <= angel2:
        #                     e = e_(np.array([y,x]),line_point1,cross1)
        #                 else:
        #                     e = e_(np.array([y, x]), line_point2, cross2)
        #                 if e<min:
        #                     min = e
        #                     minset = (y,x)

        # global non_L_dis  ####  设置的多少距离之内则不会有拐点
        if num < non_L_dis:
            return False,closeset
        # print("min2:", min)
        if min <= thr1:
            # L_dis = get_distance_point2line(np.array([pixel[minnum][0], pixel[minnum][1]]),
            #                                 np.array([start[0], start[1], cross[0], cross[1]]))  ###拟拐点距离两焦点所确定直线的距离
            # per = num // percent
            # if minnum - per > 0:
            #     prepix = pixel[minnum - per]  ###按比例找到拟拐点前面的点
            # else:
            #     prepix = pixel[0]
            # if minnum + per <= num:
            #     nextpix = pixel[minnum + per]  ###按比例找到拟拐点后面的点
            # else:
            #     nextpix = pixel[num]
            #
            # dis_minus = math.fabs(L_dis - get_distance_point2line(np.array([prepix[0], prepix[1]]), np.array(
            #     [start[0], start[1], cross[0], cross[1]]))) + math.fabs(
            #     L_dis - get_distance_point2line(np.array([nextpix[0], nextpix[1]]),
            #                                     np.array(
            #                                         [start[0], start[1], cross[0],
            #                                          cross[1]])))
            # ###拟拐点距离减去两边一定距离的点到直线距离，做和
            # dis_per = dis_minus / L_dis  ### 做的差的和所占拟拐点到直线距离的比例
            # global dis_per_thr
            curve = getcurve(ori_ds,ori_x,ori_y,minnum,num,min)# min 是此点离心率
            if min >= thr2:

                # print("dis_per:",dis_per)
                if curve < curve_thr:
                    return False,closeset
            print("拟拐点坐标:", pixel[minnum])

            L_[minset[0]][minset[1]][0] = minset[0]
            L_[minset[0]][minset[1]][1] = minset[1]
            print("拐点....................:", minset)
            # # sub_axix = filter(lambda x: x % 200 == 0, x_axix)
            # plt.title('{}'.format(n))
            # plt.plot(pixel, angle_with_horizon, color='blue', label='angle')
            # plt.legend()  # 显示图例
            #
            # plt.xlabel('pixel')
            # plt.ylabel('angle')
            # plt.show()

            return True,closeset  ########有拐点
        else:
            return False,closeset

def dis_traversal(spath,img,x,y,first,stroke,px = -999,py = -999,tagg = []):

    # print("matches[y][x][0] != 0:", matches[y][x][0] != 0)
    # print("matches[y][x][1] != 0:", matches[y][x][1] != 0)
    # print("point_class(img,x,y) == 1:", point_class(img, x, y) == 1)
    if first == 0 and ((L_[y][x][0] != 0 or L_[y][x][1] != 0)or point_class(img,x,y) == 1):
        print("should cut:")

        stroke.append((y,x))
        # print("b", x, y)
        white_pic = np.ones((img.shape[0], img.shape[1]), bool)
        for q in range(img.shape[0]):
            for m in range(img.shape[1]):
                white_pic[q][m] = np.True_
        for dot in stroke:
            white_pic[dot[0]][dot[1]] = False
            # img[dot[0]][dot[1]] = True

        white_pic = Image.fromarray(white_pic)
        # path = r"D:/project/stroke_segmentation/image/test"
        global n
        n += 1
        white_pic.save(spath + "/{}.png".format(n))
        print("save" , n)

        white_pic = img
        for dot in stroke:
            white_pic[dot[0]][dot[1]] = True
            # img[dot[0]][dot[1]] = True
        white_pic[y][x] = False

        white_pic = Image.fromarray(white_pic)
        # path = r"D:/project/stroke_segmentation/image/test"
        n += 1
        white_pic.save(spath + "/{}.png".format(n))
        print("save", n)
        # stroke = []
        # if point_class(img,x,y) == 2:
        #     dis_traversal(spath,img,x,y,1,stroke,px,py)
        return 0


    if point_class(img,x,y) == 1:
                      #起点
        stroke.append((y, x))
        # print("c", x, y)

        a,b,name = ineighbor(img,x,y)
        if b == 1:
            next = (y + a[0][0],x + a[0][1])  #前y,后x
        else:
            for qq in range(len(name)):
                if (a[qq][0] == 0)or(a[qq][1] == 0):
                    next = (y + a[qq][0],x + a[qq][1])
                    break
        stroke.append((y, x))
        # print("d", x, y)
        dis_traversal(spath,img,next[1],next[0],0,stroke,x,y,[])
        return 0


    ########### 一般点
    if point_class(img,x,y) == 2:


        # if (x,y) in tagg:  ###  处理闭合笔画的
        #     print("真闭合.....................................")
        #     return  0
        # tagg.append((x,y))
        a,b,name = ineighbor(img,x,y)  #b和name没用
        a = np.array(a)
        next = (-999,-999)

        if first == 1:  ## 闭合笔画的起始点
            for h in range(a.shape[0]):
                if a[h][0] == 0 or a[h][1] == 0:
                    next = (y + a[h][0],x + a[h][1])
            if next == (-999,-999):
                next = (y + a[0][0],x + a[0][1])
            stroke.append((y, x))
            # print("e", x, y)
            dis_traversal(spath, img, next[1], next[0], 0, stroke, x, y, tagg)
            return 0

        if a.shape[0] == 2:   #领域为2的一般点
            if (a[0][0] + y == py)and(a[0][1] + x == px):
                next = (y + a[1][0],x + a[1][1])
                stroke.append((y, x))
                # print("e", x, y)
                dis_traversal(spath,img,next[1],next[0],0,stroke,x,y,tagg)
                return 0
            else:
                next = (y + a[0][0],x + a[0][1])
                stroke.append((y, x))
                # print("f", x, y)
                dis_traversal(spath,img,next[1],next[0],0,stroke,x,y,tagg)
                return 0
        else:              #领域为3或4的一般点
            # print("当前点：",x,y)
            # print("8领域：",a.shape[0])
            # print("领域相连个数：",b)
            arrlist = a.tolist()
            for i in range(a.shape[0]):
                if ((a[i][0] == 0)or(a[i][1] == 0))and((a[i][0] + y != py)or(a[i][1] + x != px)):
                    next = (y + a[i][0], x + a[i][1])
                    # print("bug1")
                    break
            if next == (-999,-999):
                for i in range(a.shape[0]):
                    if a.shape[0] == 3:
                        if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
                            next = (y + a[i][0], x + a[i][1])
                            # print("bug2")
                            break
            # print("下一个：",next[1],next[0])
            stroke.append((y, x))
            # print("g", x, y)
            dis_traversal(spath,img,next[1], next[0], 0, stroke, x, y,tagg)
            return 0


                ##################################   有bug
            # elif (a[i][0] != 0)and(a[i][1] != 0):
            #     if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
            #         next = (y + a[i][0], x + a[i][1])
            #         stroke = traversal(img, next[1], next[0], 0, stroke, x, y,px,py)
            #         stroke.append((y, x))
            #         return stroke
                # print(not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist))
            # print("???")
                ##################################

    print("why is here?")
    print("point_class:",point_class(img,x,y))






def dis_stroke(strokes_path):
    while True:
        f = os.listdir(strokes_path)
        new_round = False
        for k in f:
            if "hav" in k:   #### 已经遍历过且无拐点的笔画段

                continue
            else:           #### 未遍历过以及之前新曾的笔画段
                img = Image.open(strokes_path + "/" + k)
                img = np.array(img)
                num = 0
                ori_points = []
                o = (-999,-999)
                for y in range(img.shape[0]):  ####找两个端点
                    for x in range(img.shape[1]):
                        if img[y][x] == False:
                            if point_class(img, x, y) == 1:
                                o = (y, x)
                                ori_points.append(o)
                                num += 1
                            if point_class(img, x, y) == 0:
                                o = (y, x)
                                ori_points.append(o)
                                num += 1
                if o == (-999,-999):
                    br = 1
                    for y in range(img.shape[0]):  ####随便找到一个黑像素
                        for x in range(img.shape[1]):
                            if img[y][x] == False:
                                o = (y,x)
                                ori_points.append(o)
                                ori_points.append(o)
                                num += 2
                                br = 0
                                break
                        if br == 0:
                            break
                print("num:",num)
                if num >=2:  ################################################################解决一个笔画段因一堆像素点聚集产生超过两个端点
                    maxlen = -1
                    for i in range(ori_points.__len__()):
                        for j in range(i + 1, ori_points.__len__()):
                            if (ori_points[i][0] - ori_points[j][0]) ** 2 + (
                                    ori_points[i][1] - ori_points[j][1]) ** 2 > maxlen:
                                ori_two = []
                                ori_two.append(ori_points[i])
                                ori_two.append(ori_points[j])
                                maxlen = (ori_points[i][0] - ori_points[j][0]) ** 2 + (
                                            ori_points[i][1] - ori_points[j][1]) ** 2
                    ori_points = []
                    ori_points.append(ori_two[0])
                    ori_points.append(ori_two[1])

                else:
                    print("空白")
                    continue
                print("两端点：",ori_points[0][1],ori_points[0][0],ori_points[1][1],ori_points[1][0])
                jud,closeset = find_min_e(img,np.array([ori_points[0][0],ori_points[0][1]]),np.array([ori_points[1][0],ori_points[1][1]]))
                if closeset[0] != -999:  ### 如果是闭合的笔画段，则将第一次搜寻到的拐点作为起始点，再搜拐点
                    ori_points = []
                    ori_points.append(closeset)
                    ori_points.append(closeset)
                    jud,nouse = find_min_e(img,np.array([closeset[0],closeset[1]]),np.array([closeset[0],closeset[1]]))
                if jud == True:
                    s = []
                    dis_traversal(strokes_path,img,ori_points[0][1],ori_points[0][0],1,s)
                    os.remove(strokes_path + "/" + k)
                    print("remove", k)
                    new_round = True
                    break
                else:
                    global n
                    n = n+1
                    os.rename(strokes_path + "/" + k, strokes_path + '/{}_hav.png'.format(n))
        if new_round == False:
            break


stin = 9
tiny = 0
angle_judge = 30
angle = 110
non_L_dis = 35     ### 两个端点距离小于此值，则规定没有拐点
thr1 = 0.94
thr2 = 0.88
dis_per_thr = 0.5     #### 拟拐点和选取两点到直线距离做差的和，与拟拐点到直线距离的比例，小于此阈值则不是拐点
percent = 6               ###选取两点的比例
curve_thr = 2.2  ##  拟拐点的曲率大于此阈值，才算拐点

#############################################################
# path = r'./image'
# f = os.listdir(path + '/所有单字' )
# for name in f:
#     ori = r'\{}_skeleton'.format(name)
#     img = Image.open(path + "/所有单字/" + name + ori + '.png')
#     img = np.array(img)
#     path = r"./image/"
#     spath = r"./image/所有单字/"+name + '/stroke'
#     if not os.path.exists(spath):
#         os.mkdir(spath)
#     d = os.listdir(spath)
#     for k in d:
#         os.remove(spath + "/" + k)
#     # thin(path + "/" + name + ori + '.png')
#     cross_points = []
#     matches = np.zeros((img.shape[0],img.shape[1],2))
#     get_cross(img)
#     # print(cross_points)
#     img = del_stin(img,stin)
#
#     # img = Image.fromarray(img)
#     # img.show()
#
#     cross_points = []
#     matches = np.zeros((img.shape[0],img.shape[1],2))   ###记录交叉点
#     L_ = np.zeros((img.shape[0],img.shape[1],2))           ###记录拐点
#     get_cross(img)
#
#     strokes(img,spath)
#     dis_stroke(spath)
#
#
#
#
#
#     sh = np.zeros((img.shape[0],img.shape[1]))
#     for i in range(matches.shape[0]):
#         for j in range(matches.shape[1]):
#             if matches[i][j][0] != 0 or matches[i][j][1] != 0:
#                 # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
#                 sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
#     sh = Image.fromarray(sh)
#     sh = sh.convert("L")
#     sh.save(path+'/所有单字/' + name+"/matches_{}.png".format(name))
#
#     sl = np.zeros((img.shape[0],img.shape[1]))
#     for i in range(L_.shape[0]):
#         for j in range(L_.shape[1]):
#             if L_[i][j][0] != 0 or L_[i][j][1] != 0:
#                 # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
#                 sl[int(L_[i][j][0])][int(L_[i][j][1])] = 255
#     sl = Image.fromarray(sl)
#     sl = sl.convert("L")
#     sl.save(path+'/所有单字/' +name+"/L_{}.png".format(name))
#
#
#
#     sk = Image.open(path +'/所有单字/' + name + "/" + name + "_skeleton.png")
#     sk = np.array(sk)
#     img = np.array(sh)
#     s = Image.new('RGB',(img.shape[0],img.shape[1]),(255,255,255))
#     s = np.array(s)
#     index = 0
#     font = ImageFont.truetype("arial.ttf", 8)  # ImageFont对象
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             if sk[i][j] == False:
#                 s[i][j] = (125,125,125)
#                 # print("skele")
#             if img[i][j] > 128:
#                 s[i][j] = (0,255,0)
#                 # print("point")
#
#     # print(s)
#     s = Image.fromarray(s)
#     drawImg = ImageDraw.Draw(s)  # 创建一个绘画对象，在img上面画
#
#     k = np.array(s)
#     for i in range(k.shape[0]):
#         for j in range(k.shape[1]):
#             if k[i][j][0] == 0:
#                 print("...")
#                 drawImg.text((j, i), "{}".format(index), (255, 0, 0), font)
#                 index += 1
#     s.save(path + '/所有单字/' +name + "/交叉点示意图.png".format(name))
#     # s.show()
#
#
#
#     sk = Image.open(path + '/所有单字/' + name + "/" + name + "_skeleton.png")
#     sk = np.array(sk)
#     img = np.array(sl)
#     s = Image.new('RGB',(img.shape[0],img.shape[1]),(255,255,255))
#     s = np.array(s)
#     index = 0
#     font = ImageFont.truetype("arial.ttf", 8)  # ImageFont对象
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             if sk[i][j] == False:
#                 s[i][j] = (125,125,125)
#                 # print("skele")
#             if img[i][j] > 128:
#                 s[i][j] = (0,255,0)
#                 # print("point")
#
#     # print(s)
#     s = Image.fromarray(s)
#     drawImg = ImageDraw.Draw(s)  # 创建一个绘画对象，在img上面画
#
#     k = np.array(s)
#     for i in range(k.shape[0]):
#         for j in range(k.shape[1]):
#             if k[i][j][0] == 0:
#                 print("...")
#                 drawImg.text((j, i), "{}".format(index), (255, 0, 0), font)
#                 index += 1
#     s.save(path + '/所有单字/' + name + "/拐点示意图.png".format(name))
#     # s.show()
# #########################################################33
name = "服_SKp"
path = r'./image/完美骨架已完成'
ori = r'\{}'.format(name)
img = Image.open(path + "/" + name + ori + '.png')
img = np.array(img)
path = r"./image/完美骨架已完成/"
spath = r"./image/完美骨架已完成/"+name + '/stroke'
if not os.path.exists(spath):
    os.mkdir(spath)
d = os.listdir(spath)
for k in d:
    os.remove(spath + "/" + k)
# thin(path + "/" + name + ori + '.png')
cross_points = []
matches = np.zeros((img.shape[0],img.shape[1],2))
get_cross(img)
print(cross_points)
# img = del_stin(img,stin)

# img = Image.fromarray(img)
# img.show()

cross_points = []
matches = np.zeros((img.shape[0],img.shape[1],2))   ###记录交叉点
L_ = np.zeros((img.shape[0],img.shape[1],2))           ###记录拐点
end = np.zeros((img.shape[0],img.shape[1],2))   ### 记录端点
get_cross(img)
get_end(img)

strokes(img,spath)
dis_stroke(spath)
combine(spath)
del_white(spath)



all = Image.new('RGB',(img.shape[0],img.shape[1]),(255,255,255))
all = np.array(all)
sh = np.zeros((img.shape[0],img.shape[1]))
for i in range(matches.shape[0]):
    for j in range(matches.shape[1]):
        if matches[i][j][0] != 0 or matches[i][j][1] != 0:
            # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
            sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
            # all[int(matches[i][j][0])][int(matches[i][j][1])] = [255,255,0]
sh = Image.fromarray(sh)
sh = sh.convert("L")
sh.save(path+name+"/matches_{}.png".format(name))

endpic = np.zeros((img.shape[0],img.shape[1]))
for i in range(end.shape[0]):
    for j in range(end.shape[1]):
        if end[i][j][0] != 0 or end[i][j][1] != 0:
            # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
            endpic[int(end[i][j][0])][int(end[i][j][1])] = 255
            # all[int(end[i][j][0])][int(end[i][j][1])] = [255, 255, 0]
endpic = Image.fromarray(endpic)
endpic = endpic.convert("L")
endpic.save(path+name+"/ends_{}.png".format(name))

sl = np.zeros((img.shape[0],img.shape[1]))
for i in range(L_.shape[0]):
    for j in range(L_.shape[1]):
        if L_[i][j][0] != 0 or L_[i][j][1] != 0:
            # all[int(L_[i][j][0])][int(L_[i][j][1])] = [255,255,0]
            # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
            sl[int(L_[i][j][0])][int(L_[i][j][1])] = 255
sl = Image.fromarray(sl)
sl = sl.convert("L")
sl.save(path+name+"/L_{}.png".format(name))



sk = Image.open(path + name + "/" + name + ".png")
sk = np.array(sk)
img = np.array(sh)
s = Image.new('RGB',(img.shape[0],img.shape[1]),(255,255,255))
s = np.array(s)
index = 0
font = ImageFont.truetype("arial.ttf", 8)  # ImageFont对象
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if sk[i][j] == False:
            s[i][j] = (125,125,125)
            all[i][j] = (0,0,0)
            # print("skele")
        if img[i][j] > 128:
            s[i][j] = (0,255,0)
            # print("point")

# print(s)
s = Image.fromarray(s)
drawImg = ImageDraw.Draw(s)  # 创建一个绘画对象，在img上面画

k = np.array(s)
for i in range(k.shape[0]):
    for j in range(k.shape[1]):
        if k[i][j][0] == 0:
            print("...")
            drawImg.text((j, i), "{}".format(index), (255, 0, 0), font)
            index += 1
s.save(path + name + "/交叉点示意图.png".format(name))
s.show()



sk = Image.open(path + name + "/" + name + ".png")
sk = np.array(sk)
img = np.array(sl)
s = Image.new('RGB',(img.shape[0],img.shape[1]),(255,255,255))
s = np.array(s)
index = 0
font = ImageFont.truetype("arial.ttf", 8)  # ImageFont对象
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if sk[i][j] == False:
            s[i][j] = (125,125,125)
            # print("skele")
        if img[i][j] > 128:
            s[i][j] = (0,255,0)
            # print("point")

# print(s)
s = Image.fromarray(s)
drawImg = ImageDraw.Draw(s)  # 创建一个绘画对象，在img上面画

endpic = np.array(endpic)
sh = np.array(sh)
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if sk[i][j] == False:
            all[i][j] = (0,0,0)
        if img[i][j] > 128:
            all[i][j] = (255, 0, 0)
        if endpic[i][j] > 128:
            all[i][j] = (255, 0, 0)
        if sh[i][j] > 128:
            all[i][j] = (255, 0, 0)



k = np.array(s)
for i in range(k.shape[0]):
    for j in range(k.shape[1]):
        if k[i][j][0] == 0:
            print("...")
            drawImg.text((j, i), "{}".format(index), (255, 0, 0), font)
            index += 1
s.save(path + name + "/拐点示意图.png".format(name))
s.show()
all = Image.fromarray(all)
all.save(path + name + "/关键点.png".format(name))
######################################################################################3