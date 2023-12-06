import os

from PIL import Image
import numpy as np
def xia(path):
    cmb = [0,3,5,7]
    L_ = Image.open(path+'/L_暇_SKp.png')
    L_ = np.array(L_)
    LU = []
    Lset = []
    for i in range(L_.shape[0]):
        for j in range(L_.shape[1]):
            if L_[i][j] == 255:
                LU.append(i**2 + j**2)
                Lset.append((i,j))
    LU = np.array(LU)
    ori = LU
    print(LU)
    LU = np.argsort(LU).astype(np.int32)
    print(LU)
    return LU,Lset,cmb,ori


def combineL(path):
    LU,Lset,cmb,ori = xia(path)


    ff = 0
    for L in Lset:
        for s in cmb:
            f = os.listdir(path + '/stroke')
            if L[0]**2 + L[1]**2 == ori[LU[s]]:
                print('此点组合:',L[1],L[0])
                img = Image.open(path + '/stroke/' + f[0])
                img = np.array(img)
                cp = np.ones((img.shape[0], img.shape[1]), bool)
                for k in f:
                    st = Image.open(path + '/stroke/' + k)
                    st = np.array(st)
                    if st[L[0]][L[1]] == False:
                        for i in range(st.shape[0]):
                            for j in range(st.shape[1]):
                                if st[i][j] == False:
                                    cp[i][j] = False
                        os.remove(path+ '/stroke/'+ k)
                cp = Image.fromarray(cp)
                ff += 1
                cp.save(path + '/stroke/{}_Lcmb.png'.format(ff))





name = '暇_SKp'
path = r'./image/完美骨架已完成/' + name
combineL(path)