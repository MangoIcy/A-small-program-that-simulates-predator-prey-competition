import pygame
import sys
import time
import random

'''=====class====='''
# 四叉树类
class QuadtreeNode:
    def __init__(self, x, y, width, height, capacity = 4):
        self.x = x          # 区域左上角x坐标
        self.y = y          # 区域左上角y坐标
        self.width = width  # 区域宽度
        self.height = height  # 区域高度
        self.capacity = capacity  # 节点容量
        self.children_list = None  # 子节点
        self.circles_list = []    # 存储的圆对象

    # 可视化
    def visualization_function(self):
        pygame.draw.rect(screen, white, (self.x, self.y, self.width, self.height), 1) # 显示域，颜色，（坐标，边长），边宽

    # 将圆插入四叉树
    def insert(self, input_circle):
        if self.children_list is not None:
            # 尝试插入到子节点
            for child in self.children_list:
                if self._contains(input_circle, child):
                    child.insert(input_circle)
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
            QuadtreeNode(x, y, w, h, self.capacity),       # 左上
            QuadtreeNode(x + w, y, w, h, self.capacity),   # 右上
            QuadtreeNode(x, y + h, w, h, self.capacity),   # 左下
            QuadtreeNode(x + w, y + h, w, h, self.capacity) # 右下
        ]

        for value in self.children_list:
            value.visualization_function()

    # 查询可能与给定圆碰撞的候选圆
    def query(self, input_circle_query, found_query_input_list):
        
        if not self._intersect(input_circle_query, self): # 判断圆是否与节点区域相交
            return
        
        found_query_input_list.extend(self.circles_list)
        
        if self.children_list is not None:
            for child in self.children_list:
                child.query(input_circle_query, found_query_input_list)

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

# 被捕食者类
class Object:
    def __init__(self,color,radius = 2):
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

'''=====function====='''
# 使用四叉树查找所有碰撞对 **四叉树主体
def find_collisions(input_circles):
    if not input_circles:
        return []
    
    # 计算场景边界
    min_x = min(Object_1.location_x - Object_1.radius for Object_1 in dynamic_variables_prey.values())
    max_x = max(Object_2.location_x + Object_2.radius for Object_2 in dynamic_variables_prey.values())
    min_y = min(Object_3.location_y - Object_3.radius for Object_3 in dynamic_variables_prey.values())
    max_y = max(Object_4.location_y + Object_4.radius for Object_4 in dynamic_variables_prey.values())
    
    # 创建四叉树
    qt = QuadtreeNode(min_x, min_y, max_x - min_x, max_y - min_y, capacity = 4)
    
    # 插入所有圆
    for value in dynamic_variables_prey.values():
        qt.insert(input_circle = value)
    
    # 检测碰撞
    collisions = [] # 碰撞圆列表

    checked = set()
    for c_value in input_circles.values():
        candidates_list = [] # 候选圆
        qt.query(input_circle_query = c_value, found_query_input_list = candidates_list)
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
# 颜色预设
green = 0, 255, 0
red = 255, 0, 0
black = 0, 0, 0
white = 255, 255, 255

# 初始化
pygame.init()

# 窗体设置
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

#被捕食者字典创建
dynamic_variables_prey = {}
counter_prey = 1
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

    # 生成测试球
    if counter_prey <= 100:
        instance_name = f'prey_{counter_prey}' # 生成一个变化的字符串
        dynamic_variables_prey[instance_name] = Object(color = green) # 直接存储到字典中

        counter_prey = counter_prey + 1
        last_time = time.time()

    # 执行四叉树算法
    collisions = find_collisions(dynamic_variables_prey)
    
    # 输出总代码段
    if counter_prey == 101:


        '''
        print('=====以下为数据输出：=====')        
        for value in dynamic_variables_prey.values():
            print(value.location)

        # 打印四叉树结果
        print(f"发现 {len(collisions)} 组碰撞：")
        for c1, c2 in collisions:
            print(f"圆({c1.location_x}, {c1.location_y}, r={c1.radius}) 和 圆({c2.location_x}, {c2.location_y}, r={c2.radius})")            

        # output_function(dynamic_variables_prey)
        '''

    # 遍历字典中每一个value并且执行value的class函数move_function()（实现刷新）
    for value in dynamic_variables_prey.values():
        value.move_function()



    time.sleep(0.1)
    pygame.display.update()