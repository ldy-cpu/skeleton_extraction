#####分成笔画段
#####统一处理交叉点

import sys
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os


#      o15  o16 o1  o2  o3
#      o14  i8  i1  i2  o4
#      o13  i7  oo  i3  o5
#      o12  i6  i5  i4  o6
#      o11  o10 o9  o8  o7



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



cross_points = []

def traversal(img,x,y,first,stroke,px = -999,py = -999,ppx = -999,ppy = -999):   #pre
    # print("x,y:",x,y)
    for cross_point in cross_points:      #遇到交叉点则截止
        # print(pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2))
        if cross_point[0] == y and cross_point[1] == x:
            stroke.append((y, x))
            return stroke
        if (pow(cross_point[0] - y,2) + pow((cross_point[1] - x),2) == 1)and(pow(cross_point[0] - py,2) + pow((cross_point[1] - px),2) == 1):
            # print(x,y,px,py)
            return stroke
    if point_class(img,x,y) == 0:   #瑕疵点
        stroke.append((y,x))
        return stroke
    ######## 端点
    if point_class(img,x,y) == 1:
        if first == 0:              #终点
            stroke.append((y,x))
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
            if next == (-999,-999):
                for i in range(a.shape[0]):
                    if a.shape[0] == 3:
                        if (not([a[i][0]+1,a[i][1]]in arrlist)) and (not([a[i][0]-1,a[i][1]]in arrlist)) and (not([a[i][0],a[i][1]+1]in arrlist)) and (not([a[i][0],a[i][1]-1]in arrlist)):
                            next = (y + a[i][0], x + a[i][1])
                            # print("bug2")
                            break
            # print("下一个：",next[1],next[0])
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




    stroke.append((y,x))   #把笔画断裂的那个点作为笔画了
    return stroke


n = 1

def strokes(img):
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
        if x !=img.shape[1]-1:
            break
    if o == (-999,-999):
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
    path = r"D:/project/stroke_segmentation/image/test"
    if not os.path.exists(path + "/stroke"):
        os.mkdir(path + "/stroke")
    if not os.path.exists(path + "/remain"):
        os.mkdir(path + "/remain")
    global n
    white_pic.save(path + "/stroke/{}.png".format(n))
    for dot in stroke:
        img[dot[0]][dot[1]] = True
    test_img = Image.fromarray(img)
    test_img.save(path + "/remain/{}.png".format(n))
    n = n + 1
    # print(n)
    strokes(img)

    return 0



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
    # return dots, ct

def combine(s_path,cross):
    print("start combine")
    for cross_point in cross:   #遍历每个交叉点
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
            if num <= 4:        #改变数值以适应不同交叉点分裂
                small_name.append(name[i])  #单独记录小于阈值长度的，以便于与所有大于4长度的笔画段相接

            elif num < 10:
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
                    if re >= 9:
                        angles.append(dots[re-9])          #记录本笔画段对应计算角度的像素坐标,同上
                        angle_name.append(name[i])     #记录本笔画段对应计算角度的像素坐标#记录本笔画段的文件名
                    else:
                        angles.append(dots[0])
                        angle_name.append(name[i])
                else:
                    angles.append(dots[9])
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
                            if theta >= 130:
                                if theta > max:
                                    max = theta
                                    m1 = angle_name[yi]
                                    m2 = angle_name[er]
            # print(max)
            if m1 != -999:
                ms.append(m1)
                ms.append(m2)
        # print(ms)
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
            tag = 0
            for rr in angle_name:
                new_stroke = rela[name.index(rr)]
                if not (rr in ms):
                    tag = 1
                    for gg in range(len(small_name)):
                        small_stroke = rela[name.index(small_name[gg])]
                        for pp in range(small_stroke.shape[0]):
                            for qq in range(small_stroke.shape[1]):
                                if small_stroke[pp][qq] == False:
                                    new_stroke[pp][qq] = False
                    new_stroke[cross_point[0]][cross_point[1]] = False
                    news = Image.fromarray(new_stroke)
                    news.save(s_path + "/{}.png".format(rr))
        else:
            tag = 1
            for rr in angle_name:
                new_stroke = rela[name.index(rr)]
                for gg in range(len(small_name)):
                    small_stroke = rela[name.index(small_name[gg])]
                    for pp in range(small_stroke.shape[0]):
                        for qq in range(small_stroke.shape[1]):
                            if small_stroke[pp][qq] == False:
                                new_stroke[pp][qq] = False
                    new_stroke[cross_point[0]][cross_point[1]] = False
                    news = Image.fromarray(new_stroke)
                    news.save(s_path + "/{}.png".format(rr))
        if tag == 1:
            for gg in range(len(small_name)):
                white = np.ones((img.shape[0], img.shape[1]), bool)
                white = Image.fromarray(white)
                white.save(s_path + "/{}.png".format(small_name[gg]))
                # os.remove(s_path + "/{}.png".format(rela[small_name[gg]]))
                # print("delete small")
    print("combine done!")
    return 0


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


def get_cross(img):
    for p in range(img.shape[0]):
        for q in range(img.shape[1]):
            if img[p][q] == False:
                if point_class(img, q, p) == 3:
                    # print("当前交叉点",x,y)
                    # tag = 0
                    # for near in range(len(cross_points)):
                    #     if pow((cross_points[near][0]-p),2) + pow((cross_points[near][1]-q),2) <= 2:
                    #         tag = 1
                    #         break
                    # if tag == 0:
                        cross_points.append((p, q))  # 记录交叉点
    return 0



path = r'D:\project\stroke_segmentation\image'
ori = r'\wo_skeleton'
img = Image.open(path + ori + '.png')
img = np.array(img)
path = r"D:/project/stroke_segmentation/image/test"
get_cross(img)
strokes(img)
combine(path + "/stroke",cross_points)
del_white(path + "/stroke")

