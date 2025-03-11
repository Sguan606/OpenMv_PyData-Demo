# OpenMv_PyData-Dmeo
It mainly revolves around image processing, color detection, and circle detection, using the OpenMV camera module and Python programming. Part of the code also incorporates a Kalman filter for target tracking and prediction.


##【max_mindata】YuanXin_to_Color.py:
该代码通过摄像头检测圆形，并根据颜色阈值判断是否为特定颜色的圆。
使用Hough变换检测圆形，并根据LAB颜色空间中的阈值过滤圆形。
如果检测到的圆形符合颜色阈值，则绘制绿色圆，否则绘制白色圆。

#All_in.py:
该代码结合了颜色检测、圆形检测和卡尔曼滤波。
首先通过颜色阈值检测特定颜色的区域，然后在区域内检测圆形。
使用卡尔曼滤波器对检测到的圆形进行跟踪和预测，绘制预测的圆形和中心点。

#Color_FindTest.py:
该代码通过颜色阈值检测图像中的色块，并根据色块的形状绘制矩形或圆形。
如果色块的伸长率大于0.5，则绘制边缘和轴线，否则绘制圆形。

#Color_to_YuanXin.py:
该代码通过颜色阈值检测红色区域，并在红色区域内检测圆形。
如果检测到的圆形位于红色区域内，则绘制绿色圆，否则绘制白色圆。

#GonChuan_Sai.py:
该代码检测红、绿、蓝三种颜色的区域，并在每种颜色的区域内检测圆形。
使用卡尔曼滤波器对每种颜色的圆形进行跟踪和预测，绘制预测的圆形和中心点。

#helloworld_1.py:
这是一个简单的示例代码，展示了如何初始化摄像头并拍摄图像。
代码还展示了如何将图像垂直翻转并显示。

#Rgb565_color_tracking.py:
该代码自动学习图像中心区域的颜色阈值，并使用该阈值跟踪特定颜色的物体。
在图像中绘制检测到的色块和中心点。

#untitled_code.py:
该代码通过摄像头检测特定区域内的色块，并根据检测结果发送数据。
使用串口通信发送检测结果，并在图像中绘制检测区域和结果。

#YuanXin_FindTest.py:
该代码通过Hough变换检测图像中的圆形，并绘制检测到的圆形。
输出检测到的圆形的坐标、半径和强度。

#YuanXin_to_Color.py:
该代码通过Hough变换检测圆形，并根据颜色阈值判断是否为特定颜色的圆。
如果检测到的圆形符合颜色阈值，则绘制绿色圆，否则绘制白色圆。
