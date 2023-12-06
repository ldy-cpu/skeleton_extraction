import numpy as np
import pickle

path = r'./image'
name = "/补"
point_path = np.loadtxt(path + name  + "/src.txt")
# print(point_path)      ##########



fills = []
fill = [1,2]
fills.append(fill)
fill = [5,3,7,12]
fills.append(fill)
fill = [7,10,13]
fills.append(fill)
fill = [4,8]
fills.append(fill)
fill = [10,11]
fills.append(fill)
fill = [0,6,14]
fills.append(fill)
fill = [6,9]
fills.append(fill)
# fill = [16,12,13]
# fills.append(fill)
# fill = [20,18,17]
# fills.append(fill)
# fill = [0,3,10,12,18,23]
# fills.append(fill)
# fill = [1,2]
# fills.append(fill)
# fill = [28,27,26,24]
# fills.append(fill)
# fill = [26,35,34,33]
# fills.append(fill)
# fill = [27,30]
# fills.append(fill)
# fill = [16,21,26]
# fills.append(fill)
# fill = [27,26,25]
# fills.append(fill)
# fill = [15,13,19,40,38,33]
# fills.append(fill)
# fill = [22,18]
# fills.append(fill)
# fill = [29,26]
# fills.append(fill)
# fill = [31,35]
# fills.append(fill)





#########################################################
print(name)


#############################################################
point_to_stroke = []
for i in range(point_path.shape[0]):
    H = []
    for j in range(point_path.shape[0]):
        L = []
        H.append(L)
    point_to_stroke.append(H)

for s in range(fills.__len__()):
    fill = fills[s]
    for i in range(fill.__len__()):
        for j in range(fill.__len__()):
            if i == j:
                continue
            point_to_stroke[fill[i]][fill[j]].append(int(s+1))

print(point_to_stroke)
m=np.array(point_to_stroke)
stroke_path = path + name + "/src_stroke"
np.save(stroke_path,arr=m)


################################################################



####################################################################################
# point_to_stroke = np.zeros((point_path.shape[0],point_path.shape[0]))
# for s in range(fills.__len__()):
#     fill = fills[s]
#     for i in range(fill.__len__()):
#         for j in range(fill.__len__()):
#             if i == j:
#                 continue
#             point_to_stroke[fill[i]][fill[j]] = int(s+1)
#             point_to_stroke[fill[j]][fill[i]] = int(s+1)
#
# print(point_to_stroke)
# stroke_path = path + name + "/src_stroke"
# np.save(stroke_path,arr=point_to_stroke)
####################################################################################



