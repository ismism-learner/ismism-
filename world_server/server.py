# world_server/server.py
import asyncio
import json
import os
import random
import websockets
import sys

# Make sure the project root is in sys.path, so we can use absolute imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- New ECS Imports ---
from world_server.ecs.world import World as EcsWorld
from world_server.ecs.components.identity import IdentityComponent
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.ism import IsmComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.economy import EconomyComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.relationship import RelationshipComponent
from world_server.ecs.components.financial_component import FinancialComponent
from world_server.ecs.components.hobby_component import HobbyComponent

# --- System Imports ---
from world_server.ecs.systems.needs_system import NeedsSystem
from world_server.ecs.systems.interaction_system import InteractionSystem
from world_server.ecs.systems.movement_system import MovementSystem
from world_server.ecs.systems.action_system import ActionSystem
from world_server.ecs.systems.banking_system import BankingSystem
from world_server.ecs.systems.technology_system import TechnologySystem
from world_server.ecs.systems.hobby_system import HobbySystem


class Server:
    def __init__(self):
        self.ecs_world = EcsWorld()
        self.clients = set()
        self.interactions = []
        self.locations = []
        self.consumer_goods = []
        self.hobby_definitions = []
        self._load_game_definitions()
        self._setup_world()

    def _load_game_definitions(self):
        """Loads all static data files like locations, interactions, goods, etc."""
        # Load locations
        locations_path = "world_server/locations.json"
        try:
            with open(locations_path, 'r', encoding='utf-8') as f:
                locations_data = json.load(f)
            for i, loc in enumerate(locations_data):
                loc['id'] = f"loc_{i}"
                loc['state'] = "active"
                loc['inventory'] = {}
                if loc['type'] == 'FOOD_SOURCE':
                    loc['inventory']['GRAIN'] = 100
                elif loc['type'] == 'WORKPLACE':
                    if loc.get('work_type') == 'FARMING':
                        loc['produces'] = "GRAIN"
                        loc['produces_rate'] = 5
                    elif loc.get('work_type') == 'MINING':
                        loc['produces'] = "ORE"
                        loc['produces_rate'] = 3
            self.locations = locations_data
            print(f"成功加载并初始化 {len(self.locations)} 个地点。")
        except FileNotFoundError:
            print(f"错误: 地点文件 '{locations_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 地点文件 '{locations_path}' 格式无效。")

        # Load interactions
        interactions_path = "world_server/interactions.json"
        try:
            with open(interactions_path, 'r', encoding='utf-8') as f:
                self.interactions = json.load(f)
            print(f"成功加载 {len(self.interactions)} 个互动。")
        except FileNotFoundError:
            print(f"错误: 互动文件 '{interactions_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 互动文件 '{interactions_path}' 格式无效。")

        # Load consumer goods
        goods_path = "world_server/consumer_goods.json"
        try:
            with open(goods_path, 'r', encoding='utf-8') as f:
                self.consumer_goods = json.load(f)
            print(f"成功加载 {len(self.consumer_goods)} 个消费品。")
        except FileNotFoundError:
            print(f"错误: 消费品文件 '{goods_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 消费品文件 '{goods_path}' 格式无效。")

        # Load hobby definitions
        hobbies_path = "world_server/hobby_definitions.json"
        try:
            with open(hobbies_path, 'r', encoding='utf-8') as f:
                self.hobby_definitions = json.load(f)
            print(f"成功加载 {len(self.hobby_definitions)} 个爱好定义。")
        except FileNotFoundError:
            print(f"错误: 爱好文件 '{hobbies_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 爱好文件 '{hobbies_path}' 格式无效。")

    def _setup_world(self):
        """初始化游戏世界，加载资源，创建实体并注册系统"""
        self._spawn_all_npcs()

        # Instantiate and register systems
        self.ecs_world.tech_system = TechnologySystem() # Attach for global access
        self.ecs_world.hobby_system = HobbySystem(self.consumer_goods)

        self.ecs_world.add_system(NeedsSystem())
        self.ecs_world.add_system(self.ecs_world.hobby_system)
        self.ecs_world.add_system(BankingSystem())
        self.ecs_world.add_system(InteractionSystem())
        self.ecs_world.add_system(MovementSystem())
        self.ecs_world.add_system(ActionSystem())
        self.ecs_world.add_system(self.ecs_world.tech_system)

        print("ECS世界服务器初始化完成，所有实体和系统已加载。")

    def _spawn_all_npcs(self):
        """加载所有NPC数据，并将其作为实体和组件添加到ECS世界中"""
        npc_dir = "generated_npcs_final/"
        if not os.path.exists(npc_dir):
            print(f"错误: NPC目录 '{npc_dir}' 不存在。")
            return

        npc_files = [f for f in os.listdir(npc_dir) if f.endswith('.json')]

        for filename in npc_files:
            filepath = os.path.join(npc_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # --- Create Entity and Components ---
            entity_id = self.ecs_world.create_entity()

            # Identity
            npc_name = data.get("identity", {}).get("npc_name", "无名氏")
            primary_ism_desc = data.get("identity", {}).get("primary_ism_name", "一个神秘的人")
            self.ecs_world.add_component(entity_id, IdentityComponent(name=npc_name, description=primary_ism_desc))

            # Position (randomly spawned)
            self.ecs_world.add_component(entity_id, PositionComponent(x=random.randint(50, 750), y=random.randint(50, 550)))

            # Ism
            self.ecs_world.add_component(entity_id, IsmComponent(data=data))

            # Needs & Demands
            needs_comp = NeedsComponent()
            leisure_script = data.get("behavioral_scripts", {}).get("leisure_activity", "IDLE")
            if leisure_script != "IDLE":
                needs_comp.demands.append(leisure_script)
            # Randomize initial needs slightly for variety
            needs_comp.needs['hunger']['current'] = random.randint(0, 40)
            needs_comp.needs['energy']['current'] = random.randint(50, 90)
            needs_comp.needs['stress']['current'] = random.randint(0, 30)
            self.ecs_world.add_component(entity_id, needs_comp)

            # Economy
            self.ecs_world.add_component(entity_id, EconomyComponent(money=random.randint(20, 100)))

            # State
            self.ecs_world.add_component(entity_id, StateComponent())

            # Relationships
            self.ecs_world.add_component(entity_id, RelationshipComponent())

            # Financial
            self.ecs_world.add_component(entity_id, FinancialComponent())

            # Hobbies
            hobby_comp = HobbyComponent()
            # Simple logic: assign interests based on ism keywords
            ism_keywords = " ".join(data.get("philosophy", {}).values())
            if "科学" in ism_keywords or "技术" in ism_keywords:
                hobby_comp.interests["AUTOMATA"] = random.uniform(60, 90)
                hobby_comp.interests["ALCHEMY"] = random.uniform(50, 80)
                hobby_comp.skills[random.choice(["AUTOMATA", "ALCHEMY"])] = random.randint(1, 3)
            if "艺术" in ism_keywords or "美学" in ism_keywords:
                hobby_comp.interests["PAINTING"] = random.uniform(60, 90)
                hobby_comp.interests["CRAFTING"] = random.uniform(40, 70)
                hobby_comp.skills["PAINTING"] = random.randint(1, 3)
            # Give a baseline interest in exercise
            hobby_comp.interests["EXERCISE"] = random.uniform(10, 40)
            self.ecs_world.add_component(entity_id, hobby_comp)


        print(f"成功加载了 {len(npc_files)} 个实体。")

    async def _game_loop(self):
        """
        The main game loop.
        Updates the world state by processing all systems and broadcasts it to clients.
        """
        while True:
            # 1. Update world time
            self.ecs_world.time += 1

            # 2. Process all systems
            # This single call replaces all the old complex logic.
            # It iterates through NeedsSystem, InteractionSystem, MovementSystem, etc.
            self.ecs_world.process(locations=self.locations, interactions=self.interactions)

            # 3. Prepare and broadcast the world state
            world_state = self.get_world_state()
            if self.clients:
                await asyncio.wait([client.send(world_state) for client in self.clients])

            # 4. Wait for the next tick
            await asyncio.sleep(0.5) # Update ~2 times per second

    def get_world_state(self):
        """
        Gathers the state of all relevant entities from the ECS world
        and packages it into the JSON format expected by the Godot client.
        """
        state_list = []

        # Define the components needed for visualization
        required_components = [
            IdentityComponent, PositionComponent, StateComponent, NeedsComponent, RelationshipComponent
        ]

        # Iterate through all entities that have the required components
        for entity_id in self.ecs_world.get_entities_with_components(*required_components):
            # Retrieve all necessary components for this entity
            identity = self.ecs_world.get_component(entity_id, IdentityComponent)
            position = self.ecs_world.get_component(entity_id, PositionComponent)
            state = self.ecs_world.get_component(entity_id, StateComponent)
            needs = self.ecs_world.get_component(entity_id, NeedsComponent)
            relationships = self.ecs_world.get_component(entity_id, RelationshipComponent)

            # Convert relationship keys from UUID to string for JSON serialization
            serializable_relationships = {str(k): v for k, v in relationships.relations.items()}

            entity_state = {
                "id": str(entity_id),
                "name": identity.name,
                "position": {"x": position.x, "y": position.y},
                "action": state.action,
                "goal": str(state.goal), # Convert complex goal objects to string for simple display
                "needs": needs.needs,
                "rupture": needs.desire['real']['rupture'],
                "relationships": serializable_relationships
            }
            state_list.append(entity_state)

        return json.dumps(state_list)

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
    try:
        asyncio.run(server.start("localhost", 8765))
    except KeyboardInterrupt:
        print("服务器已手动关闭。")