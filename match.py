import matplotlib.pyplot as plt
import pycpd
import numpy as np
from PIL import Image,ImageDraw,ImageFont
#######################都按x,y来，虽然图像出来是反的
def txt_all(img,name,tag):
    with open("./image/TEST/match_point/{}/{}.txt".format(name,tag), "w") as f:
        # i = 0
        # j = 0
        # while i < img.shape[0]:
        #     while j < img.shape[1]:
        #         if img[i][j] > 128:
        #             f.write("{}".format(j))
        #             f.write((" "))
        #             f.write("{}".format(i))
        #             f.write(" ")
        #             f.write("")
        #             f.write("\n")
        #         j += 2
        #     i += 2


        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] == False:
                    f.write("{}".format(j))
                    f.write((" "))
                    f.write("{}".format(i))
                    f.write(" ")
                    f.write("")
                    f.write("\n")
                j+=1
            i+= 1

def txt(path,img,name,tag):
    with open(path + "/{}.txt".format(tag), "w") as f:
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] >128:
                    f.write("{}".format(j))
                    f.write((" "))
                    f.write("{}".format(i))
                    f.write(" ")
                    f.write("")
                    f.write("\n")
def trans_txt(path,img):
    with open(path + "/tar_trans.txt", "w") as f:
        for i in range(img.shape[0]):
            f.write("{}".format(img[i][0]))
            f.write((" "))
            f.write("{}".format(img[i][1]))
            f.write("\n")

def addNumToImg(img):
    drawImg = ImageDraw.Draw(img) # 创建一个绘画对象，在img上面画
    font = ImageFont.truetype("arial.ttf",10) # ImageFont对象
    # print(img.size)
    drawImg.text((img.width-40, 20),"9+",(255, 0, 0),font) # 确定好坐标不能超了！！！
    # img.save("modified.jpg","jpeg") # 保存修改后的图片，（修改后的名字，格式）

    # modified_img = Image.open("modified.jpg")
    img.show()




name = "滨"
path = r'./image'
mod = 0    ############ 建库用1，测试用0
#######################txt
#1.
if mod == 1:
    path = path + '/' + name
    ori = r'\matches_{}'.format(name)
    sk = Image.open(path + "/" + name +"_skeleton.png" )
    sk = np.array(sk)
    img = Image.open(path + ori + '.png')
    img = np.array(img)
    txt(path,img,name,'src')


    # img_all = Image.open('D:\project\stroke_segmentation\image\{}_src_skeleton.png'.format(name))
    # img_all = np.array(img_all)
    # txt_all(img_all,name,'src')

#########src只有建立库的时候用

##########每次有新图片要对比用
#2.
else:
    path = path + '/' + name +'_tar'
    ori = r'\matches_{}_tar'.format(name)
    img = Image.open(path + ori + '.png')
    img = np.array(img)
    txt(path ,img,name,'tar')
    # img_all = Image.open('D:\project\stroke_segmentation\image\{}_tar_skeleton.png'.format(name))
    # img_all = np.array(img_all)
    # # txt_all(img_all,name,'tar')

########################txt


###################对比src和tar
#3.
    path = r'./image'
    X = np.loadtxt(path + '/'+name + "/src.txt")
    Y = np.loadtxt(path + '/'+name + "_tar/tar.txt")
    for i in range(X.shape[0]):
        X[i][0] = X[i][0] / 250
        X[i][1] = X[i][1] / 320
    for j in range(Y.shape[0]):
        Y[j][0] = Y[j][0] / 250
        Y[j][1] = Y[j][1] / 320

    # reg =pycpd.RigidRegistration(**{'X': X, 'Y': Y})
    # data,(s,r,c) = reg.register()
    reg =pycpd.DeformableRegistration(**{'X': X, 'Y': Y})
    data,(s,r) = reg.register()

    for i in range(X.shape[0]):
        X[i][0] = int(X[i][0]*250)
        X[i][1] = int(X[i][1]*320)
    for j in range(data.shape[0]):
        data[j][0] = int(data[j][0]*250)
        data[j][1] = int(data[j][1]*320)

    trans_txt(path+'/'+name+'_tar',data)

    fig = plt.figure()
    ax = fig.gca(projection="3d")
    ax.scatter(data[:,0],data[:,1])
    ax.scatter(X[:,0],X[:,1])
    plt.show()

#######################



# mimg = np.zeros((500,500))
# for i in range(data.shape[0]):
#     mimg[int(data[i][1])][int(data[i][0])] = 255
# for i in range(X.shape[0]):
#     mimg[int(X[i][0])][int(data[i][1])] = 128
#
# mimg = Image.fromarray(mimg)
# mimg = mimg.convert("L")
# mimg.save("./image/TEST/match_point/match_pic.png")

