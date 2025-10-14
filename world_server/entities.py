# world_server/entities.py
"""
定义游戏世界中的实体，用于服务器
"""
import uuid
import random
from resource_manager import ResourceManager

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
        self.money = random.randint(20, 100) # NPC的个人资金

        # 关系（动态）
        self.relationships = {} # Key: other_npc_id, Value: {"affinity": 0}

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
            'stress': {
                'current': random.randint(0, 30),
                'max': 100,
                'change_per_hour': 1, # 压力会随着时间慢慢积累
                'priority_threshold': 50 # 压力过大时寻求娱乐
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

    def think(self, all_entities, interactions, locations):
        """NPC的思考/行动逻辑，现在由需求和互动驱动"""
        # 1. 检查并处理互动
        self.evaluate_and_initiate_interaction(all_entities, interactions)

        # 2. 评估需求并设定目标
        self.evaluate_needs(locations)

        # 3. 根据当前目标执行行动
        self.execute_action(locations)

    def get_affinity(self, other_npc_id):
        """安全地获取与另一个NPC的亲和度"""
        return self.relationships.get(other_npc_id, {"affinity": 0})["affinity"]

    def _get_all_ism_keywords(self):
        """获取NPC所有'ism'的关键词列表"""
        keywords = set()
        # 添加主要'ism'的关键词
        for key in ['field_theory', 'ontology', 'epistemology', 'teleology']:
            keywords.update(self.ism_data.get(key, {}).get('keywords', []))
        # 添加次要'ism'的关键词
        for secondary_ism in self.ism_data.get('secondary_isms', []):
            for key in ['field_theory', 'ontology', 'epistemology', 'teleology']:
                keywords.update(secondary_ism.get(key, {}).get('keywords', []))
        return list(keywords)

    def _check_interaction_conditions(self, interaction, target):
        """检查发起者和目标是否满足特定互动的条件"""
        initiator_keywords = self._get_all_ism_keywords()
        target_keywords = target._get_all_ism_keywords()
        conditions = interaction.get('conditions', {})

        # 检查发起者的条件
        if 'initiator_has_any_keyword' in conditions:
            if not any(k in initiator_keywords for k in conditions['initiator_has_any_keyword']):
                return False

        # 检查目标的条件
        if 'target_has_any_keyword' in conditions:
            if not any(k in target_keywords for k in conditions['target_has_any_keyword']):
                return False

        if 'target_must_not_have_keyword' in conditions:
            if any(k in target_keywords for k in conditions['target_must_not_have_keyword']):
                return False

        return True

    def evaluate_and_initiate_interaction(self, all_entities, interactions):
        """评估并决定是否以及如何与其他NPC互动"""
        if random.random() > 0.02: # 降低互动评估的频率以提高性能
            return

        for other in all_entities:
            if other.id == self.id:
                continue

            dist = ((self.position['x'] - other.position['x'])**2 + (self.position['y'] - other.position['y'])**2)**0.5
            if dist < 80: # 增加互动距离

                possible_interactions = []
                for interaction in interactions:
                    if self._check_interaction_conditions(interaction, other):
                        possible_interactions.append(interaction)

                if not possible_interactions:
                    continue

                # --- 决策逻辑 ---
                # 简单的决策：优先考虑亲和度。如果关系好，倾向于友好互动；如果关系差，倾向于攻击性互动。
                affinity = self.get_affinity(other.id)

                chosen_interaction = None
                if affinity < -20: # 关系很差
                    hostile_options = [i for i in possible_interactions if i.get('type') == 'aggressive']
                    if hostile_options:
                        chosen_interaction = random.choice(hostile_options)
                elif affinity > 20: # 关系很好
                    friendly_options = [i for i in possible_interactions if i.get('type') == 'friendly']
                    if friendly_options:
                        chosen_interaction = random.choice(friendly_options)
                else: # 关系一般或初识
                    # 随机选择一个可能的互动
                    if possible_interactions:
                        chosen_interaction = random.choice(possible_interactions)

                if chosen_interaction:
                    self.initiate_interaction(chosen_interaction, other)
                    break # 每次只与一个NPC互动

    def initiate_interaction(self, interaction, target):
        """对目标发起一个互动"""
        print(f"'{self.name}' initiates '{interaction['name']}' with '{target.name}'.")

        # 应用对发起者的效果
        effects = interaction.get('effects', {})
        self.needs['idealism']['current'] = max(0, self.needs['idealism']['current'] + effects.get('initiator_idealism_change', 0))

        # 让目标接收互动
        target.receive_interaction(interaction, self)

    def receive_interaction(self, interaction, aggressor):
        """处理接收到的互动"""
        effects = interaction.get('effects', {})

        # 更新关系
        affinity_change = effects.get('base_affinity_change', 0)
        current_affinity = self.get_affinity(aggressor.id)
        new_affinity = current_affinity + affinity_change
        self.relationships[aggressor.id] = {"affinity": new_affinity}

        # 更新需求
        self.needs['idealism']['current'] = max(0, self.needs['idealism']['current'] + effects.get('target_idealism_change', 0))

        # 更新创伤
        self.desire['real']['rupture'] = max(0, self.desire['real']['rupture'] + effects.get('target_rupture_change', 0))
        if effects.get('target_rupture_change', 0) > 0:
            self.desire['real']['source_of_trauma'] = aggressor.id

        # --- 新增：思想传播逻辑 ---
        propagate_chance = effects.get('propagate_ism_chance', 0)
        if random.random() < propagate_chance:
            # 从发起者的次要'ism'中选择一个来传播
            aggressor_secondary_isms = aggressor.ism_data.get('secondary_isms', [])
            if aggressor_secondary_isms:
                ism_to_propagate = random.choice(aggressor_secondary_isms)
                # 确保接收者还没有这个'ism'
                receiver_secondary_isms = self.ism_data.get('secondary_isms', [])
                receiver_ism_names = [ism.get('name') for ism in receiver_secondary_isms]

                if ism_to_propagate.get('name') not in receiver_ism_names:
                    receiver_secondary_isms.append(ism_to_propagate)
                    self.ism_data['secondary_isms'] = receiver_secondary_isms
                    print(f"** Ideological Spread: '{aggressor.name}' spreads '{ism_to_propagate.get('name')}' to '{self.name}'! **")


        print(f"'{self.name}' reacts to '{interaction['name']}'. Affinity towards '{aggressor.name}' is now {new_affinity}.")

        # --- 更复杂的反应逻辑 ---
        receiver_keywords = self._get_all_ism_keywords()
        interaction_type = interaction.get('type')

        if interaction_type == 'aggressive':
            # 如果接收者有对抗性，并且关系不好，他们不会逃跑，而是会愤怒
            if '对抗' in receiver_keywords and new_affinity < 10:
                self.current_action = "Fuming"
                # 在未来的迭代中，这里可以触发一个报复性互动
            else:
                self.current_goal = "FLEE_FROM_THREAT"
                self.current_action = "Fleeing"

        elif interaction_type == 'friendly':
            # 如果接收者是多疑的或虚无的，他们对友好行为的反应会更差
            if any(k in receiver_keywords for k in ['孤立', '虚无主义']):
                self.relationships[aggressor.id]["affinity"] = new_affinity - 10 # 减少亲和度增益
                self.current_action = "Suspicious"
            else:
                # 正常反应，什么也不做，继续之前的行为
                pass


    def evaluate_needs(self, locations):
        """评估自身需求，设定最优先的目标"""
        # 0. 如果当前目标是前往某地，则暂时不重新评估，除非需求更紧急
        if isinstance(self.current_goal, dict) and self.current_goal.get("type") == "GO_TO_LOCATION":
            # (在未来，这里可以添加逻辑，例如，如果突然受到攻击，可以中断寻路)
            return

        # 1. Tier 3 (Real) 需求优先于一切
        if self.desire['real']['rupture'] > 50 and self.desire['real']['source_of_trauma']:
            self.current_goal = "REPLACE_SOURCE_OF_TRAUMA"
            return

        # 2. Tier 1 (Physiological) 需求优先
        if self.current_goal == "FLEE_FROM_THREAT":
            return

        # 检查饥饿
        if self.needs['hunger']['current'] > self.needs['hunger']['priority_threshold']:
            # 使用ResourceManager查找有食物的地点
            best_food_location = ResourceManager.get_richest_location("GRAIN", locations)
            if best_food_location:
                self.current_goal = {"type": "GO_TO_LOCATION", "target_location": best_food_location, "purpose": "SATISFY_HUNGER"}
                return

        # 检查精力
        if self.needs['energy']['current'] < self.needs['energy']['priority_threshold']:
            shelter_locations = [loc for loc in locations if loc.get('type') == 'SHELTER']
            if shelter_locations:
                closest_loc = min(shelter_locations, key=lambda loc: ((self.position['x'] - loc['position']['x'])**2 + (self.position['y'] - loc['position']['y'])**2)**0.5)
                self.current_goal = {"type": "GO_TO_LOCATION", "target_location": closest_loc, "purpose": "REST"}
                return

        # 检查压力
        if self.needs['stress']['current'] > self.needs['stress']['priority_threshold']:
            entertainment_locations = [loc for loc in locations if loc.get('type') == 'ENTERTAINMENT']
            # 筛选出NPC能负担得起的娱乐场所
            affordable_locations = [loc for loc in entertainment_locations if self.money >= loc.get('cost', 0)]
            if affordable_locations:
                # 简单起见，随机选择一个
                target_loc = random.choice(affordable_locations)
                self.current_goal = {"type": "GO_TO_LOCATION", "target_location": target_loc, "purpose": "SEEK_ENTERTAINMENT"}
                return

        # 3. Tier 2 (Societal/Ideological) 需求
        # 检查工作需求 (作为一种特殊的demand)
        if "WORK" in self.demands:
             work_locations = [loc for loc in locations if loc.get('type') == 'WORKPLACE']
             if work_locations:
                # 为了简单起见，我们让他们随机选一个工作地点，而不是最近的
                target_loc = random.choice(work_locations)
                self.current_goal = {"type": "GO_TO_LOCATION", "target_location": target_loc, "purpose": "WORK"}
                return

        if self.needs['idealism']['current'] < self.needs['idealism']['priority_threshold']:
            self.current_goal = "PONDER_PHILOSOPHICAL_QUESTIONS"
            return

        # 4. 如果没有紧急需求，并且当前目标是可中断的，则从demands中选一个或游荡
        if isinstance(self.current_goal, str) and self.current_goal in ["Wander", "Idle"]:
             # 过滤掉WORK，因为它已经被特殊处理了
             other_demands = [d for d in self.demands if d != "WORK"]
             if other_demands:
                self.current_goal = random.choice(other_demands)
             else:
                self.current_goal = "Wander"

    def execute_action(self, locations):
        """根据当前目标(goal)决定具体行动(action)和移动"""
        move_x, move_y = 0, 0
        speed = 2

        # --- 新增：基于地点的行动逻辑 ---
        if isinstance(self.current_goal, dict) and self.current_goal.get("type") == "GO_TO_LOCATION":
            target_loc = self.current_goal["target_location"]
            purpose = self.current_goal["purpose"]
            target_pos = target_loc["position"]
            dist_to_target = ((self.position['x'] - target_pos['x'])**2 + (self.position['y'] - target_pos['y'])**2)**0.5

            # 如果已经到达地点
            if dist_to_target < target_loc["radius"]:
                if purpose == "SATISFY_HUNGER":
                    self.current_action = "Eating"
                    # 尝试消耗资源，如果成功则恢复饥饿
                    if ResourceManager.consume(target_loc, "GRAIN", 5, locations):
                        self.needs['hunger']['current'] = max(0, self.needs['hunger']['current'] - 25) # 吃一顿饱的
                        if self.needs['hunger']['current'] <= 0:
                            self.current_goal = "Wander" # 需求满足，重置目标
                    else:
                        # 如果没有食物了，NPC会感到困惑并重新评估
                        self.current_action = "Confused (No Food)"
                        self.current_goal = "Wander"

                elif purpose == "REST":
                    self.current_action = "Sleeping"
                    self.needs['energy']['current'] = min(self.needs['energy']['max'], self.needs['energy']['current'] + 2.5) # 在地点休息恢复速度更快
                    if self.needs['energy']['current'] >= self.needs['energy']['max']:
                        self.current_goal = "Wander" # 需求满足，重置目标

                elif purpose == "WORK":
                    work_type = target_loc.get("work_type", "Working")
                    self.current_action = f"{work_type}"

                    # 工作会生产资源
                    ResourceManager.produce(target_loc, locations)

                    # 工作会消耗精力和增加压力，但会赚钱
                    self.needs['energy']['current'] = max(0, self.needs['energy']['current'] - 0.2)
                    self.needs['stress']['current'] = min(self.needs['stress']['max'], self.needs['stress']['current'] + 0.3)
                    self.money += 1 # 每次工作行动赚取1单位金钱

                    # 工作一段时间后就离开
                    if random.random() < 0.03:
                        self.current_goal = "Wander"

                elif purpose == "SEEK_ENTERTAINMENT":
                    self.current_action = f"Enjoying at {target_loc['name']}"
                    cost = target_loc.get('cost', 0)

                    # 扣除金钱并降低压力
                    self.money -= cost
                    self.needs['stress']['current'] = max(0, self.needs['stress']['current'] - 50) # 娱乐大大降低压力

                    # 应用意识形态影响
                    influence = target_loc.get('ideological_influence', {})
                    if 'idealism' in influence:
                        self.needs['idealism']['current'] = min(self.needs['idealism']['max'], max(0, self.needs['idealism']['current'] + influence['idealism']))
                    if 'rupture' in influence:
                        self.desire['real']['rupture'] = min(100, max(0, self.desire['real']['rupture'] + influence['rupture']))

                    # 娱乐后离开
                    self.current_goal = "Wander"

            # 如果还没到，就往那边走
            else:
                self.current_action = f"Going to {target_loc['name']}"
                # 计算移动方向
                dx = target_pos['x'] - self.position['x']
                dy = target_pos['y'] - self.position['y']
                if dist_to_target > 0:
                    move_x = (dx / dist_to_target) * speed
                    move_y = (dy / dist_to_target) * speed

        # --- 旧的抽象行动逻辑 (保留用于其他类型的目标) ---
        elif self.current_goal == "SATISFY_HUNGER": # 作为找不到地点时的后备方案
            self.current_action = "Foraging for food" # 改为更明确的动作
            move_x, move_y = random.choice([-speed, speed]), random.choice([-speed, speed])
            self.needs['hunger']['current'] -= 0.05 # 野外觅食效率低
            if self.needs['hunger']['current'] <= 0:
                self.current_goal = "Wander"

        elif self.current_goal == "REST": # 作为找不到地点时的后备方案
            self.current_action = "Resting wherever possible"
            self.needs['energy']['current'] += 0.1 # 随地休息效率低
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

        # --- Reactionary Actions ---
        elif self.current_action == "Fuming":
            # 愤怒地原地踏步
            move_x, move_y = random.choice([-1, 1, 0]), random.choice([-1, 1, 0])
            if random.random() < 0.1: # 有几率冷静下来
                self.current_action = "Idle"

        elif self.current_action == "Suspicious":
            # 保持静止，表示怀疑
            if random.random() < 0.2: # 有几率恢复正常
                self.current_action = "Idle"

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