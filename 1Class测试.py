import pygame
import sys
import time
import random

class Object:
    def __init__(self,color):
        # 初始位置
        self.location_x = random.randint(0,width)
        self.location_y = random.randint(0,height)

        # 速度
        speed_list = [-1,1]
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list)

        # 颜色
        self.color = color

    def move_function(self):
        # 位置信息更新
        self.location_x = self.location_x + self.speed_x
        self.location_y = self.location_y + self.speed_y
        self.location = [self.location_x,self.location_y]

        # 边界检测
        if self.location_x >= width:
            self.speed_x = -1
        if self.location_x <= 0:
            self.speed_x = 1

        if self.location_y >= height:
            self.speed_y = -1
        if self.location_y <= 0:
            self.speed_y = 1

        # 绘制
        pygame.draw.circle(screen,self.color,self.location,5,0)

# 颜色预设
green = 0,255,0
red = 255,0,0
black = 0,0,0

# 初始化
pygame.init()

# 窗体设置
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

#对象创建
dynamic_variables = {}
counter = 1
last_time = time.time()

# 循环体
while True:

    screen.fill(black)

    # 退出程序
    for event in pygame.event.get():
        # 叉退出
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            # ESC退出
            if event.key == pygame.K_ESCAPE:
                for key in dynamic_variables:
                    print(key)
                exit()

    # 1秒时间计数
    current_time = time.time()
    if current_time - last_time >= 1: # 间隔多少秒生成一个对象

        # 动态生成 key 名
        instance_name = f'instance_{counter}' 
        # 直接存储到字典中
        dynamic_variables[instance_name] = Object(color="green")  

        counter = counter + 1
        last_time = time.time()

    # 遍历字典中每一个value并且执行value的class函数move_function()
    for value in dynamic_variables.values():
        value.move_function()

    time.sleep(0.001)
    pygame.display.update()