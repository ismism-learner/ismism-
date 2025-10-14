# world_server/entities.py
"""
定义游戏世界中的实体，用于服务器
"""
import uuid
import random

class Entity:
    """所有实体的基类"""
    def __init__(self, name, description=""):
        self.id = str(uuid.uuid4()) # 每个实体都有一个唯一ID
        self.name = name
        self.description = description
        self.position = {"x": random.randint(50, 750), "y": random.randint(50, 550)} # 实体在2D世界中的随机初始位置

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

class Player(Entity):
    """玩家类（在当前的可视化工具中未使用）"""
    def __init__(self, name, description="一个普通人"):
        super().__init__(name, description)

class NPC(Entity):
    """非玩家角色(NPC)类"""
    def __init__(self, name, description="一个路人"):
        super().__init__(name, description)
        self.ism_data = {}
        self.current_action = "Idle" # NPC当前的动作描述
        self.current_goal = "Wander" # NPC当前的目标

        # Tier 1: 生理需求
        self.needs = {
            'hunger': {
                'current': random.randint(0, 40),
                'max': 100,
                'change_per_hour': 4,
                'priority_threshold': 50
            },
            'energy': {
                'current': random.randint(50, 90),
                'max': 100,
                'change_per_hour': -5,
                'priority_threshold': 30
            },
            'idealism': {
                'current': 50,
                'max': 100,
                'change_per_hour': -0.1, # 如果不加强，理想主义会缓慢衰减
                'priority_threshold': 40 # 低于此值则寻求强化信念
            }
        }

        # Tier 2: 社会/意识形态需求
        self.demands = [] # e.g., ["PURSUE_HOBBY", "DEFEAT_RIVAL"]

        # Tier 3: 欲望 (拉康理论)
        self.desire = {
            'imaginary': {}, # 对更完美之物的欲求
            'symbolic': {}, # 对社会认可的欲求
            'real': { # 创伤驱动
                'rupture': 0, # 创伤值
                'source_of_trauma': None # 创伤来源 (NPC ID)
            }
        }

    def think(self, all_entities):
        """NPC的思考/行动逻辑，现在由需求驱动"""

        # 1. 检查并处理互动
        self.check_for_interaction(all_entities)

        # 2. 评估需求并设定目标
        self.evaluate_needs()

        # 3. 根据当前目标执行行动
        self.execute_action()

    def check_for_interaction(self, all_entities):
        """检查与其他NPC的互动"""
        for other in all_entities:
            if other.id == self.id:
                continue

            dist = ((self.position['x'] - other.position['x'])**2 + (self.position['y'] - other.position['y'])**2)**0.5

            if dist < 50: # 互动距离阈值
                # 随机决定是否发起互动
                if random.random() < 0.01: # 降低互动频率
                    # 简化：随机选择一个 "攻击性" 互动
                    self.initiate_insult(other)
                    break # 每次只互动一次

    def initiate_insult(self, target):
        """对目标发起一次侮辱，触发Symbolic和Real Desire"""
        print(f"'{self.name}' insults '{target.name}'!")

        # 对方会如何反应？这取决于他们的'ism'
        # 这里我们直接调用一个方法来处理被侮辱的后果
        target.receive_insult(self)

    def receive_insult(self, aggressor):
        """处理被侮辱的后果"""
        # Symbolic Desire: 我们假设所有NPC目前都讨厌被侮辱
        self.needs['idealism']['current'] = max(0, self.needs['idealism']['current'] - 10) # 侮辱会打击自尊/理想

        # Real Desire: 积累创伤，并记录来源
        self.desire['real']['rupture'] += 25 # 侮辱是创伤性事件
        self.desire['real']['source_of_trauma'] = aggressor.id
        print(f"'{self.name}' feels the sting of the insult. Rupture is now {self.desire['real']['rupture']}.")

        # 立即反应：进入一个短暂的 "Fleeing" 状态
        self.current_goal = "FLEE_FROM_THREAT"
        self.current_action = "Fleeing"


    def evaluate_needs(self):
        """评估自身需求，设定最优先的目标"""
        # Tier 3 (Real) 需求优先于一切
        if self.desire['real']['rupture'] > 50 and self.desire['real']['source_of_trauma']: # 创伤阈值
            self.current_goal = "REPLACE_SOURCE_OF_TRAUMA"
            return

        # Tier 1 需求优先
        if self.current_goal == "FLEE_FROM_THREAT": # 如果正在逃跑，暂时不考虑其他需求
            return
        if self.needs['energy']['current'] < self.needs['energy']['priority_threshold']:
            self.current_goal = "REST"
            return
        if self.needs['hunger']['current'] > self.needs['hunger']['priority_threshold']:
            self.current_goal = "SATISFY_HUNGER"
            return

        # Tier 2 需求
        if self.needs['idealism']['current'] < self.needs['idealism']['priority_threshold']:
            self.current_goal = "PONDER_PHILOSOPHICAL_QUESTIONS"
            return

        # 如果没有紧急需求，并且当前没有长期目标，则从demands中选一个
        if self.current_goal in ["Wander", "REST", "SATISFY_HUNGER", "FLEE_FROM_THREAT"]:
            if self.demands:
                self.current_goal = random.choice(self.demands)
            else:
                self.current_goal = "Wander"

    def execute_action(self):
        """根据当前目标(goal)决定具体行动(action)和移动"""
        move_x, move_y = 0, 0
        speed = 2

        # --- Tier 1 Actions ---
        if self.current_goal == "SATISFY_HUNGER":
            self.current_action = "Seeking Food"
            move_x, move_y = random.choice([-speed, speed]), random.choice([-speed, speed])
            self.needs['hunger']['current'] -= 0.1
            if self.needs['hunger']['current'] <= 0:
                self.current_goal = "Wander"

        elif self.current_goal == "REST":
            self.current_action = "Resting"
            self.needs['energy']['current'] += 0.2
            if self.needs['energy']['current'] >= self.needs['energy']['max']:
                self.current_goal = "Wander"

        # --- Tier 2 Actions ---
        elif self.current_goal == "PONDER_PHILOSOPHICAL_QUESTIONS":
            self.current_action = "Pondering"
            self.needs['idealism']['current'] += 0.5
            if self.needs['idealism']['current'] >= self.needs['idealism']['max']:
                self._evolve_demand(self.current_goal)

        elif self.current_goal == "PURSUE_ROUTINE_HOBBY":
            self.current_action = "Engaged in Hobby"
            move_x, move_y = random.choice([-speed, speed, 0]), random.choice([-speed, speed, 0])
            if random.random() < 0.01:
                self.needs['idealism']['current'] = min(self.needs['idealism']['max'], self.needs['idealism']['current'] + 10)
                self._evolve_demand(self.current_goal)

        elif self.current_goal == "SEEK_LUXURY_GOODS":
            self.current_action = "Seeking Goods"
            move_x, move_y = random.choice([-speed, speed]), random.choice([-speed, speed])
            if random.random() < 0.01:
                self.needs['idealism']['current'] = min(self.needs['idealism']['max'], self.needs['idealism']['current'] + 15)
                self._evolve_demand(self.current_goal)

        # --- Evolved Tier 2 Actions ---
        elif self.current_goal == "SEEK_RARE_ARTIFACT":
            self.current_action = "Seeking Artifact"
            move_x, move_y = random.choice([-speed*2, speed*2]), random.choice([-speed*2, speed*2]) # More frantic search

        elif self.current_goal == "MASTER_CRAFT":
            self.current_action = "Honing Craft" # Stationary, focused work

        elif self.current_goal == "WRITE_MANIFESTO":
            self.current_action = "Writing Manifesto" # Stationary, focused work

        # --- Tier 3 Actions ---
        elif self.current_goal == "REPLACE_SOURCE_OF_TRAUMA":
            self.current_action = "Plotting Revenge"
            # In a real scenario, this would involve complex logic to find and act against the source.
            # For now, the NPC just paces angrily.
            move_x, move_y = random.choice([-speed, speed, -speed, speed, 0]), 0

        elif self.current_goal == "FLEE_FROM_THREAT":
            self.current_action = "Fleeing"
            # For now, just move randomly and fast. A real implementation would move away from the threat.
            move_x, move_y = random.choice([-speed*2, speed*2]), random.choice([-speed*2, speed*2])
            if random.random() < 0.1: # 10% chance to calm down each tick
                self.current_goal = "Wander"

        # --- Default Action ---
        elif self.current_goal == "Wander":
            self.current_action = "Wandering"
            move_x, move_y = random.choice([-speed, speed, 0]), random.choice([-speed, speed, 0])

        else:
            self.current_action = "Idle"

        # 更新位置 (加上一些边界限制)
        self.position["x"] = max(0, min(800, self.position["x"] + move_x))
        self.position["y"] = max(0, min(600, self.position["y"] + move_y))

    def _evolve_demand(self, completed_demand):
        """(Imaginary Desire) 在一个需求满足后，生成一个更高级的欲望"""
        # 从当前需求列表中移除已完成的需求
        if completed_demand in self.demands:
            self.demands.remove(completed_demand)

        # 定义简单的进化路径
        evolution_path = {
            "SEEK_LUXURY_GOODS": "SEEK_RARE_ARTIFACT", # 想要更好的东西
            "PURSUE_ROUTINE_HOBBY": "MASTER_CRAFT", # 想把爱好做到极致
            "PONDER_PHILOSOPHICAL_QUESTIONS": "WRITE_MANIFESTO" # 想把思想写下来
        }

        # 如果存在进化路径，则添加新的、更高级的需求
        if completed_demand in evolution_path:
            new_demand = evolution_path[completed_demand]
            if new_demand not in self.demands:
                self.demands.append(new_demand)
                print(f"NPC {self.name} a new desire: {new_demand}")

        # 无论如何，完成后先回归漫游状态
        self.current_goal = "Wander"