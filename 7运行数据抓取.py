import pygame # 可视化依赖库
import sys  # 系统程序依赖库
import time  # 时间戳依赖库
import random  # 随机数依赖库
import matplotlib.pyplot  # 数据分析依赖库

'''=====调试参数设定====='''
creat_prey_time = 0.0001  # prey输出间隔时间/秒

max_predator_counter = 1000  # 最大predator数量/个
max_prey_counter = 1000  # 最大prey数量/个

initial_predator_counter = 50  # 初始predator数量/个
initial_prey_counter = 100  # 初始prey数量/个

predator_circle_radius = 1  # predator半径
prey_circle_radius = 10  # prey半径

predator_max_fasting_time = 5  # 捕食者最长空腹时间
predator_max_life = 50  # 捕食者寿命/秒

prey_split_time = 1  # prey分裂时间/s

capacity_counter = 4  # 节点容量
screen_width, screen_height = 800, 600  # 窗体大小
speed = 1  # 运动速度值

collect_time = 0.1  # 时间断面采样率

'''=====color====='''
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 225

'''=====class====='''
class Predator:  # 捕食者类
    def __init__(self, predator_color, predator_radius, id):
        self.radius = predator_radius  # 大小

        self.x = random.randint(self.radius, screen_width - self.radius)
        self.y = random.randint(self.radius, screen_height - self.radius)
        self.location = [self.x, self.y]  # 对象位置

        speed_list = [-speed, speed]  # 对象速度
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list) 

        self.color = predator_color  # 绘制颜色
        self.id = id  # 添加唯一标识符

        self.creat_time = time.time() # 创建时间
        self.last_hunt_time = time.time()  # 最后捕食时间

    '''运动原理'''
    def move_function(self):
        if self.x + self.radius >= screen_width or self.x - self.radius <= 0:
            self.speed_x *= -1
        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.speed_y *= -1
        self.x += self.speed_x
        self.y += self.speed_y
        self.location = [self.x, self.y]

    '''可视化'''
    def draw_function(self):
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0)

class Prey:  # 被捕食者类
    def __init__(self, prey_color, prey_radius, id, x = None, y = None):
        self.radius = prey_radius  # 大小

        if x == None or y == None:
            self.x = random.randint(self.radius, screen_width - self.radius)
            self.y = random.randint(self.radius, screen_height - self.radius)
        else:
            self.x = x
            self.y = y
        self.location = [self.x, self.y]  # 对象位置

        speed_list = [-speed, speed]  # 对象速度
        self.speed_x = random.choice(speed_list)
        self.speed_y = random.choice(speed_list)

        self.color = prey_color  # 绘制颜色
        self.last_split_time = time.time()  #最后分裂时间

        self.id = id  # 添加唯一标识符

    '''运动原理'''
    def move_function(self):
        if self.x + self.radius >= screen_width or self.x - self.radius <= 0:
            self.speed_x *= -1
        if self.y + self.radius >= screen_height or self.y - self.radius <= 0:
            self.speed_y *= -1
        self.x += self.speed_x
        self.y += self.speed_y
        self.location = [self.x, self.y]

    '''可视化'''
    def draw_function(self):
        pygame.draw.circle(screen, self.color, self.location, self.radius, 0)

class QuadtreeNode:  # 四叉树类
    def __init__(self, node_x, node_y, node_width, node_height, node_capacity=capacity_counter):
        self.node_x = node_x  # 节点坐标
        self.node_y = node_y  # 节点坐标
        self.node_width = node_width  # 节点宽
        self.node_height = node_height  # 节点高
        self.node_capacity = node_capacity  # 节点容量
        self.object_list = []  # 节点内元素列表
        self.subnode_list = []  # 节点内子节点列表

    '''可视化'''
    def visualization_function(self, input_color):
        pygame.draw.rect(screen, input_color, (self.node_x, self.node_y, self.node_width, self.node_height), 1)

    '''节点插入'''
    def insert_object_function(self, insert_input_object_value):
        if len(self.subnode_list) == 4:  # 当父节点有子节点时
            for subnode_value in self.subnode_list:  # 遍历子节点，找到适合的子节点
                if self.whether_node_contains_object_function(insert_input_object_value, subnode_value):  # 找到适合的子节点
                    subnode_value.insert_object_function(insert_input_object_value)
                    return
            self.object_list.append(insert_input_object_value)
        else:
            self.object_list.append(insert_input_object_value)
            if len(self.object_list) > self.node_capacity:  # 判断父节点是否需要分裂
                self.split_node_function()  # 分裂父节点
                for object_value in self.object_list.copy():  # 对父节点已有对象再插入
                    moved = False
                    for subnode_value in self.subnode_list:  # 遍历子节点，找到适合的子节点
                        if self.whether_node_contains_object_function(object_value, subnode_value):  # 找到适合的子节点
                            subnode_value.insert_object_function(object_value)
                            moved = True
                            break  # 节约算力
                    if moved:
                        self.object_list.remove(object_value)  # 父节点对象列表仅保留压线对象

    '''是否完全在节点内'''
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

    '''节点分裂'''
    def split_node_function(self):
        subnode_w = self.node_width / 2
        subnode_h = self.node_height / 2
        self.subnode_list = [
            QuadtreeNode(self.node_x, self.node_y, subnode_w, subnode_h),
            QuadtreeNode(self.node_x + subnode_w, self.node_y, subnode_w, subnode_h),
            QuadtreeNode(self.node_x, self.node_y + subnode_h, subnode_w, subnode_h),
            QuadtreeNode(self.node_x + subnode_w, self.node_y + subnode_h, subnode_w, subnode_h)
        ]  # 直接重新定义来代替append

        # 绘制子节点
        for subnode_instance_value in self.subnode_list:
            subnode_instance_value.visualization_function(input_color = white)

    '''候选检测对象'''
    def query_function(self, input_object):
        candidates = []  # 候选名单
        if len(self.subnode_list) == 4:  # 父节点判断是否有子节点
            for subnode in self.subnode_list:  # 遍历子节点，寻找是否有合适的子节点
                if not self.check_object_overlap(input_object, subnode):  # 即对象在子节点内或压线时，将其进行进一步查询
                    candidates.extend(subnode.query_function(input_object))  # 若压线时，遍历会有两个/四个子节点都满足if，并将这些子节点的对象都添加到候选名单中
        for obj in self.object_list:  # 将这些子节点的对象都添加到候选名单中
            if isinstance(obj, Prey) == True:  # 如果obj在Prey类里面
                candidates.append(obj)
        return candidates

    '''是否完全在节点外'''
    def check_object_overlap(self, obj, node):
        obj_left = obj.x - obj.radius
        obj_right = obj.x + obj.radius
        obj_top = obj.y - obj.radius
        obj_bottom = obj.y + obj.radius

        node_left = node.node_x
        node_right = node.node_x + node.node_width
        node_top = node.node_y
        node_bottom = node.node_y + node.node_height

        return (obj_right < node_left or 
                    obj_left > node_right or 
                    obj_bottom < node_top or 
                    obj_top > node_bottom)

'''=====self_function====='''
def find_collisions_main_body_function(input_total_dict):  # 碰撞组查询函数
    '''建树及分配程序'''
    # 计算四叉树根节点边界坐标
    min_x = min(obj.x - obj.radius for obj in input_total_dict.values())
    max_x = max(obj.x + obj.radius for obj in input_total_dict.values())
    min_y = min(obj.y - obj.radius for obj in input_total_dict.values())
    max_y = max(obj.y + obj.radius for obj in input_total_dict.values())

    # 生成四叉树根节点
    root_quadtree_node = QuadtreeNode(min_x, min_y, max_x - min_x, max_y - min_y)
    root_quadtree_node.visualization_function(input_color = white)

    # 将object传入四叉树总结点中并切割分配
    for value in input_total_dict.values():
        root_quadtree_node.insert_object_function(value)

    '''碰撞检测程序'''
    collisions_list = [] # 用于存储碰撞对元组
    for predator in predator_dict.values():
        candidates_list = root_quadtree_node.query_function(predator)

        for prey in candidates_list: # 对候选对象执行精细碰撞检测
            if checking_collisions(predator, prey):
                collisions_list.append((predator, prey))  # 存储元组

                '''其它程序'''
                predator.last_hunt_time = time.time()  #更新最后捕食时间

    return collisions_list

def checking_collisions(obj_1, obj_2):  # 欧几里得式精细碰撞检测函数
    dx = obj_1.x - obj_2.x
    dy = obj_1.y - obj_2.y
    distance = (dx**2 + dy**2)**0.5
    return distance <= (obj_1.radius + obj_2.radius)

def predator_copy_function():  # 模拟predator分裂
    global counter_predator, number_predator
    if counter_predator <= max_predator_counter:
        key = f'predator_{number_predator}'
        predator = Predator(red, predator_circle_radius, number_predator)

        total_dict[key] = predator
        predator_dict[key] = predator

        counter_predator += 1
        number_predator += 1

def prey_copy_function(input_x, input_y):  # 模拟prey分裂
    global counter_prey, number_prey
    if counter_prey <= max_prey_counter:
        key = f'prey_{number_prey}'
        prey = Prey(green, prey_circle_radius, number_prey, x = input_x, y = input_y)

        total_dict[key] = prey
        prey_dict[key] = prey

        counter_prey += 1
        number_prey += 1

def data_analyze_function(x, y_1, y_2):  # 数据分析函数
    global red, green

    matplotlib.pyplot.plot(x, y_1, color = 'red')
    matplotlib.pyplot.plot(x, y_2, color = 'green')

    matplotlib.pyplot.title("Simple Line Plot")
    matplotlib.pyplot.xlabel("X-axis")
    matplotlib.pyplot.ylabel("Y-axis")

    matplotlib.pyplot.show()

'''=====main====='''

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

total_dict = {}
predator_dict = {}
prey_dict = {}

counter_predator = 0  # 当前predator数目
counter_prey = 0  # 当前prey数目
number_predator = 1  # predator编号/id
number_prey = 1  # prey编号/id

collect_data_time_list = []  # 运行数据时间收集列表
collect_data_predator_counter_list = []  # 运行数据predator收集列表
collect_data_prey_counter_list = []  # 运行数据prey收集列表

start_time = time.time()  # 记录运行起始时间戳
data_collect_last_time = start_time  # 最后一次抓取时间

'''=====loop====='''
while True:
    screen.fill(black)
    
    # 退出程序
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            data_analyze_function(collect_data_time_list, collect_data_predator_counter_list, collect_data_prey_counter_list)

    '''=====creat====='''
    # 生成初始Predator
    if number_predator <= initial_predator_counter:
        key = f'predator_{number_predator}'
        predator = Predator(red, predator_circle_radius, number_predator)

        total_dict[key] = predator
        predator_dict[key] = predator

        counter_predator += 1
        number_predator += 1

    # 生成初始Prey
    if number_prey <= initial_prey_counter:
        key = f'prey_{number_prey}'
        prey = Prey(green, prey_circle_radius, number_prey)

        total_dict[key] = prey
        prey_dict[key] = prey

        counter_prey += 1
        number_prey += 1

    '''=====refresh====='''
    # 更新对象位置
    for obj in total_dict.values():
        obj.move_function()
        obj.draw_function()

    # 检测碰撞
    if len(total_dict) != 0:  # 防止全部元素消失导致报错
        collisions_list = find_collisions_main_body_function(total_dict)
    
    '''=====delete====='''
    # 删除被捕食的Prey(此处使用该算法是因为一帧类会发生多次碰撞)
    remove_values = {pair[1] for pair in collisions_list}  # 使用集合去重并直接提取值
    keys_to_delete = [k for k, v in prey_dict.items() if v in remove_values]  # 单次遍历收集所有待删键
    for key in keys_to_delete:  # 统一删除键
        del total_dict[key]
        del prey_dict[key]

        counter_prey -= 1
        predator_copy_function()

    # 删除停留时间过长的Predator（模拟被饿死）
    keys_to_delete = []
    current_time = time.time()
    for key, value in predator_dict.items():
        if current_time - value.last_hunt_time >= predator_max_fasting_time:
            keys_to_delete.append(key)
    for key in keys_to_delete:  # 统一删除键
        del total_dict[key]
        del predator_dict[key]

        counter_predator -= 1

    # 删除停留时间过长的Predator（模拟寿命）
    keys_to_delete = []
    current_time = time.time()
    for key, value in predator_dict.items():
        if current_time - value.creat_time >= predator_max_life:
            keys_to_delete.append(key)
    for key in keys_to_delete:  # 统一删除键
        del total_dict[key]
        del predator_dict[key]

        counter_predator -= 1
        
    '''=====recreat====='''
    # prey时间分裂
    current_time = time.time()
    for prey_value in prey_dict.copy().values():
        if current_time - prey_value.last_split_time >= prey_split_time:
            prey_copy_function(input_x = prey_value.x, input_y = prey_value.y)
            prey_value.last_split_time = current_time

    '''=====print====='''
    # 打印碰撞结果
    if collisions_list:
        print("\n=== 碰撞检测结果 ===")
        for idx, (predator, prey) in enumerate(collisions_list, 1):
            print(f"碰撞对 {idx}: Predator(ID:{predator.id}) 和 Prey(ID:{prey.id})")
            print(f"Predator位置: ({predator.x:.1f}, {predator.y:.1f})")
            print(f"Prey位置:    ({prey.x:.1f}, {prey.y:.1f})")
            print("-" * 40)

    '''data analyze'''
    # 运行数据收集
    current_time = time.time()
    if current_time - data_collect_last_time >= collect_time:
        run_time = current_time - start_time

        collect_data_time_list.append(run_time)
        collect_data_predator_counter_list.append(counter_predator)
        collect_data_prey_counter_list.append(counter_prey)

        data_collect_last_time = current_time

    time.sleep(0.001)
    pygame.display.update()