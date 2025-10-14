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

    def think(self):
        """NPC的思考/行动逻辑，现在它会更新自己的状态而不是打印"""
        scripts = self.ism_data.get("behavioral_scripts", {})
        leisure_script = scripts.get("leisure_activity", "IDLE")

        # 根据行为脚本决定一个简单的移动逻辑
        move_x, move_y = 0, 0
        speed = 2 # 移动速度

        if leisure_script == "PURSUE_ROUTINE_HOBBY":
            self.current_action = "Wandering"
            move_x = random.choice([-speed, speed, 0])
            move_y = random.choice([-speed, speed, 0])
        elif leisure_script == "SEEK_LUXURY_GOODS":
            self.current_action = "Seeking Goods"
            # 倾向于朝一个方向移动
            move_x = random.choice([-speed, speed])
            move_y = random.choice([-speed, speed])
        elif leisure_script == "PONDER_PHILOSOPHICAL_QUESTIONS":
            self.current_action = "Pondering"
            # 哲学家倾向于静止不动
            move_x, move_y = 0, 0
        else: # IDLE 或其他
            self.current_action = "Idle"
            move_x, move_y = 0, 0

        # 更新位置 (加上一些边界限制)
        self.position["x"] = max(0, min(800, self.position["x"] + move_x))
        self.position["y"] = max(0, min(600, self.position["y"] + move_y))