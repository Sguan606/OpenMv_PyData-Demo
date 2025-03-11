import sensor, time

red_threshold = [(30, 100, 15, 127, 15, 127)]

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_vflip(True)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)     #关闭自动增益，让颜色跟踪不受环境光影响，避免图像质量变化
sensor.set_auto_whitebal(False) #关闭自动白平衡，确保颜色跟踪不受环境光和白平衡影响
clock = time.clock()

while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)

    blobs = img.find_blobs(red_threshold, pixels_threshold=100,\
    area_threshold=100, merge=True)

    for blob in blobs:
        area = (blob.x(), blob.y(), blob.w(), blob.h())
        statistics = img.get_statistics(roi=area)
        circles = img.find_circles(
            threshold = 2500,
            x_margin = 10,
            y_margin = 10,
            r_margin = 10,
            r_min = 2,
            r_max = 100,
            r_step = 2)
        for c in circles:
            if blob.x() <= c.x() <= blob.x() + blob.w() and\
            blob.y() <= c.y() <= blob.y() + blob.h():
                img.draw_circle(c.x(), c.y(), c.r(), color=(192, 255, 0))
                print("Circle found: x = {}, y = {}, radius = {}".format(c.x(),\
                c.y(), c.r()))
            else:
                img.draw_circle(c.x(), c.y(), c.r(), color=(255, 255, 255))


    print("FPS %f" % clock.fps())
