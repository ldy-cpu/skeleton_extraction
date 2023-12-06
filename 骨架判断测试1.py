from functools import partial
import math
from matplotlib.pyplot import angle_spectrum
# import this
import numpy as np
from PIL import Image
import operator
import matplotlib.pyplot as plt


class SkelentonPoint:
    def __init__(self):
        self.x = -1
        self.y = -1
        self.classification = None  # 点类别       0：默认 1：端点 2：常规点 3：分叉点 4：邻接点
        self.visited = None  # 访问记录     0：没访问过 1：访问过
        self.direction = None  # 下一个点的方向记录 范围0~7

    # 设置骨架点(x, y)坐标值
    def set_xy(self, x, y):
        self.x = x
        self.y = y

    # 获取骨架点(x, y)坐标值
    def get_xy(self):
        return self.x, self.y

    # 设置骨架点类别-
    def set_classification(self, image):
        img = image
        classification = self.is_end_con_fork(img)
        self.classification = classification

    # 获取骨架点类别
    def get_classification(self):
        return self.classification

    # 设置该点的访问状态为-访问过
    def set_visited(self):
        self.visited = 1

    # 重置该点的访问状态为-未访问
    def reset_visited(self):
        self.visited = 0

    # 获取该点的访问状态
    def is_visited(self):
        return self.visited

    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)
        # return "(" + self.x + "," + self.y + ")"

    # 获取该点的邻居
    # def neighbours(self, image):
    #     img = image
    #     x_1, y_1, x1, y1 = self.x - 1, self.y - 1, self.x + 1, self.y + 1
    #     return [img[x_1][self.y], img[x_1][y1], img[self.x][y1], img[x1][y1],  # P2,P3,P4,P5
    #             img[x1][self.y], img[x1][y_1], img[self.x][y_1], img[x_1][y_1]]  # P6,P7,P8,P9

    # 定义像素点周围的8邻域
    #       P8 P1 P2
    #       P7 P0 P3
    #       P6 P5 P4
    # 返回8邻域
    def neighbours_xy(self):
        return [(self.x - 1, self.y),       (self.x - 1, self.y + 1),                                 # P1, P2,
                (self.x, self.y + 1),       (self.x + 1, self.y + 1),   (self.x + 1, self.y),         # P3, P4, P5
                (self.x + 1, self.y - 1),   (self.x, self.y - 1),       (self.x - 1, self.y - 1), ]   # P6, P7, P8

    # 获取8邻域中值为1的邻居坐标
    def get_neighbour(self, image):
        img = image
        neighbours = []
        neighbours_8 = self.neighbours_xy()
        for i, coordinate in enumerate(neighbours_8):
            x, y = coordinate
            if img[x][y] == 1:
                # point = SkelentonPoint()
                # point.set_xy(x, y)
                # neighbours.append(point)
                neighbours.append((x, y))
        return neighbours

    # 判断该点是否为端点
    def      is_end_con_fork(self, image):
        img = image
        neighbours = self.get_neighbour(img)
        return len(neighbours)

    # 设置当前点的下一个点所处的方向
    def set_direction(self, x, y, image):
        neighbours_8 = self.neighbours_xy()
        direction = neighbours_8.index((x, y))
        self.direction = direction + 1



    # def find_next_point(self, image):
    #     neighbours = self.get_neighbour()
    #     for point in neighbours:
    #         if point.is_visited() == 0:
    #             point.set_visited()



class Skelenton:

    def __init__(self, image):
        self.sk = []        # 骨架点
        self.end = []       # 端点
        self.con = []       # 常规点
        self.fork = []      # 分叉点
        self.dir = []       # 方向序列
        self.stroke_part = list()       # 笔画段集合，嵌套列表
        self.stroke = list()            # 笔画集合，嵌套列表
        self.image = image
        self.image_stroke = list()      # 笔画图集合
        self.set_skelenton(image)       # 将骨架图中所有点加入 sk 列表
        self.set_classification(image)      # 为骨架中的点分类

    # 向 sk 列表中添加新的点
    def add_point(self, point):
        self.sk.append(point)

    # 打印骨架中的所有像素点
    def print_skelenton(self):
        print(self.sk)
        # for point in self.sk:
        #     print(point)

    # 打印骨架中的所有端点
    def print_end(self):
        print("端点：  ", end="")
        print(self.end)

    # 打印骨架中的所有普通点
    def print_con(self):
        print("普通点：", end="")
        print(self.con)

    # 打印骨架中的所有分叉点
    def print_fork(self):
        print("分叉点：", end="")
        print(self.fork)

    # 将骨架图中所有点加入 sk 列表
    def set_skelenton(self, image):
        Image_Thinned = image.copy()
        rows, columns = Image_Thinned.shape
        for x in range(1, rows - 1):
            for y in range(1, columns - 1):
                if Image_Thinned[x][y] == 1:
                    point = SkelentonPoint()
                    point.set_xy(x, y)
                    self.sk.append(point)

    # 为骨架中的点分类
    def set_classification(self, image):
        for point in self.sk:
            point.set_classification(image)
            classification = point.get_classification()
            if classification == 1:
                self.end.append(point)
            if classification == 2:
                self.con.append(point)
            if classification >= 3:
                self.fork.append(point)

    def amalgamate_fork(self):
        
        return

    # 重置所有骨架点的访问状态
    def reset_visited(self):
        for point in self.sk:
            point.reset_visited()

    # 得到笔画段————递归
    def get_stroke_part_recursive(self, this_point, part):
        img = self.image
        this_point.set_visited()
        part.append(this_point)
        if this_point.get_classification() != 2:
            return    
        neighbours = this_point.get_neighbour(img)
        for x, y in neighbours:
            for next_point in self.sk:
                if operator.eq((x, y), next_point.get_xy()):
                    if next_point.is_visited() == 0:
                        self.get_stroke_part_recursive(next_point, part)

    # 得到骨架笔画段集合
    def get_stroke_part(self):
        img = self.image

        self.reset_visited()

        for fork in self.fork:
            neighbours = fork.get_neighbour(img)
            fork.set_visited()
            for x, y in neighbours:
                for this_point in self.sk:
                    if operator.eq((x, y), this_point.get_xy()):        # 找到fork的邻居
                        if this_point.is_visited() == 0:
                            this_point.set_visited()
                            print(this_point)
                            part = list()       # 存放当前骨架笔画段的列表
                            part.append(fork)
                            part.append(this_point)
                            neighbours = this_point.get_neighbour(img)
                            for x, y in neighbours:
                                for next_point in self.sk:
                                    if operator.eq((x, y), next_point.get_xy()):
                                        if next_point.is_visited() == 0:
                                            self.get_stroke_part_recursive(next_point, part)      # 递归寻找下一个相邻的骨架点
                                            self.stroke_part.append(part)  
                                 

    def get_slope(self, point1, point2):
        x1, y1 = point1.get_xy()
        x2, y2 = point2.get_xy()
        return (y1 - y2)/(x1 - x2) 

    # 计算向量角度
    def _get_angle(self, point1, point2):
        x1, y1 = point1.get_xy()
        x2, y2 = point2.get_xy()
        angle = math.atan2(y1-y2, x1-x2)
        angle = int(angle * 180/math.pi)
        return angle
    
    # 找角度间的最大值
    def _find_max(self, angle, length):
        max = 0
        for i in range(length):
            if max < angle[i]:
                max = angle[i]
                flag = i
        return flag, max

    # 计算各个笔画段间的夹角，并寻找对应关系
    def get_angle(self, fork_stroke_part):
        angle = list()
        for part in fork_stroke_part:
            angle.append(self._get_angle(part[0], part[4]))     # 还少一个分叉点在最后的情况没写，并且设置的为距离分叉点5个像素计算角度
        
        stroke_pipei = np.zeros((len(angle), len(angle)), dtype=np.int32)
        for i in range(len(angle)):
            for j in range(len(angle)):
                if i == j:
                    continue
                if angle[i] * angle[j] >= 0:
                    stroke_pipei[i][j] = abs(angle[i] - angle[j])
                else:
                    stroke_pipei[i][j] = abs(angle[i]) + abs(angle[j])
                    if stroke_pipei[i][j] > 180:
                        stroke_pipei[i][j] = 360 - stroke_pipei[i][j]
        
        for i in range(len(angle)):
            flag, max = self._find_max(stroke_pipei[i], len(stroke_pipei))
            if max >= 160:      # 设置两笔画段间夹角不小于160时，认为其对应
                stroke_pipei[i] = 0
                stroke_pipei[i][flag] = 1
            else:
                stroke_pipei[i] = 0
        
        print(stroke_pipei)
        return stroke_pipei
    
    # 组合笔画
    def amalgamate_stroke(self, stroke_pipei, fork_stroke_part):
        flag_del = list()
        for i in range(np.shape(stroke_pipei)[0]):
            for j in range(i, np.shape(stroke_pipei)[1]):
                if stroke_pipei[i][j] == 1 and stroke_pipei[j][i] == 1:
                    # 说明i, j代表的笔画匹配成功，将其合并
                    if fork_stroke_part[i][0] == fork_stroke_part[j][0]:
                        fork_stroke_part[i] = list(reversed(fork_stroke_part[i]))
                        fork_stroke_part[j].pop(0)
                        fork_stroke_part[i].extend(fork_stroke_part[j])
                    elif fork_stroke_part[i][-1] == fork_stroke_part[j][-1]:
                        fork_stroke_part[i] = list(reversed(fork_stroke_part[i]))
                        fork_stroke_part[i].pop(0)
                        fork_stroke_part[j].extend(fork_stroke_part[i])
                    flag_del.insert(0, j)

        for i in flag_del:
            fork_stroke_part.pop(i)

    # 获取笔画，从分叉点处分割，而后组合
    def get_stroke(self):
        img = self.image
        
        self.reset_visited()

        for fork in self.fork:
            fork_stroke_part = list()       # 保存与当前分叉点相连的所有笔画段

            # 寻找与当前分叉点相连的笔画段
            for i in range(len(self.stroke_part)-1, -1, -1):
                if self.stroke_part[i][0] == fork or self.stroke_part[i][-1] == fork:
                    # 将其从笔画段集合self.stroke_part中抽出，放入当前分叉点相连笔画段集合fork_stroke_part中
                    fork_stroke_part.append(self.stroke_part.pop(i))

                    # print(part[0], part[10])
                    # slope = self.get_slope(part[0], part[4])
                    # self.get_angle(part[0], part[10])
                    # print(slope)
            # 计算当前分叉点相连笔画段之间的夹角
            stroke_pipei = self.get_angle(fork_stroke_part)
            self.amalgamate_stroke(stroke_pipei, fork_stroke_part)

            self.stroke_part.extend(fork_stroke_part)

        for i in range(len(self.stroke_part)):
            print(len(self.stroke_part), self.stroke_part[i])
        self.stroke.extend(self.stroke_part)

    def get_stroke_image(self):
        img_shape = self.image.shape
        for i in range(len(self.stroke)):
            img_stroke = np.zeros(img_shape, dtype=np.int32)
            for j in range(len(self.stroke[i])):
                x, y = self.stroke[i][j].get_xy()
                img_stroke[x][y] = 1
            self.image_stroke.append(img_stroke)


    # 
    def find_xy_point(self, x, y, image):
        return self.sk.index((x, y))

    # 得到方向序列————递归
    def get_direction_recursive(self, this_point):
        img = self.image
        this_point.set_visited()
        neighbours = this_point.get_neighbour(img)
        for x, y in neighbours:
            for next_point in self.sk:
                if operator.eq((x, y), next_point.get_xy()):
                    if next_point.is_visited() == 0:
                        this_point.set_direction(x, y, img)
                        self.dir.append(this_point)
                        self.get_direction_recursive(next_point)

    # 得到方向序列
    def get_direction(self):
        img = self.image

        self.reset_visited()

        x1, y1 = self.end[0].get_xy()
        x2, y2 = self.end[1].get_xy()
        if x1 + y1 < x2 + y2:
            start = self.end[0]
        else:
            start = self.end[1]

        self.get_direction_recursive(start)

    # 打印方向序列
    def print_direction(self):
        counts = np.zeros((8,), dtype=np.int)
        for point in self.dir:
            counts[point.direction - 1] += 1
            print(point.direction, end=", ")

        print()
        for i in range(8):
            print(i+1, counts[i])


# np.set_printoptions(threshold=np.inf)
path = "D:\project\stroke_segmentation\image"
filename = "\shi1_skeleton.txt"
filename_open = path + filename
BW = np.loadtxt(filename_open, delimiter=' ')
skelenton1 = Skelenton(BW)

print("总点数：", end="")
print(len(skelenton1.sk), len(skelenton1.con))
# skelenton1.print_skelenton()
skelenton1.print_end()
skelenton1.print_con()
skelenton1.print_fork()
'''
skelenton1.get_stroke_part()
# print(skelenton1.stroke_part)
for i in range(3):
    print(skelenton1.stroke_part[i])
    print(len(skelenton1.stroke_part[i]))

skelenton1.get_stroke()
skelenton1.get_stroke_image()

fig, ax = plt.subplots(1, len(skelenton1.stroke)+1)
ax = ax.ravel()

ax[0].imshow(skelenton1.image, cmap=plt.cm.gray)
ax[0].set_title('Original skelenton image')
ax[0].axis('off')

for i in range(len(skelenton1.stroke)):
    # eval("ax" + repr(i+2)).imshow(skelenton1.image_stroke[i], cmap=plt.cm.gray)
    # eval("ax" + repr(i+2)).set_title('stroke' + repr(i+2) + ' skelenton image')
    # eval("ax" + repr(i+2)).axis('off')
    ax[i+1].imshow(skelenton1.image_stroke[i], cmap=plt.cm.gray)
    ax[i+1].set_title('stroke' + repr(i+1) + ' skelenton image')
    ax[i+1].axis('off')
    
plt.show()

# skelenton1.get_direction()
# skelenton1.print_direction()
'''