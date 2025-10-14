# game/world.py
"""
定义游戏世界
"""

class World:
    def __init__(self):
        print("游戏世界已创建。")
        self.scenes = {} # 存储所有场景
        self.current_scene = None # 当前玩家所在的场景
        self.time = 0 # 世界时间，以tick为单位
        self.ticks_per_hour = 120 # 假设每120个tick（60秒）等于游戏内一小时

    def add_scene(self, scene):
        """添加一个新场景"""
        self.scenes[scene.name] = scene

    def set_current_scene(self, scene_name):
        """设置当前场景"""
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            print(f"场景已切换到: {scene_name}")
        else:
            print(f"错误: 找不到名为 '{scene_name}' 的场景。")


class Scene:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.entities = [] # 存放该场景中的所有实体 (NPC, 物品等)

    def add_entity(self, entity):
        """向场景中添加一个实体"""
        self.entities.append(entity)

    def describe(self):
        """返回场景的描述"""
        return self.description