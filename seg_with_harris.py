#####由s3改动，将分割开的笔画段用拐点进一步分割
import math

import cv2
import sys
import matplotlib.pyplot as plt
from PIL import Image,ImageFont,ImageDraw
import numpy as np
import os


#      o15  o16 o1  o2  o3
#      o14  i8  i1  i2  o4
#      o13  i7  oo  i3  o5
#      o12  i6  i5  i4  o6
#      o11  o10 o9  o8  o7




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
        o = one(x,y,tiny)
        if o == (0,0):
            matches[y][x][0] = y
            matches[y][x][1] = x
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


n = 1

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
    if o == (-999,-999):
        img_last = Image.fromarray(img)
        img_last.save(spath + "/{}.png".format(n))
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
                    # print("当前交叉点",x,y)
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


def one(x,y,tiny): ##确保对比点周围没有其他对比点
    for i in range(tiny):
        for j in range(tiny):
            for t in range(-1,2):
                for o in range(-1,2):
                    if (matches[y+t*i][x+o*j][0] != 0) or (matches[y+t*i][x+o*j][1] != 0):
                        b = (matches[y+t*i][x+o*j][0],matches[y+t*i][x+o*j][1])
                        return b  ##如果周围有其他对比点，用其他对比点代表此点去对比
    return (0,0)

def on_stroke(x,y,tiny,img):  ##将harris检测的点放到笔画上
    min = 999
    a = -999
    b = -999
    for i in range(tiny):
        for j in range(tiny):
            for t in range(-1,2):
                for o in range(-1,2):
                    if img[y+t*i][x+o*j] == False:
                        if i^2+j^2<min:   ##找距离harris检测的点最近的笔画上的点
                            min = t^2+o^2
                            a = y+t*i
                            b = x+o*j
    return a,b

def harris(mod,spath,npypath):
    # 读入图像并转化为float类型，用于传递给harris函数
    f = os.listdir(spath + '/stroke')
    for i in range(1,len(f)+1):
        filename = spath + '/stroke'+ '/{}.png'.format(i)
        img = Image.open(filename)
        img = np.array(img)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] == True:
                    img[i][j] = 255
                else:
                    img[i][j] = 0
        gray_img = np.float32(img)

        # 对图像执行harris
        ######################################################src建库
        if mod == 1:
            q = 6
            w = 3
            e = 0.2
            Harris_detector = cv2.cornerHarris(gray_img, q, w, e)
            arg = np.zeros(3)
            arg[0] = q
            arg[1] = w
            arg[2] = e
            np.save(spath+"/harris_arg.npy",arr=arg)   ####存储harris_arg


        #####################################################
        ###########################################################tar
        else:
            arg = np.load(npypath+"/harris_arg.npy")
            Harris_detector = cv2.cornerHarris(gray_img, int(arg[0]), int(arg[1]), arg[2])


        ############################################################

        # print(Harris_detector)
        # 膨胀harris结果
        dst = cv2.dilate(Harris_detector, None)

        # 设置阈值
        thres = 0.01 * dst.max()
        harris_dots = []
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if Harris_detector[i][j] > 0:
                    min = 999
                    v = one(j,i,tiny)
                    if v == (0, 0):
                        print("harris:",j,i)
                        for p in range(tiny):
                            for q in range(tiny):
                                for t in range(-1, 2):
                                    for o in range(-1, 2):
                                        if img[i+ t * p][j + o * q] == False and p**2+q**2<min:
                                            print("harris_near:",j + o * q,i+ t * p)
                                            min = p**2+q**2
                                            nmin = (i+ t * p,j + o * q)
                        matches[nmin[0]][nmin[1]][0] = nmin[0]
                        matches[nmin[0]][nmin[1]][1] = nmin[1]

                    # else:      #########如果周围有，则不用存，因为这是在笔画中间
                    #     matches[i][j][0] = v[0]  ##存实际代表此点去对比的点
                    #     matches[i][j][1] = v[1]

def harris_traversal(spath,num,img,img_name,x,y,first,stroke,px = -999,py = -999,tagg = []):
    print("x:",x,"y:",y,"first=",first)



    if first == 0 and ((matches[y][x][0] != 0 or matches[y][x][1] != 0)or point_class(img,x,y) == 1):

        for i in range(-1,2):
            for j in range(-1,2):
                if matches[y+i][x+j][0]>0 or matches[y+i][x+j][1]>0:
                    stroke.append((y+i,x+j))
                    print("a",x+i,y+j)
                    break
        print("should cut")
        stroke.append((y,x))
        print("b", x, y)
        white_pic = np.ones((img.shape[0], img.shape[1]), bool)
        for q in range(img.shape[0]):
            for m in range(img.shape[1]):
                white_pic[q][m] = np.True_
        for dot in stroke:
            white_pic[dot[0]][dot[1]] = False
            # img[dot[0]][dot[1]] = True

        white_pic = Image.fromarray(white_pic)
        # path = r"D:/project/stroke_segmentation/image/test"
        white_pic.save(spath + "/{}_{}.png".format(img_name,num))
        stroke = []
        if point_class(img,x,y) == 2:
            harris_traversal(spath,num + 1,img,img_name,x,y,1,stroke,px,py)
        return 0


    if point_class(img,x,y) == 1:

                      #起点
        for i in range(-1, 2):
            for j in range(-1, 2):
                if matches[y + i][x + j][0] > 0 or matches[y + i][x + j][1] > 0:
                    stroke.append((y + i, x + j))
                    print("c", x+i, y+j)
                    break
        a,b,name = ineighbor(img,x,y)
        if b == 1:
            next = (y + a[0][0],x + a[0][1])  #前y,后x
        else:
            for qq in range(len(name)):
                if (a[qq][0] == 0)or(a[qq][1] == 0):
                    next = (y + a[qq][0],x + a[qq][1])
                    break
        stroke.append((y, x))
        print("d", x, y)
        harris_traversal(spath,num,img,img_name,next[1],next[0],0,stroke,x,y)
        return 0


    ########### 一般点
    if point_class(img,x,y) == 2:
        if (x,y) in tagg:
            return  0
        tagg.append((x,y))
        a,b,name = ineighbor(img,x,y)  #b和name没用
        a = np.array(a)
        next = (-999,-999)
        if a.shape[0] == 2:   #领域为2的一般点
            if (a[0][0] + y == py)and(a[0][1] + x == px):
                next = (y + a[1][0],x + a[1][1])
                stroke.append((y, x))
                print("e", x, y)
                harris_traversal(spath,num,img,img_name,next[1],next[0],0,stroke,x,y,tagg)
                return 0
            else:
                next = (y + a[0][0],x + a[0][1])
                stroke.append((y, x))
                print("f", x, y)
                harris_traversal(spath,num,img,img_name,next[1],next[0],0,stroke,x,y,tagg)
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
            print("g", x, y)
            harris_traversal(spath,num,img,img_name,next[1], next[0], 0, stroke, x, y,tagg)
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

def harris_stroke(strokes_path):
    f = os.listdir(strokes_path)
    steady = len(f)
    for k in range(1,steady+1):
        img = Image.open(strokes_path +'/{}.png'.format(k))
        img = np.array(img)
        print(k)
        o = (-999, -999)
        tag = []
        b = 0
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                if img[y][x] == False:
                    if (x,y) in tag:
                        o = (x,y)
                        b = 1
                        break
                    if point_class(img, x, y) == 1:
                        o = (x, y)
                        tag.append(o)
                        break
                    if point_class(img, x, y) == 0:
                        o = (x, y)
                        tag.append(o)
                        break
        if tag.__len__()==0:
            for y in range(img.shape[0]):
                for x in range(img.shape[1]):
                    if img[y][x] == False:
                        if (x, y) in tag:
                            b = 1
                            break

                        if (y, x) in cross_points:
                            o = (x, y)
                            tag.append(o)
                            break
                        if matches[y][x][0] > 0 or matches[y][x][1] > 0:
                            o = (x, y)
                            tag.append(o)
                            break
                if b == 1 or x != img.shape[1] - 1:
                    break
        if o == (-999,-999):
            print("存在闭合")
            continue
            # sys.exit(0)
        stroke = []
        tagg = []
        harris_traversal(strokes_path,1,img,k,o[0],o[1],1,stroke,tagg)
        os.remove(strokes_path+'/{}.png'.format(k))
    return 0



stin = 6
tiny = 6




name = "服_SKp"
path = r'./image/完美骨架已完成'
ori = r'\{}_skeleton'.format(name)
img = Image.open(path + "/" + name + ori + '.png')
img = np.array(img)
path = r"./image/完美骨架已完成/"
spath = r"./image/完美骨架已完成/"+name + '/stroke'
if not os.path.exists(spath):
    os.mkdir(spath)
d = os.listdir(spath)
for k in d:
    os.remove(spath + "/" + k)

cross_points = []
matches = np.zeros((img.shape[0],img.shape[1],2))
get_cross(img)
print (cross_points)
img = del_stin(img,stin)
# img = Image.fromarray(img)
# img.show()

cross_points = []
matches = np.zeros((img.shape[0],img.shape[1],2))
L_ = np.zeros((img.shape[0],img.shape[1],2))
get_cross(img)

strokes(img,spath)
namem = name
for i in range(len(name)):
    if name[i] == '_':
        namem = name[0:i]
        break

harris(1,path+name,path+namem)  ######### 建库用1，测试用0
harris_stroke(spath)


sh = np.zeros((img.shape[0],img.shape[1]))
for i in range(matches.shape[0]):
    for j in range(matches.shape[1]):
        if matches[i][j][0] != 0 or matches[i][j][1] != 0:
            # sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
            sh[int(matches[i][j][0])][int(matches[i][j][1])] = 255
sh = Image.fromarray(sh)
sh = sh.convert("L")
sh.save(path+name+"/matches_{}.png".format(name))


sk = Image.open(path + name + "/" + name + "_skeleton.png")
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
s.show()

if "tar" in name: ##########保存matches数组
    np.save(path+ name + "/point_in_point",arr=matches)