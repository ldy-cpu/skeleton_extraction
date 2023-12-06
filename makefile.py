import os
import shutil
oldpath = r'D:\project\stroke_segmentation\image\完美骨架'


f = os.listdir(oldpath)
for im in f:
    im = im[0:-4]
    if not os.path.exists(oldpath + '/' + im):
        os.mkdir(oldpath + '/' + im)
    shutil.move(oldpath + '/' + im + '.png',oldpath + '/' + im + '/' + im + '.png')