import pygame
import sys
import time
import random

'''=====调试参数设定====='''
creat_prey_time = 0.0001 # prey输出间隔时间
max_predator_counter = 10 # 最大predator数量
max_prey_counter = 10 # 最大prey数量
predator_circle_radius = 10 # predator半径
prey_circle_radius = 10 # prey半径
capacity_counter = 4 # 节点容量
screen_width, screen_height = 800, 600 # 窗体大小
speed = 1

'''=====color====='''
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 225

'''=====class====='''
class Predator: # Predator类创建
    def __init__(self, predator_color, predator_radius):
        # 位置
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.location = [self.x, self.y]
        # 速度
        speed_list = [-speed,speed]
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list) 
        # 颜色及半径
        self.color = predator_color
        self.radius = predator_radius

    def move_function(self): # 运动函数
        # 边界检测
        if self.x + self.radius >= screen_width:
            self.speed_x = -speed
        if self.x - self.radius <= 0:
            self.speed_x = speed
        if self.y + self.radius >= screen_height:
            self.speed_y = -speed
        if self.y - self.radius <= 0:
            self.speed_y = speed

        self.x = self.x + self.speed_x
        self.y = self.y + self.speed_y

        self.location = [self.x, self.y]

    def draw_function(self): # 可视化函数
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0) # 显示域，颜色，坐标，半径，边宽

class Prey: # Prey类创建
    def __init__(self, prey_color, prey_radius):
        # 位置
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.location = [self.x, self.y]
        # 速度
        speed_list = [-speed,speed]
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list) 
        # 颜色及半径
        self.color = prey_color
        self.radius = prey_radius

    def move_function(self): # 运动函数
        # 边界检测
        if self.x + self.radius >= screen_width:
            self.speed_x = -speed
        if self.x - self.radius <= 0:
            self.speed_x = speed
        if self.y + self.radius >= screen_height:
            self.speed_y = -speed
        if self.y - self.radius <= 0:
            self.speed_y = speed

        self.x = self.x + self.speed_x
        self.y = self.y + self.speed_y

        self.location = [self.x, self.y]

    def draw_function(self): # 可视化函数
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0) # 显示域，颜色，坐标，半径，边宽

class QuadtreeNode: # 四叉树节点类创建
    def __init__(self, node_x, node_y, node_width, node_height, node_capacity = capacity_counter):
        # 空间位置参数
        self.node_x = node_x
        self.node_y = node_y
        self.node_width = node_width
        self.node_height = node_height

        # 容器性质参数
        self.node_capacity = node_capacity
        self.object_list = [] # 存储节点内predator/prey对象的value，若该节点被切分，则该节点参数object_in_node_list为空列表或包含边界objec，元素为value值
        self.subnode_list = [] # 若给节点被切分，则存储该节点下的子节点，元素为QuadtreeNode的value值，只有两种状态，空，四个子节点

    '''四叉树可视化函数'''
    def visualization_function(self, input_color):
        pygame.draw.rect(screen, input_color, (self.node_x, self.node_y, self.node_width, self.node_height), 1) # 显示域，颜色，（坐标，边长），边宽

    '''插入object并分配函数'''
    def insert_object_function(self, insert_input_object_value):
        # 若父节点的子节点列表中有子节点，即父节点已被分裂，则直接插入到子节点中
        if len(self.subnode_list) == 4:

            for subnode_value in self.subnode_list:

                if self.whether_node_contains_object_function(insert_input_object_value, subnode_value):

                    subnode_value.insert_object_function(insert_input_object_value = insert_input_object_value) # 若被完全纳入其中，则执行insert函数，循环往复直到插入没有被分裂子节点object_in_node_list列表中
                    return
                
            self.object_list.append(insert_input_object_value)

        #父节点的子节点列表中没有子节点，则现将其插入到object_in_node_list，直到溢出产出分裂
        else: 
            # 插入object到该节点的object_in_node_list列表
            self.object_list.append(insert_input_object_value)

            # 判断该节点内object是否大于node.capacity，是否该分裂
            if len(self.object_list) > self.node_capacity: # 发生分裂，需要object再分配
                self.split_node_function() # 创建子节点

                # 对已经存储在父节点的object_in_node_list中的object再分配
                for object_value in self.object_list.copy(): # 遍历object
                    move = False
                    # 判断该object完全在哪个subnode内
                    for subnode_value in self.subnode_list: # 遍历subnode

                        if self.whether_node_contains_object_function(input_object = object_value, input_check_subnode = subnode_value):
                            subnode_value.insert_object_function(insert_input_object_value = object_value) # 若其完全在子节点中，则将其置入子节点object列表
                            move = True
                            break # 对后续的子节点不用遍历了，节约计算资源
                    if move == True:
                        self.object_list.remove(object_value) # 将其从父节点object列表舍弃，若已经插入的object遍历完sunnode后无法插入，则将其保留在父节点

    '''判断object是否完全包含在节点区域内函数'''
    def whether_node_contains_object_function(self, input_object, input_check_subnode):
        checking_subnode_left = input_check_subnode.node_x
        checking_subnode_right = input_check_subnode.node_x + input_check_subnode.node_width
        checking_subnode_top = input_check_subnode.node_y
        checking_subnode_bottom = input_check_subnode.node_y + input_check_subnode.node_height

        object_left = input_object.x - input_object.radius
        object_right = input_object.x + input_object.radius
        object_top = input_object.y - input_object.radius
        object_bottom = input_object.y + input_object.radius

        return (object_left >= checking_subnode_left and
                object_right <= checking_subnode_right and
                object_top >= checking_subnode_top and
                object_bottom <= checking_subnode_bottom)

    '''节点分割函数'''
    def split_node_function(self):
        # 根据父节点的参数值计算子节点空间位置参数值
        subnode_x = self.node_x
        subnode_y = self.node_y
        subnode_w = self.node_width / 2
        subnode_h = self.node_height / 2

        # 创建四个新的节点，将父节点的子节点存储列表变化为（因为subnode_in_node_list模式只有两种，用替换节约资源，相当于存储）
        self.subnode_list = [
            QuadtreeNode(subnode_x, subnode_y, subnode_w, subnode_h), # 左上
            QuadtreeNode(subnode_x + subnode_w, subnode_y, subnode_w, subnode_h), # 右上
            QuadtreeNode(subnode_x, subnode_y + subnode_h, subnode_w, subnode_h), # 左下
            QuadtreeNode(subnode_x + subnode_w, subnode_y + subnode_h, subnode_w, subnode_h) # 右下
        ]

        # 绘制子节点
        for subnode_instance_value in self.subnode_list:
            subnode_instance_value.visualization_function(input_color = white)

    '''候选圆查询函数'''
    def query_function(self, input_object):
        candidates = []
        # 如果当前节点有子节点，递归查询子节点
        if len(self.subnode_list) == 4:
            for subnode in self.subnode_list:
                # 检查输入对象是否与子节点区域相交
                if self.check_object_overlap(input_object, subnode):
                    candidates.extend(subnode.query_function(input_object))
        # 添加当前节点的对象
        for obj in self.object_list:
            if isinstance(obj, Prey) == True:  # 确保只检测 Predator 和 Prey 的碰撞
                candidates.append(obj)
        return candidates

    '''检查对象是否与节点区域重叠'''
    def check_object_overlap(self, obj, node):
        # 检查对象是否与节点区域重叠
        obj_left = obj.x - obj.radius
        obj_right = obj.x + obj.radius
        obj_top = obj.y - obj.radius
        obj_bottom = obj.y + obj.radius

        node_left = node.node_x
        node_right = node.node_x + node.node_width
        node_top = node.node_y
        node_bottom = node.node_y + node.node_height

        return not (obj_right < node_left or 
                    obj_left > node_right or 
                    obj_bottom < node_top or 
                    obj_top > node_bottom)






'''=====self_function====='''
def find_collisions_main_body_function(input_total_dict): # 检测碰撞程序主体，返回值应为一个列表
    '''分配程序'''
    # 计算场景边界
    min_x = min(instance_value.x - instance_value.radius for instance_value in input_total_dict.values())
    max_x = max(instance_value.x + instance_value.radius for instance_value in input_total_dict.values())
    min_y = min(instance_value.y - instance_value.radius for instance_value in input_total_dict.values())
    max_y = max(instance_value.y + instance_value.radius for instance_value in input_total_dict.values())

    # 生成四叉树总节点
    total_quadtree_node = QuadtreeNode(node_x = min_x, node_y = min_y, node_width = max_x - min_x, node_height = max_y - min_y, node_capacity = capacity_counter)

    # 将object传入四叉树总结点中并切割分配
    for value in input_total_dict.values():
        total_quadtree_node.insert_object_function(insert_input_object_value = value)


    '''碰撞检测程序'''
    collisions_list = [] # 用于存储碰撞对
    for predator in predator_dict.values():
        
        candidates_list = []
        candidates_list.extend(total_quadtree_node.query_function(predator))
        
        for prey_value in candidates_list:
            if len(checking_collisions(obj_1 = predator, obj_2 = prey_value)) > 0:
                collisions_list.append(checking_collisions(obj_1 = predator, obj_2 = prey_value))
            else:
                pass

    return collisions_list


def checking_collisions(obj_1, obj_2):
    obj_1_x = obj_1.x
    obj_1_y = obj_1.y
    obj_1_radius = obj_1.radius

    obj_2_x = obj_2.x
    obj_2_y = obj_2.y
    obj_2_radius = obj_2.radius

    distance = ((obj_1_x - obj_2_x)**2 + (obj_1_y - obj_2_y)**2)**0.5

    if distance <= (obj_1_radius + obj_2_radius):
        return (obj_1, obj_2)
    else:
        return ()

'''=====body====='''
pygame.init() # 初始化
screen = pygame.display.set_mode((screen_width, screen_height)) # 窗体设置

total_dict = {} # 总对象字典创建
predator_dict = {}
prey_dict = {}

counter_predator = 0
number_predator = 1
counter_prey = 0
number_prey = 1

'''loop'''
while True:

    screen.fill(black) # 刷新界面

    # 退出程序
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: # 叉退出
            exit()
        elif event.type == pygame.KEYDOWN: # 检测按键按下
            if event.key == pygame.K_ESCAPE: # ESC退出
                exit()

    # predator生成
    if counter_predator <= max_predator_counter: # 限定最大生成数
        if counter_predator < max_predator_counter: # 设置初始生成数为10
            total_dict[f'predator_{number_predator}'] = Predator(predator_color = red, predator_radius = predator_circle_radius)

            predator_dict[f'predator_{number_predator}'] = Predator(predator_color = red, predator_radius = predator_circle_radius)

            counter_predator = counter_predator + 1
            number_predator = number_predator + 1

    # prey生成
    if counter_prey <= max_prey_counter: # 限定最大生成数
        if counter_prey < max_prey_counter: # 设置初始生成数为10
            total_dict[f'prey_{number_prey}'] = Prey(prey_color = green, prey_radius = prey_circle_radius)

            prey_dict[f'prey_{number_prey}'] = Prey(prey_color = green, prey_radius = prey_circle_radius)

            counter_prey = counter_prey + 1
            number_prey = number_prey + 1

    # prey与predator刷新
    for value_instance in total_dict.values():
        value_instance.move_function() # 运动函数
        value_instance.draw_function() # 可视化函数

    # 复杂型四叉树检测程序
    collisions_list = []
    collisions_list.extend(find_collisions_main_body_function(input_total_dict = total_dict)) # 返回一个列表
    print(collisions_list)



    time.sleep(0.01)
    pygame.display.update()
