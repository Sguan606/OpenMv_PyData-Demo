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
           img.draw_circle(c.x(), c.y(), c.r(), color=(192, 255, 0))
           print("Circle found: x = {}, y = {}, radius = {}".format(c.x(), c.y(), c.r()))
        else:
           img.draw_circle(c.x(), c.y(), c.r(), color=(255, 255, 255))
    print("FPS %f" % clock.fps())
