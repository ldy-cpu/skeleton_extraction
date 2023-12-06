##  按左上点排序，然后依次找左上的拐点和端点，并按给定笔画拐点数组，遍历笔画，如不符，则错误

import os
import sys

from PIL import Image
import numpy as np
from seg_with_dis import point_class



def luorder(path,name):    ##按左上排序
    L_ = Image.open(path + '/L_{}.png'.format(name))
    L_ = np.array(L_)
    end = Image.open(path + '/ends_{}.png'.format(name))
    end = np.array(end)
    cross = Image.open(path + '/matches_{}.png'.format(name))
    cross = np.array(cross)
    order = []
    points = []
    for i in range(L_.shape[0]):
        for j in range(L_.shape[1]):
            if L_[i][j] == 255 or end[i][j] == 255 or cross[i][j] == 255:
                points.append((i,j))
                order.append(i+j)
    order = np.array(order)
    # points = np.array(points)
    order = np.argsort(order).astype(np.int32)
    return points,order


def judge(path,points,order,name):    ### 决定笔画
    L_ = Image.open(path + '/L_{}.png'.format(name))
    L_ = np.array(L_)
    # end = Image.open(path + '/ends_{}_SKp.png'.format(name))
    # end = np.array(end)
    cross = Image.open(path + '/matches_{}.png'.format(name))
    cross = np.array(cross)
    index = 0
    lpathchange = 0
    # for i in range(order.shape[0]):   ## 按笔画
    i = 0
    while i <order.shape[0]:
        two = 0
        print("i:",i)
        # if os.listdir(path+'/stroke').__len__() == 0:
        #     break
        if index == strokemassage.__len__():
            # with open(path + "/error.txt", "w") as f:
            #     f.write("2笔画出错！")
            print("all done !!")
            sys.exit(0)
        point = points[order[i]]
        print("此起点：",point[1],point[0])
        f = os.listdir(path+'/stroke')
        strokefinal = np.ones((cross.shape[0], cross.shape[1]), bool)
        for q in range(cross.shape[0]):
            for m in range(cross.shape[1]):
                strokefinal[q][m] = np.True_

        startpoint = point  ## point是整个笔画起点，startpoint是每个笔画段起点
        lnum = 0  ##此次拐点个数计数
        brtag = 0
        remove = []
        print("index: ",index)
        # flag = np.zeros(f.__len__())
        flag = []
        for shi in range(5):   ## 5 没有实际意义，目的是让多循环几遍
            roll = -1

            for k in f:
                roll += 1

                img = Image.open(path + '/stroke/' + k )
                img = np.array(img)
                print("笔画段名称：", k)
                print("wtf:", img[startpoint[0]][startpoint[1]] == False)
                print(startpoint[1],startpoint[0])
                # print("wtf:", point_class(img, startpoint[1], startpoint[0]) == 1)
                print("wtf:", k not in flag)
                if img[startpoint[0]][startpoint[1]] == False and point_class(img,startpoint[1],startpoint[0]) == 1 and (k not in flag):
                    print('a')
                    flag.append(k)
                    startshould = 0
                    for q in range(cross.shape[0]):
                        for m in range(cross.shape[1]):
                            if img[q][m] == False:
                                strokefinal[q][m] = False
                            if img[q][m] == False and (q !=startpoint[0] or m != startpoint[1] )and point_class(img,m,q) == 1:   ### 不是此次起始点，且是端点，则是此次终点
                                pre = startpoint
                                startshould = 1
                                t,o = q,m

                                print("下一轮笔画段起点：",m,q)
                                if L_[q][m] == 255:  ##如果上次终点是拐点，则拐点数＋1
                                    print("l:",m,q)
                                    lnum += 1
                                    brtag = 0
                                    if lnum > strokemassage[index]:   ### 如终点的拐点超出了此笔画应有的拐点数，则打断
                                        print("b:",strokemassage[index])
                                        print("lnum:",lnum)
                                        brtag = 1
                                else:  ##如不是拐点，则终止
                                    brtag = 1

                                    if lnum < strokemassage[index]:   ## 如终止后拐点数不足应有，则出错
                                        if L_[point[0]][point[1]] == 255 and lpathchange == 0:   ## 如果出错了，且是此拐点第一次，则将此拐点相关的两个笔画段交换一下，重新测试

                                            a = strokemassage[index]
                                            strokemassage[index] = strokemassage[index + 1]
                                            strokemassage[index+ 1] = a
                                            # index -= 1

                                            ctntag = 1
                                            brtag = 2
                                            # remove = []

                                        else:                      ## 如果起点不是拐点，或已是此拐点第二次，则出错
                                            with open(path + "/error.txt", "w") as f:
                                                f.write("1笔画出错！")
                                            print("1笔画出错!")
                                            print("lpath:",lpathchange)
                                            sys.exit(0)
            #for k in f:
                    # for q in range(cross.shape[0]):
                    #     for m in range(cross.shape[1]):
                    if startshould == 1:
                        print('startpoint 赋新值')
                        startpoint = (t, o)
                    remove.append(path + '/stroke/' + k)
                    # os.remove(path + '/stroke/' + k)
                    if brtag == 0:
                        continue
                    if brtag == 1:
                        if L_[point[0]][point[1]] != 0:
                            two = 1
                        lpathchange = 0
                        strokefinal = Image.fromarray(strokefinal)
                        strokefinal.save(path + '/strokefinal/{}.png'.format(index))
                        for h in remove:
                            os.remove(h)
                        index += 1
                        break
                    if brtag == 2:
                        # index -= 1
                        i -= 1
                        lpathchange = 1  ## 设置已拐点为笔画开头，已遍历过一条错误路线
                        break
                else:
                    continue
        # for shi in range(5):
            if brtag == 1 or brtag == 2:
                break
        if two == 1:
            i -= 1
        # index += 1
        # if L_[point[0]][point[1]] == 255 and lpathchange == 0:
        #     i -= 1
        # if L_[point[0]][point[1]] == 255:
        #     lpathchange = 1
        # if L_[point[0]][point[1]] == 255 and lpathchange == 1:
        #     lpathchange = 0

        i += 1












# startpoints = []   ###可能起笔的点（端点，交叉点（在笔画段图上此点是端点才行），拐点）
# endpoints =  []    ###可能终结的点（端点，交叉点，（这两个在笔画段上都属于端点，所以只要 判断此点不是拐点，则已终结，判断经过拐点数是否符合即可）   拐点）
strokemassage = [0,1,1,0,0,0,0,1,0,0,1,0,0]   ###按照笔画，每个笔画上有几个拐点
name = '暇_SKp'
path = r'./image/完美骨架已完成/' + name
if not os.path.exists(path + '/strokefinal'):
    os.mkdir(path + '/strokefinal')
else:
    f = os.listdir(path + '/strokefinal')
    for k in f:
        os.remove(path + '/strokefinal/' + k)





points,order = luorder(path,name)
judge(path,points,order,name)
