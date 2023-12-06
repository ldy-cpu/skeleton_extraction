from functools import partial
import matplotlib.pyplot as plt
from pycpd import DeformableRegistration,RigidRegistration
import numpy as np
import time
from PIL import Image

def visualize(iteration, error, X, Y, ax):
    plt.cla()
    ax.scatter(X[:, 0],  X[:, 1], color='red', label='Target')
    ax.scatter(Y[:, 0],  Y[:, 1], color='blue', label='Source')
    plt.text(0.87, 0.92, 'Iteration: {:d}'.format(
        iteration), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize='x-large')
    ax.legend(loc='upper left', fontsize='x-large')
    plt.draw()
    plt.pause(0.001)


def main():
    path = r"D:\project\stroke_segmentation\image"
    name = r"扳"
    src = Image.open(path + "/" + name + "/" + name +"_skeleton.png")
    tar = Image.open(path + "/" + name + "_tar/" + name +"_tar_skeleton.png")
    src = np.array(src)
    tar = np.array(tar)
    with open(path +"/" + name + "/ap.txt", "w") as f:
        for i in range(src.shape[0]):
            for j in range(src.shape[1]):
                if src[i][j] == False:
                    f.write("{}".format(j))
                    f.write((" "))
                    f.write("{}".format(i))
                    f.write(" ")
                    f.write("")
                    f.write("\n")
    with open(path + "/" + name + "_tar/ap.txt", "w") as f:
        for i in range(tar.shape[0]):
            for j in range(tar.shape[1]):
                if tar[i][j] == False:
                    f.write("{}".format(j))
                    f.write((" "))
                    f.write("{}".format(i))
                    f.write(" ")
                    f.write("")
                    f.write("\n")


    X = np.loadtxt(path +"/" + name + "/ap.txt")
    Y = np.loadtxt(path + "/" + name + "_tar/ap.txt")
    for i in range(X.shape[0]):
        X[i][0] = X[i][0]/250
        X[i][1] = X[i][1] /320
    for j in range(Y.shape[0]):
        Y[j][0] = Y[j][0] / 250
        Y[j][1] = Y[j][1] / 320

    # fig = plt.figure()
    # fig.add_axes([0, 0, 1, 1])
    # callback = partial(visualize, ax=fig.axes[0])

    # reg = RigidRegistration(**{'X': X, 'Y': Y})
    # data, (s,r,c) = reg.register()
    reg = DeformableRegistration(**{'X': X, 'Y': Y})
    data,(s,c) = reg.register()
    plt.show()
    ############################################
    fig = plt.figure()
    ax = fig.gca(projection="3d")
    ax.scatter(Y[:, 0], Y[:, 1])
    # ax.scatter(X[:, 0], X[:, 1])
    ax.scatter(data[:, 0], data[:, 1])
    ax.scatter(X[:, 0], X[:, 1])
    plt.show()



    for i in range(X.shape[0]):
        X[i][0] = X[i][0]*250
        X[i][1] = X[i][1]*320
    for j in range(Y.shape[0]):
        data[j][0] = data[j][0]*250
        data[j][1] = data[j][1]*320


    mimg = np.zeros((300, 300))
    for i in range(data.shape[0]):
        mimg[int(data[i][1])][int(data[i][0])] = 255
    for i in range(X.shape[0]):
        mimg[int(X[i][1])][int(X[i][0])] = 255

    mimg = Image.fromarray(mimg)
    mimg = mimg.convert("L")
    mimg.save(path +"/" + name + "_tar/skm.png")

if __name__ == '__main__':
    main()
