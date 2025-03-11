# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor
import image
import time

# 初始化摄像头
sensor.reset()  # 复位并初始化传感器
sensor.set_pixformat(sensor.RGB565)  # 设置像素格式为 RGB565
sensor.set_framesize(sensor.QVGA)  # 设置帧大小为 QVGA (320x240)
sensor.skip_frames(time=2000)  # 等待设置生效
clock = time.clock()  # 创建一个时钟对象来跟踪 FPS

while True:
    clock.tick()  # 更新 FPS 时钟
    img = sensor.snapshot()  # 拍摄一张照片并返回图像

    # 获取图像的字节数据
    img_bytes = img.to_bytes()

    # 创建一个新的字节数组用于存储翻转后的图像
    flipped_bytes = bytearray(len(img_bytes))

    # 图像参数
    width = img.width()
    height = img.height()
    bytes_per_pixel = 2  # RGB565 格式每个像素占 2 字节

    # 逐行翻转图像
    for y in range(height):
        for x in range(width):
            # 计算原图像和目标图像的像素位置
            src_index = (y * width + x) * bytes_per_pixel
            dst_index = ((height - 1 - y) * width + x) * bytes_per_pixel
            # 复制像素数据
            flipped_bytes[dst_index:dst_index + bytes_per_pixel] = img_bytes[src_index:src_index + bytes_per_pixel]

    # 将翻转后的字节数据写回图像
    flipped_img = image.Image(width, height, sensor.RGB565, data=flipped_bytes, copy_to_fb=True)
    img.replace(flipped_img)  # 替换当前帧缓冲区
