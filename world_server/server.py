# world_server/server.py
import asyncio
import json
import os
import websockets
from world import World, Scene
from entities import NPC

class Server:
    def __init__(self):
        self.world = World()
        self.clients = set()
        self.interactions = []
        self._load_interactions()
        self._setup_world()

    def _load_locations(self):
        """加载所有可能的地点"""
        locations_path = "world_server/locations.json"
        try:
            with open(locations_path, 'r', encoding='utf-8') as f:
                self.world.current_scene.locations = json.load(f)
            print(f"成功加载 {len(self.world.current_scene.locations)} 个地点。")
        except FileNotFoundError:
            print(f"错误: 地点文件 '{locations_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 地点文件 '{locations_path}' 格式无效。")

    def _load_interactions(self):
        """加载所有可能的互动行为"""
        interactions_path = "world_server/interactions.json"
        try:
            with open(interactions_path, 'r', encoding='utf-8') as f:
                self.interactions = json.load(f)
            print(f"成功加载 {len(self.interactions)} 个互动。")
        except FileNotFoundError:
            print(f"错误: 互动文件 '{interactions_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 互动文件 '{interactions_path}' 格式无效。")

    def _setup_world(self):
        """初始化游戏世界，创建场景并加载所有NPC"""
        starting_scene = Scene("MainWorld", "The main world space for all NPCs.")
        self.world.add_scene(starting_scene)
        self.world.set_current_scene("MainWorld")
        self._load_locations() # 加载地点
        self._spawn_all_npcs()
        print("世界服务器初始化完成，所有NPC已加载。")

    def _spawn_all_npcs(self):
        """加载所有NPC数据并将其添加到世界中"""
        npc_dir = "generated_npcs_final/"
        if not os.path.exists(npc_dir):
            print(f"错误: NPC目录 '{npc_dir}' 不存在。")
            return

        npc_files = [f for f in os.listdir(npc_dir) if f.endswith('.json')]

        for filename in npc_files:
            filepath = os.path.join(npc_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            npc_name = data.get("identity", {}).get("npc_name", "无名氏")
            primary_ism = data.get("identity", {}).get("primary_ism_name", "一个神秘的人")

            npc = NPC(name=npc_name, description=primary_ism)
            npc.ism_data = data

            # 从 'ism' 数据中提取行为脚本作为初始 'Demand'
            leisure_script = data.get("behavioral_scripts", {}).get("leisure_activity", "IDLE")
            if leisure_script != "IDLE":
                npc.demands.append(leisure_script)

            self.world.current_scene.add_entity(npc)

        print(f"成功加载了 {len(npc_files)} 个NPC。")

    async def _game_loop(self):
        """游戏主循环，定期更新并广播状态"""
        last_hour = 0
        while True:
            # 1. 更新世界时间
            self.world.time += 1
            current_hour = self.world.time // self.world.ticks_per_hour

            # 2. 更新所有NPC的状态
            if self.world.current_scene:
                all_entities = self.world.current_scene.entities

                # 如果游戏内小时发生变化，则更新所有NPC的需求
                if current_hour > last_hour:
                    for entity in all_entities:
                        if isinstance(entity, NPC):
                            # 更新饥饿
                            hunger_change = entity.needs['hunger']['change_per_hour']
                            entity.needs['hunger']['current'] = min(entity.needs['hunger']['max'], entity.needs['hunger']['current'] + hunger_change)
                            # 更新精力
                            energy_change = entity.needs['energy']['change_per_hour']
                            entity.needs['energy']['current'] = max(0, entity.needs['energy']['current'] + energy_change)
                            # 更新理想主义 (缓慢衰减)
                            idealism_change = entity.needs['idealism']['change_per_hour']
                            entity.needs['idealism']['current'] = max(0, entity.needs['idealism']['current'] + idealism_change)
                    last_hour = current_hour

                # 每个tick都执行思考逻辑
                for entity in all_entities:
                    if isinstance(entity, NPC):
                        entity.think(all_entities, self.interactions, self.world.current_scene.locations)

            # 3. 准备要发送的状态数据
            world_state = self.get_world_state()

            # 3. 将状态广播给所有连接的客户端
            if self.clients:
                await asyncio.wait([client.send(world_state) for client in self.clients])

            # 4. 等待下一个心跳
            await asyncio.sleep(0.5) # 每秒更新2次

    def get_world_state(self):
        """获取当前世界所有NPC的状态，并打包成JSON"""
        state = []
        if self.world.current_scene:
            for entity in self.world.current_scene.entities:
                if isinstance(entity, NPC):
                    state.append({
                        "id": entity.id,
                        "name": entity.name,
                        "position": entity.position,
                        "action": entity.current_action,
                        "goal": entity.current_goal,
                        "needs": entity.needs,
                        "rupture": entity.desire['real']['rupture'],
                        "relationships": entity.relationships
                    })
        return json.dumps(state)

    async def register(self, websocket):
        """注册新的客户端连接"""
        self.clients.add(websocket)
        print(f"新客户端连接: {websocket.remote_address}")
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"客户端断开连接: {websocket.remote_address}")

    async def start(self, host, port):
        """启动服务器"""
        print(f"WebSocket服务器正在启动，监听地址 ws://{host}:{port}")
        async with websockets.serve(self.register, host, port):
            await self._game_loop()

if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start("localhost", 8765))