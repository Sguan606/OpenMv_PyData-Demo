import sensor, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_vflip(True)  #垂直方向翻转
sensor.skip_frames(time=2000)
sensor.set_auto_whitebal(True)#自动白平衡模式
sensor.set_auto_gain(False)#关闭自动增益模式
clock = time.clock()

while(True):
# 每次循环都调用 tick() 更新时钟，计算帧率
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    for c in img.find_circles(
        threshold=3500,  #设置霍夫变换的阈值,值越大,强度更高的圆才会被检测到\
        x_margin=10,  # x方向的合并误差范围，增大会使相近的圆合并。\
        y_margin=10,  # y方向的合并误差范围，增大会使相近的圆合并。\
        r_margin=10,  # 半径方向的合并误差范围，增大会使半径相近的圆合并。\
        r_min=2,  # 设置检测的最小圆半径\
        r_max=100,  # 设置检测的最大圆半径 单位是像素。100 像素对应多少毫米\
        r_step=2  # 设置检测半径时的步长，步长越小，检测的圆的精度越高，但性能消耗较大\
    ):
        img.draw_circle(c.x(), c.y(), c.r(), color=(255, 0, 0))

        print("Circle found: x = {}, y = {}, radius = {}, magnitude = \
        {}".format(c.x(), c.y(), c.r(), c.magnitude()))

    # 输出当前帧率，帮助调试和评估图像处理的性能
    print("FPS: %f" % clock.fps())
