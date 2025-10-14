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
        self._setup_world()

    def _setup_world(self):
        """初始化游戏世界，创建场景并加载所有NPC"""
        starting_scene = Scene("MainWorld", "The main world space for all NPCs.")
        self.world.add_scene(starting_scene)
        self.world.set_current_scene("MainWorld")
        self._spawn_all_npcs()
        print("世界服务器初始化完成，所有NPC已加载。")

    def _spawn_all_npcs(self):
        """加载所有NPC数据并将其添加到世界中"""
        npc_dir = "../generated_npcs_final/"
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

            self.world.current_scene.add_entity(npc)

        print(f"成功加载了 {len(npc_files)} 个NPC。")

    async def _game_loop(self):
        """游戏主循环，定期更新并广播状态"""
        while True:
            # 1. 更新所有NPC的状态
            if self.world.current_scene:
                for entity in self.world.current_scene.entities:
                    if isinstance(entity, NPC):
                        entity.think()

            # 2. 准备要发送的状态数据
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
                        "action": entity.current_action
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