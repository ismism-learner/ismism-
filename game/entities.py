# game/entities.py
"""
定义游戏中的实体
"""

class Entity:
    """所有实体的基类"""
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Player(Entity):
    """玩家类"""
    def __init__(self, name, description="一个普通人"):
        super().__init__(name, description)


class NPC(Entity):
    """非玩家角色(NPC)类"""
    def __init__(self, name, description="一个路人"):
        super().__init__(name, description)
        # 在未来的步骤中，我们会在这里加载NPC的哲学“主义”数据
        self.ism_data = {}

    def think(self):
        """NPC的思考/行动逻辑，由其内部数据驱动"""
        # 我们以"leisure_activity"脚本作为本次行为的驱动力
        scripts = self.ism_data.get("behavioral_scripts", {})
        leisure_script = scripts.get("leisure_activity", "IDLE")

        action_text = ""
        if leisure_script == "PURSUE_ROUTINE_HOBBY":
            action_text = "正在进行他的日常爱好。"
        elif leisure_script == "SEEK_LUXURY_GOODS":
            action_text = "看起来在寻找奢侈品来享受。"
        elif leisure_script == "ENGAGE_IN_ARTISTIC_CREATION":
            action_text = "沉浸在某种艺术创作中。"
        elif leisure_script == "PONDER_PHILOSOPHICAL_QUESTIONS":
            action_text = "陷入了深刻的哲学思辨。"
        else:
            # 为任何其他脚本提供一个默认的、可见的文本
            action_text = f"似乎在无所事事地闲逛... ({leisure_script})"

        print(f"[{self.name}] {action_text}")