## 保存笔画信息，从左上的拐点和端点开始，然后根据笔画对应的笔画段（关键点处已连接，只有拐点处断开）的   #上下左右以及斜下左、斜下右（因撇，提等无法保证起笔更左上，所以不能用）#
# /横、竖、左斜、右斜判断对错;如果错误则起点轮到下一个（如是拐点，则拐点的另一条路径），直到剩下所有笔画段都不符合笔画信息，则报错;如果正确，则保存此笔画
import os
import sys

from PIL import Image
import numpy as np
from seg_with_dis import point_class
import goto
from dominate.tags import label

from goto import with_goto




                                    #   4  1  2
                                    #   3  o  3
                                    #   2  1  4
stroke_name = {'横':[3],'竖':[1],'撇':[2],'捺':[4],'点':[4],'提':[2],'竖钩':[1,4],\
               '弯钩':[1,4],'卧钩':[4,1],'横钩':[3,2],'横撇':[3,2],'横撇弯钩':[3,2,1,4],\
               '横折':[3,1],'横折钩':[3,1,4],'横折提':[3,1,2],'横折弯':[3,1,3],'横折弯钩':[3,1,3,1],\
               '横折折撇':[3,2,3,2],'横折折折钩':[3,2,3,2,4],'撇点':[2,4],'撇折':[2,3],\
               '竖提':[1,2],'竖弯':[1,3],'竖弯钩':[1,3,1],'竖折':[1,3],'竖折撇':[1,3,2],'竖折折钩':[1,3,1,4],\
               '斜钩':[4,1]}



def clockwise_angle(v1, v2):
 x1,y1 = v1
 x2,y2 = v2
 dot = x1*x2+y1*y2
 det = x1*y2-y1*x2
 theta = np.arctan2(det, dot)
 theta = theta if theta>0 else 2*np.pi+theta
 theta = theta * 180 / np.pi
 theta = int(theta)
 return theta


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
                # order.append(i+2*j)
                order.append(i + j)
    order = np.array(order)
    # points = np.array(points)
    order = np.argsort(order).astype(np.int32)
    return points,order



def type_judge(x1,y1,x2,y2,type):   ## 判断笔画段是否属于接下来应该有的那一类
    angel = clockwise_angle((1, 0), (x1 - x2, y1 - y2))
    if type == 1:   #接下来应是竖
        if (angel>=45 and angel<=135) or (angel>=225 and angel<=315):
            return True
        else:
            return False
    if type == 2:  #左下斜
        if (angel>=90 and angel<=180) or (angel>=270 and angel<=360) or angel == 0:
            return True
        else:
            return False
    if type == 3:  ##横
        if (angel>=0 and angel<=45) or (angel>=135 and angel<=225) or (angel>=315 and angel <=360):
            return True
        else:
            return False
    if type == 4:  ##右下斜
        if (angel>=0 and angel<=90) or (angel>=180 and angel<=270):
            return True
        else:
            return False
    print('笔画内字典出错')
    sys.exit(1)


@with_goto
def makestroke(path,strokes,points,order):
    L_ = Image.open(path + '/L_{}.png'.format(name))
    L_ = np.array(L_)
    for stroke in range(strokes.__len__()):   ###按笔顺提取笔画
        print("笔顺：",stroke)
        f = os.listdir(path + '/stroke')  ##每次提取新笔画，笔画段文件都经历了一次更新
        finaltag = 0
        for dot in range(order.shape[0]):   ###每次提取都找最左上的点，如未成功，则继续找其次左上的点
            print("当前笔画起点:",points[order[dot]][1],points[order[dot]][0])
            chance = 1
            L_tag = 0
            first_point = points[order[dot]]
            if L_[points[order[dot]][0]][points[order[dot]][1]] == 255:  ##如果是拐点则给两次机会
                chance = 2
                L_tag = 1

            while chance > 0:  ## 拐点给两次机会，其他点只有一次，没机会了就从下一个左上点开始
                print("chance:",chance)
                remove = [] ## 暂存拟删除的文件名
                strokefinal = np.ones((L_.shape[0], L_.shape[1]), bool)
                for q in range(L_.shape[0]):
                    for m in range(L_.shape[1]):
                        strokefinal[q][m] = np.True_
                chance -= 1
                startpoint = first_point
                pre = (-1,-1)
                nextsubstroke = 0  ## 是否该寻找下一个笔画段的标志
                sub = 0 ## 此笔画的第几段
                i = 0
                while i < f.__len__():   ###遍历笔画段文件，每提取一个笔画段，i都置0，从头遍历

                    if chance == 0 and L_tag == 1:  ## 如果是拐点的第二次，则从后往前，以保证先遍历到另一个路径
                        img = Image.open(path + '/stroke/' + f[f.__len__()-1-i])
                    else:
                        img = Image.open(path + '/stroke/' + f[i])
                    img = np.array(img)

                    if img[startpoint[0]][startpoint[1]] == False and \
                            point_class(img,startpoint[1],startpoint[0]) == 1: ### 此点是笔画段端点
                        for shu in range(L_.shape[0]):
                            for heng in range(L_.shape[1]):
                                if img[shu][heng] == False:
                                    strokefinal[shu][heng] = False
                                    if point_class(img,heng,shu) == 1 and (startpoint[0] != shu or startpoint[1] != heng)\
                                            and (pre[0]!= shu or pre[1] != heng): ## 此笔画段是未记录过的，所以是接下来的路径，所以找到endpoint
                                        endpoint = (shu,heng)
                                        nextsubstroke = 1   ## 找到了新的端点，作为下一段起点
                                        if chance == 0 and L_tag == 1:  ## 如果是拐点的第二次，则从后往前，以保证先遍历到另一个路径
                                            remove.append(path + '/stroke/' + f[f.__len__()-1-i])
                                        else:
                                            remove.append(path + '/stroke/' + f[i])  ## 把此段放入拟删除
                                        i = f.__len__()-1



                    if i == f.__len__()-1:   ## 遍历完一遍了
                        if nextsubstroke == 1:  ## 如果找到了下一段起点(不一定需要真的有下一段，只要发现新的端点即可)
                            nextsubstroke = 0
                            if type_judge(startpoint[1],startpoint[0],endpoint[1],endpoint[0],stroke_name[strokes[stroke]][sub]):  ## 如果此段笔画段符合应有走向
                                if sub == stroke_name[strokes[stroke]].__len__()-1:##如果此笔画段是此笔画的最后一段
                                    print("此笔画笔画段个数：",sub)
                                    strokefinal = Image.fromarray(strokefinal)
                                    strokefinal.save(path + '/strokefinal/{}.png'.format(stroke))
                                    for h in remove:
                                        os.remove(h)
                                    finaltag = 1
                                else:
                                    sub += 1  ## 定位到下一段
                                    pre = startpoint
                                    startpoint = endpoint
                                    i = -1
                        #     else:   ##不符合走向
                        #         chance -= 1
                        # else: ## 未找到新的端点
                        #     chance -= 1
                    i += 1
                if finaltag == 1:
                    break
            if finaltag == 1:
                break
        label.newstroke













# startpoints = []   ###可能起笔的点（端点，交叉点（在笔画段图上此点是端点才行），拐点）
# endpoints =  []    ###可能终结的点（端点，交叉点，（这两个在笔画段上都属于端点，所以只要 判断此点不是拐点，则已终结，判断经过拐点数是否符合即可）   拐点）
# strokemassage = ['竖','横折','横','横','竖','横折','横','横','横','横折','横','横撇','捺']   ###按照笔画，每个笔画上有几个拐点
strokemassage = ['竖','横折','竖','点','撇','横','横','横','点','点','点','点']
name = '黑_SKp'
path = r'./image/完美骨架已完成/' + name
if not os.path.exists(path + '/strokefinal'):
    os.mkdir(path + '/strokefinal')
else:
    f = os.listdir(path + '/strokefinal')
    for k in f:
        os.remove(path + '/strokefinal/' + k)





points,order = luorder(path,name)
makestroke(path,strokemassage,points,order)
