import sensor, time
from ulab import numpy as np

color_threshold = (0, 100, 0, 127, 0, 127)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_vflip(True)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

position_threshold = 4
radius_threshold = 4
MAX_CHANGE_THRESHOLD = 80
prev_x, prev_y, prev_r = None, None, None
threshold_calculated = False
threshold_roi = (70,50,20,20)

def get_threshold(roi):
    threshold = [0, 0, 0, 0, 0, 0]
    for _ in range(150):
        img = sensor.snapshot()
        hist = img.get_histogram(roi=roi)
        img.draw_rectangle(roi, color=(0, 255, 0), thickness=2)
        img.draw_string(roi[0], roi[1] - 10, "Collecting Threshold...",\
        color=(0, 255, 0), scale=1)
        lo = hist.get_percentile(0.05)
        hi = hist.get_percentile(0.95)
        print("采集计算阈值中...请等待")
        threshold[0] = (threshold[0] + lo.l_value()) // 2
        threshold[1] = (threshold[1] + hi.l_value()) // 2
        threshold[2] = (threshold[2] + lo.a_value()) // 2
        threshold[3] = (threshold[3] + hi.a_value()) // 2
        threshold[4] = (threshold[4] + lo.b_value()) // 2
        threshold[5] = (threshold[5] + hi.b_value()) // 2
    print(f"计算阈值的位置区域是 ROI Info: x={roi[0]}, y={roi[1]}, \
    width={roi[2]}, height={roi[3]}")
    print("计算出的阈值  Threshold: Lmin={0} Lmax={1}, \
    Amin={2} Amax={3}, Bmin={4} Bmax={5}".format(
    threshold[0], threshold[1], threshold[2], threshold[3], threshold[4], threshold[5]))
    return threshold

Ts = 1/12 #Ts = 1 帧率的倒数
A = np.array([[1, 0, 0, 0, Ts, 0],
              [0, 1, 0, 0, 0, Ts],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 1]])
C = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],\
[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]])
Q_value = [1e-6 for _ in range(6)]
Q = np.diag(Q_value)
R_value = [1e-6 for _ in range(6)]
R = np.diag(R_value)

x = 0
y = 0
last_frame_x = x
last_frame_y = y
w = 0
h = 0
dx = 0
dy = 0
Z = np.array([x,y,w,h,dx,dy])
x_hat = np.array([80, 60, 30, 30, 2, 2])
x_hat_minus = np.array([0,0,0,0,0,0])
p_value = [10 for _ in range(6)]
p = np.diag(p_value)

def Kalman_Filter(Z):
    global A,C,Q,R,x_hat,x_hat_minus,p
    x_hat_minus = np.dot(A,x_hat)
    p_minus = np.dot(A, np.dot(p, A.T)) + Q
    S = np.dot(np.dot(C, p_minus), C.T) + R
    regularization_term = 1e-4
    S_regularized = S + regularization_term * np.eye(S.shape[0])
    S_inv = np.linalg.inv(S_regularized)
    K = np.dot(np.dot(p_minus, C.T), S_inv)
    x_hat = x_hat_minus + np.dot(K,(Z - np.dot(C,x_hat_minus)))
    p = np.dot((np.eye(6) - np.dot(K,C)),p_minus)
    return x_hat
last_frame_location = [0 for _ in range(4)]
last_frame_rect = [0 for _ in range(4)]
box = [0 for _ in range(4)]


while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    if not threshold_calculated:#获取指定位置阈值-进行阈值计算的内容
        color_threshold = get_threshold(threshold_roi)
        threshold_calculated = True

    for c in img.find_circles(
        threshold = 2500,  # 设置圆形检测的阈值,较高意味着需更明显圆才能被检测到
        x_margin = 10,     # 圆心的X坐标允许的误差范围
        y_margin = 10,     # 圆心的Y坐标允许的误差范围
        r_margin = 10,     # 圆半径的允许误差范围
        r_min = 2,         # 圆的最小半径 单位为像素
        r_max = 100,       # 圆的最大半径 单位为像素
        r_step = 2):       # 圆半径变化的步长 单位像素
        area = (c.x() - c.r(), c.y() - c.r(), 2 * c.r(), 2 * c.r())  # (x, y, width, height)
        statistics = img.get_statistics(roi=area)

        if (
            color_threshold[0] < statistics.l_mode() < color_threshold[1] and
            color_threshold[2] < statistics.a_mode() < color_threshold[3] and
            color_threshold[4] < statistics.b_mode() < color_threshold[5] ):
            x, y, r = c.x(), c.y(), c.r()
            if prev_x is None or prev_y is None or prev_r is None:
                prev_x, prev_y, prev_r = x, y, r  #更新上次的位置值
                img.draw_circle(x, y, r, color=(192, 255, 0)) #绘制圆为绿色
                # 输出圆心坐标和半径
                print("第一次检测       First detection: center_x = {}, \
                center_y = {}, radius = {}".format(x, y, r))
                circle_center_x = x
                circle_center_y = y
                circle_radius = r
            else:
                x_change = abs(x - prev_x)
                y_change = abs(y - prev_y)
                r_change = abs(r - prev_r)
                if (
                    (x_change > position_threshold or y_change > \
                    position_threshold or r_change > radius_threshold) and
                    (x_change <= MAX_CHANGE_THRESHOLD and y_change <= \
                    MAX_CHANGE_THRESHOLD and r_change <= MAX_CHANGE_THRESHOLD)):
                    prev_x, prev_y, prev_r = x, y, r
                    img.draw_circle(x, y, r, color=(192, 255, 0))
                    print("更新检测       Updated detection: center_x = \
                    {}, center_y = {}, radius = {}".format(x, y, r))
                    circle_center_x = x
                    circle_center_y = y
                    circle_radius = r
                else :
                    img.draw_circle(prev_x, prev_y, prev_r, color=(192, 255, 0))
                    print("没有显著变化 No significant change: center_x = \
                    {}, center_y = {}, radius = {}".format(prev_x, prev_y, prev_r))
                    circle_center_x = prev_x
                    circle_center_y = prev_y
                    circle_radius = prev_r
            rect_x = int(circle_center_x - circle_radius)
            rect_y = int(circle_center_y - circle_radius)
            rect_w = int(2 * circle_radius)
            rect_h = int(2 * circle_radius)
            rect = [rect_x, rect_y, rect_w, rect_h]

            box = [rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]]
            x, y, w, h = rect[0], rect[1], rect[2], rect[3]
            dx = (x - last_frame_x) / Ts
            dy = (y - last_frame_y) / Ts
            Z = np.array([x, y, w, h, dx, dy])
            x_hat = Kalman_Filter(Z)
            last_frame_x, last_frame_y = x, y
            last_frame_rect = rect
            last_frame_location = box

        else:
            x,y,w,h = (x_hat[0] + (x_hat[4] * Ts)),(x_hat[1] + (x_hat[5] * Ts)),x_hat[2],x_hat[3]
            dx = (x - last_frame_x) / Ts
            dy = (y - last_frame_y) / Ts
            Z = np.array([x, y, w, h, dx, dy])
            x_hat = Kalman_Filter(Z)
            last_frame_x, last_frame_y = x, y
            last_frame_rect = [x,y,w,h]
            last_frame_location = [x,y,(x + w),(y + h)]
    predicted_rect = [
        int(x_hat[0]),
        int(x_hat[1]),
        int(x_hat[2]),
        int(x_hat[3])]
    img.draw_rectangle(predicted_rect, color=(100, 100, 100))
    center_x = int(x_hat[0] + x_hat[2] / 2)
    center_y = int(x_hat[1] + x_hat[3] / 2)
    radius = int(min(x_hat[2], x_hat[3]) / 2)
    print("卡尔曼计算       Predicted Circle: center_x = {}, center_y = \
    {}, radius = {}".format(center_x, center_y, radius))

    print("FPS %f" % clock.fps()) #输出当前的帧率

