
#####不分笔画段，直接用16邻域判断是否继续遍历为一个笔画
import sys
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
path = r'D:\project\stroke_segmentation\image'
ori = r'\test_skeleton'
img = Image.open(path + ori + '.png')
img = np.array(img)

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

def oneighbor(img,x,y):
    if img[y][x] == True:
        print("中心点不是黑色像素o")
        sys.exit(0)
    o1 = {'img': img[y - 2][x], 'y+': -2, 'x+': 0}
    o2 = {'img': img[y - 2][x + 1], 'y+': -2, 'x+': 1}
    o3 = {'img': img[y - 2][x + 2], 'y+': -2, 'x+': 2}
    o4 = {'img': img[y - 1][x + 2], 'y+': -1, 'x+': 2}
    o5 = {'img': img[y][x + 2], 'y+': 0, 'x+': 2}
    o6 = {'img': img[y + 1][x + 2], 'y+': 1, 'x+': 2}
    o7 = {'img': img[y + 2][x + 2], 'y+': 2, 'x+': 2}
    o8 = {'img': img[y + 2][x + 1], 'y+': 2, 'x+': 1}
    o9 = {'img': img[y + 2][x], 'y+': 2, 'x+': 0}
    o10 = {'img': img[y + 2][x - 1], 'y+': 2, 'x+': -1}
    o11 = {'img': img[y + 2][x - 2], 'y+': 2, 'x+': -2}
    o12 = {'img': img[y + 1][x - 2], 'y+': 1, 'x+': -2}
    o13 = {'img': img[y][x - 2], 'y+': 0, 'x+': -2}
    o14 = {'img': img[y - 1][x - 2], 'y+': -1, 'x+': -2}
    o15 = {'img': img[y - 2][x - 2], 'y+': -2, 'x+': -2}
    o16 = {'img': img[y - 2][x - 1], 'y+': -2, 'x+': -1}
    outside = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, o14, o15, o16]
    outside_b = []
    name = []
    for i in range(16):
        if outside[i]['img'] == False:
            a = (outside[i]['y+'],outside[i]['x+'])
            outside_b.append(a)
            p = i + 1
            name.append(p)

    return outside_b,name

def point_class(img,x,y,iso = 0):
    inside,u,name = ineighbor(img,x,y)
    inside = np.array(inside)
    if inside.shape[0] == 0:
        if iso == 0:
            print("存在孤点")
            print(x,y)
            sys.exit(0)
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



def traversal(img,x,y,first,stroke,px = -999,py = -999,ppx = -999,ppy = -999):   #pre
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
    #######交叉点
    if point_class(img,x,y) == 3:
        # print("当前交叉点",x,y)
        i,b,iname = ineighbor(img,x,y)
        o,oname = oneighbor(img,x,y)
############################### 计算角度从pre计算
        # for l in range(len(iname)):
        #     if (i[l][0] + y == py)and(i[l][1] + x == px):
        #         break
        # z = iname[l] * 2 - 1                            #z为pre点的延长，用于计算其他16领域和z的夹角
        # o.append((py, px))
        # oname.append(z)
  #####################################


#########################################计算角度从ppre计算
        z = -999
        for tt in range(len(oname)):
            if (o[tt][0] + y) == ppy and (o[tt][1] + x) == ppx:
                z = oname[tt]
                break
        if z == -999:
            for tt in range(len(oname)):
                if ((o[tt][0] + y + 1  == ppy)and(o[tt][1] + x == ppx))or((o[tt][0] + y - 1  == ppy)and(o[tt][1] + x == ppx))or((o[tt][0] + y == ppy)and(o[tt][1] + x + 1 == ppx))or((o[tt][0] + y == ppy)and(o[tt][1] + x - 1 == ppx)):
                    z = oname[tt]
                    break
        if z == -999:
            print("ppre不在16领域，且找不到pppre")


#############################################
        ms = []         #角度最大的向量组  两两成对
        for tt in range(5):     # 5没有什么意义
            max = 0  # 最大的角度
            m1 = -999
            m2 = -999
            for yi in range(len(oname)):
                if not(oname[yi] in ms):
                    for er in range(len(oname)):
                        if not(oname[er] in ms):
                            theta = clockwise_angle(o[yi],o[er])
                            if theta >= 135:
                                if theta > max:
                                    max = theta
                                    m1 = oname[yi]
                                    m2 = oname[er]
            # print(max)
            if m1 != -999:
                ms.append(m1)
                ms.append(m2)
        # print("z:",z)
        # print(ms)
        if z in ms:         #如果上一个结点还能继续成笔画
            index = ms.index(z)
            if index%2 == 0:
                nnext_n = ms[index + 1]    #16领域的搜索方向代号
            else:
                nnext_n = ms[index - 1]
            # print(nnext_n)
            if (nnext_n == 3)or(nnext_n == 7)or(nnext_n == 11)or(nnext_n == 15):
                if (nnext_n + 1)/2 in iname:
                    next_n = (nnext_n + 1)/2
                else:
                    stroke.append((y, x))
                    return stroke
            elif (nnext_n == 5)or(nnext_n == 9)or(nnext_n == 13):
                if (nnext_n + 1)/2 in iname:
                    next_n = (nnext_n + 1)/2
                elif ((nnext_n + 1)/2 + 1) in iname:
                    next_n = ((nnext_n + 1)/2 + 1)
                elif ((nnext_n + 1)/2 - 1) in iname:
                    next_n = ((nnext_n + 1) / 2 - 1)
                else:
                    stroke.append((y, x))
                    return stroke
            elif (nnext_n == 1):
                if (nnext_n + 1)/2 in iname:
                    next_n = (nnext_n + 1)/2
                elif ((nnext_n + 1)/2 + 1) in iname:
                    next_n = ((nnext_n + 1)/2 + 1)
                elif 8 in iname:
                    next_n = 8
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 2:
                if 1 in iname:
                    next_n = 1
                elif 2 in iname:
                    next_n = 2
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 4:
                if 3 in iname:
                    next_n = 3
                elif 2 in iname:
                    next_n = 2
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 6:
                if 3 in iname:
                    next_n = 3
                elif 4 in iname:
                    next_n = 4
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 8:
                if 5 in iname:
                    next_n = 5
                elif 4 in iname:
                    next_n = 4
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 10:
                if 5 in iname:
                    next_n = 5
                elif 6 in iname:
                    next_n = 6
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 12:
                if 7 in iname:
                    next_n = 7
                elif 6 in iname:
                    next_n = 6
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 14:
                if 7 in iname:
                    next_n = 7
                elif 8 in iname:
                    next_n = 8
                else:
                    stroke.append((y, x))
                    return stroke
            elif nnext_n == 16:
                if 1 in iname:
                    next_n = 1
                elif 8 in iname:
                    next_n = 8
                else:
                    stroke.append((y, x))
                    return stroke


            if next_n%2 == 0:           ## 虽然next本应是偶数位，但如果有基数位和此偶数位紧挨，则应该通过基数位去偶数位## 此行为可能导致重新遍历已遍历过的基数位
                if next_n == 8:
                    if 1 in iname:
                        next_n = 1
                    if 7 in iname:
                        next_n = 7
                elif (next_n + 1)in iname:
                    next_n = next_n + 1

                elif (next_n - 1)in iname:
                    next_n = next_n -1
            # print(next_n)

            for c in range(len(iname)):
                if iname[c] == next_n:
                    next_set = i[c]       #8领域下一个点的坐标
                    break

            next = (y + next_set[0], x + next_set[1])
            stroke = traversal(img, next[1], next[0], 0, stroke, x, y,px,py)
            stroke.append((y, x))
            return stroke

        else:
            stroke.append((y, x))
            return stroke



    # stroke.append((y,x))   #把笔画断裂的那个点作为笔画了
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
        if x !=img.shape[1]-1:
            break
    if o == (-999,-999):
        print("done!")
        sys.exit(0)
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
    global n
    white_pic.save("D:/project/stroke_segmentation/image/test/{}.png".format(n))

    pots = []    #记录删除像素点之前的交叉点
    for pot in stroke:
        if point_class(img,pot[1],pot[0]) == 3:
            pots.append(pot)

    for dot in stroke:
        img[dot[0]][dot[1]] = True
    for dot in pots:
        img[dot[0]][dot[1]] = False
    test_img = Image.fromarray(img)
    test_img.save("D:/project/stroke_segmentation/image/test/remain{}.png".format(n))
    n = n + 1
    print(n)
    strokes(img)

    return 0






strokes(img)