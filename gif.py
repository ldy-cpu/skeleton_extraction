# from PIL import Image
# import os
# gifFileName = 'C:/Users/Ldy/Desktop/1111.gif'
# #使用Image模块的open()方法打开gif动态图像时，默认是第一帧
# im = Image.open(gifFileName)
# pngDir = gifFileName[:-4]
# #创建存放每帧图片的文件夹
# os.mkdir(pngDir)
# try:
#   while True:
#     #保存当前帧图片
#     current = im.tell()
#     im.save(pngDir+'/'+str(current)+'.png')
#     #获取下一帧图片
#     im.seek(current+1)
# except EOFError:
#     pass

# import cv2
# from PIL import ImageFont, ImageDraw, Image
# import numpy as np
# for i in range(26):
#   bk_img = cv2.imread("C:/Users/Ldy/Desktop/1111/{}.png".format(i))
#   #设置需要显示的字体
#   fontpath = "C:/Users/Ldy/Desktop/1111/No.130-ShangShouZhuiGuangShouXieTi-2.ttf"
#   font = ImageFont.truetype(fontpath, 32)
#   img_pil = Image.fromarray(bk_img)
#   draw = ImageDraw.Draw(img_pil)
#   #绘制文字信息
#   draw.text((25, 160),  "熊宝儿好熊宝儿好\n熊宝儿可爱是个宝", font = font, fill = (255, 255, 255))
#   bk_img = np.array(img_pil)
#
#   # cv2.imshow("add_text",bk_img)
#   # cv2.waitKey()
#   cv2.imwrite("C:/Users/Ldy/Desktop/1111/done{}.png".format(i),bk_img)

from PIL import Image
im=Image.open("C:/Users/Ldy/Desktop/1111/done0.png")
images=[]
images.append(Image.open('C:/Users/Ldy/Desktop/1111/done0.png'))
images.append(Image.open('C:/Users/Ldy/Desktop/1111/done0.png'))
images.append(Image.open('C:/Users/Ldy/Desktop/1111/done0.png'))
for i in range(1,26):
  images.append(Image.open('C:/Users/Ldy/Desktop/1111/done{}.png'.format(i)))
  images.append(Image.open('C:/Users/Ldy/Desktop/1111/done{}.png'.format(i)))
  images.append(Image.open('C:/Users/Ldy/Desktop/1111/done{}.png'.format(i)))
  images.append(Image.open('C:/Users/Ldy/Desktop/1111/done{}.png'.format(i)))
im.save('C:/Users/Ldy/Desktop/1111/done.gif', save_all=True, append_images=images,loop=2,duration=0.5,comment=b"aaabb")