import sensor, time
from ulab import numpy as np

color_thresholds = {
    'red':   (0, 100, 0, 127, 0, 127),
    'green': (0, 100, -128, -10, 0, 127),
    'blue':  (0, 100, -128, 127, -128, -10)}

HOUGH_THRESHOLD = 2000
MIN_RADIUS = 10
MAX_RADIUS = 50
TS = 1/60  #帧时间（假设帧率为60fps）

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_vflip(True)
# sensor.set_hmirror(True)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

class KalmanFilter:                 #卡尔曼滤波器类
    def __init__(self, initial_state):
        self.A = np.array([         #状态转移矩阵
            [1, 0, 0, 0, TS, 0],    #(位置和速度的状态转移)
            [0, 1, 0, 0, 0, TS],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]])
        self.C = np.eye(6)          #观测矩阵（单位矩阵,表示状态和观测值直接对应）
        self.Q = np.diag([1e-6]*6)  #过程噪声协方差矩阵（过程噪声较小）
        self.R = np.diag([1e-6]*6)  #观测噪声协方差矩阵（观测噪声较小）
        self.x_hat = initial_state  #初始状态估计值
        self.p = np.diag([10]*6)    #初始误差协方差矩阵

    def update(self, Z):
        x_hat_minus = np.dot(self.A, self.x_hat)                    #预测状态
        p_minus = np.dot(self.A, np.dot(self.p, self.A.T)) + self.Q #预测误差协方差

        S = np.dot(self.C, np.dot(p_minus, self.C.T)) + self.R      #计算卡尔曼增益的分母
        S_inv = np.linalg.inv(S + 1e-4*np.eye(6))            #计算逆矩阵，加入正则化项避免奇异矩阵
        K = np.dot(np.dot(p_minus, self.C.T), S_inv)                #计算卡尔曼增益
        self.x_hat = x_hat_minus + np.dot(K, (Z - np.dot(self.C, x_hat_minus)))  #更新状态估计
        self.p = np.dot((np.eye(6) - np.dot(K, self.C)), p_minus)   #更新误差协方差
        return self.x_hat

#初始化三个卡尔曼滤波器（分别对应红、绿、蓝）
kf_red = KalmanFilter(np.array([80, 60, 30, 30, 2, 2]))
kf_green = KalmanFilter(np.array([80, 60, 30, 30, 2, 2]))
kf_blue = KalmanFilter(np.array([80, 60, 30, 30, 2, 2]))

while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    #===== 在画幅中心绘制小圆环标志 =====
    img.draw_circle(80, 60, 5, color=(0, 0, 0), thickness=1)  #黑色小圆环,半径5像素
    #分别处理红、绿、蓝三种颜色
    for color, threshold in color_thresholds.items():
        #第一步：颜色阈值分割，找到当前颜色的区域
        blobs = img.find_blobs([threshold], merge=True, margin=10)  #查找当前颜色的区域

        if blobs:
            #取最大的色块
            largest_blob = max(blobs, key=lambda b: b.area())  #找到面积最大的当前颜色区域
            #绘制当前颜色的矩形框
            if color == 'red':
                rect_color = (255, 0, 0)  #红色
            elif color == 'green':
                rect_color = (0, 255, 0)  #绿色
            else:
                rect_color = (0, 0, 255)  #蓝色
            img.draw_rectangle(largest_blob.rect(), color=rect_color)  #绘制矩形框

            #第二步：在当前颜色的区域内检测圆形
            roi = (largest_blob.x(), largest_blob.y(), largest_blob.w(), largest_blob.h())
            circles = img.find_circles(
                threshold=HOUGH_THRESHOLD, #圆形检测的灵敏度
                x_margin=10,               #圆心x坐标的误差范围
                y_margin=10,               #圆心y坐标的误差范围
                r_margin=10,               #半径的误差范围
                r_min=MIN_RADIUS,          #最小半径
                r_max=MAX_RADIUS,          #最大半径
                roi=roi                    #限制检测区域为当前颜色区域
            )

            if circles:
                #筛选同心圆：取半径最大的圆（假设最外层是目标）
                valid_circles = []
                for c in circles:
                    #检查是否在色块中心附近
                    if abs(c.x() - largest_blob.cx()) < 15 and abs(c.y() - largest_blob.cy()) < 15:
                        valid_circles.append(c)

                if valid_circles:
                    target = max(valid_circles, key=lambda c: c.r()) #找到半径最大的圆
                    x, y, r = target.x(), target.y(), target.r()     #获取圆心坐标和半径
                    #绘制检测到的圆环
                    img.draw_circle(x, y, r, color=(0, 255, 0))      #绿色圆环

                    #更新卡尔曼滤波器
                    Z = np.array([x, y, 2*r, 2*r, 0, 0])#构造观测值：[x, y, w, h, dx, dy]
                    if color == 'red':
                        state = kf_red.update(Z)        #更新红色滤波器
                    elif color == 'green':
                        state = kf_green.update(Z)      #更新绿色滤波器
                    else:
                        state = kf_blue.update(Z)       #更新蓝色滤波器

                    #绘制预测结果
                    pred_x = int(state[0])    #预测的圆心x坐标
                    pred_y = int(state[1])    #预测的圆心y坐标
                    pred_r = int(state[2]/2)  #预测的半径

                    #约束圆心在当前颜色的区域内
                    blob_x, blob_y, blob_w, blob_h = largest_blob.rect()  #获取当前颜色区域的边界
                    pred_x = max(blob_x, min(blob_x + blob_w, pred_x))  #约束x坐标在当前颜色区域内
                    pred_y = max(blob_y, min(blob_y + blob_h, pred_y))  #约束y坐标在当前颜色区域内
                    pred_r = min(pred_r, min(blob_w, blob_h) // 2)  #约束半径不超过当前颜色区域大小

                    #绘制预测的圆心和圆环
                    img.draw_cross(pred_x, pred_y, color=rect_color)  #红色、绿色或蓝色十字标记圆心
                    img.draw_circle(pred_x, pred_y, pred_r, color=(255, 255, 0))  #黄色圆环

    print("FPS:", clock.fps())  #输出当前帧率
