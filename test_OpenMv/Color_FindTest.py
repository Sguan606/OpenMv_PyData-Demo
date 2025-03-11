import sensor, time

color_threshold = (30, 100, 15, 127, 15, 127)

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
    img = sensor.snapshot()

    for blob in img.find_blobs(
        [color_threshold],
        pixels_threshold=200,
        area_threshold=200,
        merge=True,
    ):

        if blob.elongation() > 0.5:
            img.draw_edges(blob.min_corners(), color=(255, 0, 0))
            img.draw_line(blob.major_axis_line(), color=(0, 255, 0))
            img.draw_line(blob.minor_axis_line(), color=(0, 0, 255))

        else :
            radius = int(min(blob.w(), blob.h()) / 2)
            img.draw_circle(blob.cx(), blob.cy(), radius, color=(255, 0, 0))

            print("Circle found: x = {}, y = {}, radius = {}, \
            ".format(blob.cx(), blob.cy(), radius))

        img.draw_cross(blob.cx(), blob.cy())
    print(clock.fps())
