import pygame
import sys
import time
import random

'''=====调试参数设定====='''
creat_prey_time = 0.0001 # prey输出间隔时间
max_prey_counter = 20 # 最大prey数量
max_predator_counter = 20 # 最大predator数量
prey_circle_radius = 5 # prey半径
predator_circle_radius = 10 # predator半径
capacity_counter = 4 # 节点容量

'''=====颜色预设====='''
green = 0, 255, 0
red = 255, 0, 0
black = 0, 0, 0
blue = 0, 0, 225
white = 255, 255, 255

'''=====class====='''
# 四叉树类
class QuadtreeNode:
    def __init__(self, x, y, width, height, capacity = capacity_counter, color = white):
        self.x = x          # 区域左上角x坐标
        self.y = y          # 区域左上角y坐标
        self.width = width  # 区域宽度
        self.height = height  # 区域高度
        self.capacity = capacity  # 节点容量
        self.children_list = []  # 存储子节点的列表
        self.circles_list = []    # 存储的圆对象的最小节点列表
        self.color = color

    # 可视化
    def visualization_function(self, input_color):
        pygame.draw.rect(screen, input_color, (self.x, self.y, self.width, self.height), 1) # 显示域，颜色，（坐标，边长），边宽

    # 将圆插入四叉树
    def insert(self, input_circle):
        if len(self.children_list) >= 1:
            # 尝试插入到子节点
            for child in self.children_list:
                if self._contains(input_circle, child):
                    child.insert(input_circle = input_circle)
                    return
            # 无法插入子节点则留在当前节点
            self.circles_list.append(input_circle)
        else:
            # 添加到当前节点
            self.circles_list.append(input_circle)
            # 检查是否需要分裂
            if len(self.circles_list) > self.capacity:
                self._split()
                # 重新分配当前节点的圆
                for c in self.circles_list.copy(): # 浅拷贝，此处的self.circles_list.copy内元素不会被修改
                    moved = False
                    for child in self.children_list:
                        if self._contains(circle = c, node = child):
                            child.insert(c)
                            moved = True
                            break
                    if moved == True :
                        self.circles_list.remove(c)

    # 判断圆是否完全包含在节点区域内
    def _contains(self, circle, node):
        node_left = node.x
        node_right = node.x + node.width
        node_top = node.y
        node_bottom = node.y + node.height
        
        circle_left = circle.location_x - circle.radius
        circle_right = circle.location_x + circle.radius
        circle_top = circle.location_y - circle.radius
        circle_bottom = circle.location_y + circle.radius
        
        return (circle_left >= node_left and
                circle_right <= node_right and
                circle_top >= node_top and
                circle_bottom <= node_bottom)
    
    # 分裂当前节点为四个子节点
    def _split(self):
        
        x = self.x
        y = self.y
        w = self.width / 2
        h = self.height / 2
        
        self.children_list = [
            QuadtreeNode(x, y, w, h, self.capacity, color = self.color), # 左上
            QuadtreeNode(x + w, y, w, h, self.capacity, color = self.color), # 右上
            QuadtreeNode(x, y + h, w, h, self.capacity, color = self.color), # 左下
            QuadtreeNode(x + w, y + h, w, h, self.capacity, color = self.color) # 右下
        ]

        for value in self.children_list:
            value.visualization_function(input_color = self.color)

    # 查询可能与给定圆碰撞的候选圆
    def query(self, input_circle_query, input_candidates_list):
        
        if self._intersect(input_circle_query, self) == False: # 判断圆是否与节点区域相交
            return None
        
        input_candidates_list.extend(self.circles_list)

        if len(self.children_list) == 4:
            for child in self.children_list:
                child.query(input_circle_query, input_candidates_list)

    # 判断圆是否与节点区域相交
    def _intersect(self, input_circle_intersect, node):
        
        # 计算节点边界
        node_left = node.x
        node_right = node.x + node.width
        node_top = node.y
        node_bottom = node.y + node.height
        
        # 计算圆的外接矩形
        circle_left = input_circle_intersect.location_x - input_circle_intersect.radius
        circle_right = input_circle_intersect.location_x + input_circle_intersect.radius
        circle_top = input_circle_intersect.location_y - input_circle_intersect.radius
        circle_bottom = input_circle_intersect.location_y + input_circle_intersect.radius
        
        # 判断矩形是否相交
        if (circle_left > node_right or
            circle_right < node_left or
            circle_top > node_bottom or
            circle_bottom < node_top):
            return False
        return True

# prey类
class Prey:
    def __init__(self, color, radius):
        # 初始位置
        self.location_x = random.randint(0, width)
        self.location_y = random.randint(0, height)
        self.location = [self.location_x, self.location_y]

        # 速度
        speed_list = [-1,1]
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list)

        # 颜色
        self.color = color

        # 半径
        self.radius = radius

    # 可视化
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
        
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0) # 显示域，颜色，坐标，半径，边宽

# predator类
class Predator:
    def __init__(self,color,radius):
        # 初始位置
        self.location_x = random.randint(0, width)
        self.location_y = random.randint(0, height)
        self.location = [self.location_x, self.location_y]

        # 速度
        speed_list = [-1,1]
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list)

        # 颜色
        self.color = color

        # 半径
        self.radius = radius

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
        
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0) # 显示域，颜色，坐标，半径，边宽

'''=====self_function====='''
# 使用四叉树查找所有碰撞对 **四叉树主体
def find_collisions(input_circles_total_dict, innput_color):
    if not input_circles_total_dict:
        return []
    
    # 计算场景边界
    min_x = min(Object_1.location_x - Object_1.radius for Object_1 in input_circles_total_dict.values())
    max_x = max(Object_2.location_x + Object_2.radius for Object_2 in input_circles_total_dict.values())
    min_y = min(Object_3.location_y - Object_3.radius for Object_3 in input_circles_total_dict.values())
    max_y = max(Object_4.location_y + Object_4.radius for Object_4 in input_circles_total_dict.values())
    
    # 创建四叉树
    qt = QuadtreeNode(min_x, min_y, max_x - min_x, max_y - min_y, capacity = capacity_counter ,color = innput_color)
    
    # 插入所有圆
    for value in input_circles_total_dict.values():
        qt.insert(input_circle = value)
    
    # 检测碰撞
    collisions = [] # 碰撞圆组列表
    checked = set() # 待检测候选圆元组
    
    for c_value in input_circles_total_dict.values():
        candidates_list = [] # 候选圆
        qt.query(input_circle_query = c_value, input_candidates_list = candidates_list)
        for other in candidates_list:
            if c_value is other:
                continue
            # 避免重复检测
            pair = (c_value, other) if id(c_value) < id(other) else (other, c_value)
            if pair not in checked:
                if check_collision(circle_1 = c_value, circle_2 = other):
                    collisions.append(pair)
                    checked.add(pair)
    return collisions

# 终端输出
def output_function(input_dict):
    print(input_dict.items()) # 输出字典集

    for value in input_dict.values():
        print(value.location)

# 检测两个圆是否碰撞
def check_collision(circle_1, circle_2):
    
    dx = circle_1.location_x - circle_2.location_x
    dy = circle_1.location_y - circle_2.location_y
    distance_sq = dx*dx + dy*dy
    radius_sum = circle_1.radius + circle_2.radius
    return distance_sq <= radius_sum*radius_sum

'''=====body====='''
# 初始化
pygame.init()

# 窗体设置
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# prey字典创建
dynamic_variables_prey = {}
# predator字典创建
dynamic_variables_predator = {}

# 时间生成变量
counter_prey = 1
counter_predator = 1
last_time = time.time()

'''=====loop====='''
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
                exit()

    # 生成predator
    if len(dynamic_variables_predator) < max_predator_counter: # 最大生成数限制条件

        # 动态生成 key 名
        instance_name = f'instance_{counter_predator}' 
        # 直接存储到字典中
        dynamic_variables_predator[instance_name] = Prey(color = "red", radius = predator_circle_radius)  

        counter_predator = counter_predator + 1

    # 执行predator四叉树算法
    collisions_predator = find_collisions(input_circles_total_dict = dynamic_variables_predator ,innput_color = red)

    # 时间计数生成prey
    if len(dynamic_variables_prey) < max_prey_counter: # 最大生成数限制条件
        current_time = time.time()
        if current_time - last_time >= creat_prey_time: # 间隔多少秒生成一个对象

            # 动态生成 key 名
            instance_name = f'instance_{counter_prey}' 
            # 直接存储到字典中
            dynamic_variables_prey[instance_name] = Prey(color = "green", radius = prey_circle_radius)  

            counter_prey = counter_prey + 1
            last_time = time.time()

    # 执行prey四叉树算法
    collisions_prey = find_collisions(input_circles_total_dict = dynamic_variables_prey, innput_color = green)  


    # 遍历字典中每一个value并且执行value的class函数move_function()（实现刷新）
    for value in dynamic_variables_prey.values():
        value.move_function()
    
    for value in dynamic_variables_predator.values():
        value.move_function()

    '''=====print====='''
    # 打印四叉树结果
    if len(collisions_prey) >=1:
        print(f"prey_发现 {len(collisions_prey)} 组碰撞：")
        for c1, c2 in collisions_prey:
            print(f"({c1.location_x}, {c1.location_y}, r={c1.radius})({c2.location_x}, {c2.location_y}, r={c2.radius})") 

    if len(collisions_predator) >=1:
        print(f"predator_发现 {len(collisions_predator)} 组碰撞：")
        for c1, c2 in collisions_predator:
            print(f"({c1.location_x}, {c1.location_y}, r={c1.radius})({c2.location_x}, {c2.location_y}, r={c2.radius})") 


    time.sleep(0.01)
    pygame.display.update()
