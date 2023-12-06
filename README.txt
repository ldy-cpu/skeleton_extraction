适用于seg_with_harris,对之前的s1,s2，segmentation3无效

建库:
0.运行zs，将filename换位汉字名
1.运行seg_with_harris.py，name换成 汉字名(角点检测方法有待优化，参数待调)，将harris函数tar模块注释,不断调整q,w,e使检测效果最佳。
2.运行match.py 1代码块，2，3注释,name改为此汉字名称
3.运行save_src_stroke.py,name改为此汉字名称,打开src.txt文件，按笔画顺序写fill，将每个笔画覆盖的关键点在src.txt文件里的索引填入

使用：
0.运行zs，将filename换位汉字名_tar,把模板字的名字暂时改成汉字名_tar
1.运行seg_with_harris.py，name换成 汉字名_tar，将harris函数src模块注释。
2.运行match.py 2，3代码块，1注释,name改为此汉字名称
3.运行combine.py,修改name,(注意每个点中保存的那个点，才是要对比的，并不是这个点自身,此数组存在point_in_point.npy)


修改了polyfit.py.curvature 求曲率方法，计算角度改变的长度按笔画长度一定比例截取，除以的微分统一为0.02
thr1改为0.94