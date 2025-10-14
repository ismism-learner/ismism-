# game/engine.py
"""
游戏核心引擎
"""
from world import World, Scene
from entities import Player

class GameEngine:
    def __init__(self):
        self.world = World()
        self.player = Player("玩家")
        self.running = False
        self._setup_world()

    def _setup_world(self):
        """初始化游戏世界，创建初始场景和玩家"""
        # 创建一个初始场景
        starting_scene = Scene("村庄广场", "你正站在村庄的中心广场。四周是一些零散的房屋。")
        self.world.add_scene(starting_scene)
        self.world.set_current_scene("村庄广场")

        # 将玩家放入场景
        self.world.current_scene.add_entity(self.player)
        self._spawn_npcs()
        print("游戏引擎已初始化，世界已创建。")

    def _spawn_npcs(self, max_npcs=3):
        """加载NPC数据并将其添加到世界中"""
        import os
        import json
        from entities import NPC

        npc_dir = "generated_npcs_final/"
        if not os.path.exists(npc_dir):
            print(f"警告: NPC目录 '{npc_dir}' 不存在。")
            return

        npc_files = [f for f in os.listdir(npc_dir) if f.endswith('.json')]

        for i, filename in enumerate(npc_files):
            if i >= max_npcs:
                break

            filepath = os.path.join(npc_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            npc_name = data.get("identity", {}).get("npc_name", "无名氏")
            primary_ism = data.get("identity", {}).get("primary_ism_name", "一个神秘的人")

            # 创建NPC实例
            npc = NPC(name=npc_name, description=primary_ism)
            npc.ism_data = data # 存储完整的“主义”数据

            # 将NPC添加到当前场景
            self.world.current_scene.add_entity(npc)
            print(f"已生成NPC: {npc_name}")

    def run(self):
        """开始游戏主循环"""
        self.running = True
        print("\n欢迎来到这个世界！输入 'look' 观察，输入 'wait' 等待，输入 'quit' 退出。")

        while self.running:
            self.handle_input()

    def handle_input(self):
        """获取并处理玩家输入"""
        command = input("> ").lower().strip()

        if command == "quit":
            self.stop()
        elif command == "look":
            self.do_look()
            self._tick()
        elif command == "wait":
            print("\n你等待了一段时间...")
            self._tick()
        else:
            print("未知的命令。")

    def _tick(self):
        """推进一个游戏时间单位（心跳），让NPC行动"""
        print("--- 时间流逝 ---")
        scene = self.world.current_scene
        for entity in scene.entities:
            # 确保是NPC并且有think方法
            if hasattr(entity, 'think'):
                entity.think()

    def do_look(self):
        """执行 'look' 命令"""
        scene = self.world.current_scene
        print(f"\n--- {scene.name} ---")
        print(scene.description)

        # 显示场景中的其他实体
        other_entities = [e.name for e in scene.entities if e is not self.player]
        if other_entities:
            print("你在这里看到了: " + ", ".join(other_entities))
        else:
            print("这里现在只有你一个人。")

    def stop(self):
        """停止游戏循环"""
        self.running = False