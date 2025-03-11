import sensor, time

color_threshold = (30, 100, 15, 127, 15, 127)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_vflip(True)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

position_threshold = 4
radius_threshold = 4
MAX_CHANGE_THRESHOLD = 80

prev_x, prev_y, prev_r = None, None, None


while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)

    for c in img.find_circles(
        threshold = 2500,
        x_margin = 10,
        y_margin = 10,
        r_margin = 10,
        r_min = 2,
        r_max = 100,
        r_step = 2
    ):
        area = (c.x() - c.r(), c.y() - c.r(), 2 * c.r(), 2 * c.r())
        statistics = img.get_statistics(roi=area)

        if (
           color_threshold[0] < statistics.l_mode() < color_threshold[1] and
           color_threshold[2] < statistics.a_mode() < color_threshold[3] and
           color_threshold[4] < statistics.b_mode() < color_threshold[5]
        ):
            x, y, r = c.x(), c.y(), c.r()
            if prev_x is None or prev_y is None or prev_r is None:
                prev_x, prev_y, prev_r = x, y, r  #更新上次的位置值
                img.draw_circle(x, y, r, color=(192, 255, 0)) #绘制圆为绿色
            else:
                x_change = abs(x - prev_x)#计算这次值和上次值 的绝对值
                y_change = abs(y - prev_y)
                r_change = abs(r - prev_r)

                if ((x_change > position_threshold or
                y_change > position_threshold or
                r_change > radius_threshold) and
                (x_change <= MAX_CHANGE_THRESHOLD and
                y_change <= MAX_CHANGE_THRESHOLD and
                r_change <= MAX_CHANGE_THRESHOLD)):
                    prev_x, prev_y, prev_r = x, y, r
                    img.draw_circle(x, y, r, color=(192, 255, 0))
                    print("Circle found: x = {}, y = {}, radius = {}".\
                    format(x, y, r))
                else :
                    img.draw_circle(prev_x, prev_y, prev_r, color=(192, 255, 0))
                    print("Circle found: x = {}, y = {}, radius = {}".\
                    format(prev_x, prev_y, prev_r))


        else:
           img.draw_circle(c.x(), c.y(), c.r(), color=(255, 255, 255))
    print("FPS %f" % clock.fps())


