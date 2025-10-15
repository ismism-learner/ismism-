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
from world_server.ecs.components.sensory_log_component import SensoryLogComponent
from world_server.ecs.components.social_ledger_component import SocialLedgerComponent
from world_server.ecs.components.cognitive_map_component import CognitiveMapComponent
from world_server.ecs.components.praxis_ledger_component import PraxisLedgerComponent


# --- System Imports ---
from world_server.ecs.systems.motivation_system import MotivationSystem
from world_server.ecs.systems.needs_system import NeedsSystem
from world_server.ecs.systems.interaction_system import InteractionSystem
from world_server.ecs.systems.movement_system import MovementSystem
from world_server.ecs.systems.action_system import ActionSystem
from world_server.ecs.systems.banking_system import BankingSystem
from world_server.ecs.systems.technology_system import TechnologySystem
from world_server.ecs.systems.hobby_system import HobbySystem
from world_server.ecs.systems.desire_system import DesireSystem
from world_server.ecs.systems.collective_action_system import CollectiveActionSystem
from world_server.ecs.systems.evolution_system import EvolutionSystem
from world_server.ecs.systems.ideology_system import IdeologySystem

# --- Generator Imports ---
from world_server.generators.biography_generator import generate_biography
from world_server.generators.mind_generator import generate_npc_mind


class Server:
    def __init__(self):
        self.ecs_world = EcsWorld()
        self.clients = set()
        self.interactions = []
        self.locations = []
        self.consumer_goods = []
        self.hobby_definitions = []
        self.relationship_types = {}
        self.collective_actions = []
        self.all_isms_data = [] # To store the new quantified ism data
        self.isms_by_id = {} # For quick lookup
        self.regions = {}
        self._load_game_definitions()
        self._setup_world()

    def _load_game_definitions(self):
        """Loads all static data files like locations, interactions, goods, etc."""
        # Load the new quantified ism data
        isms_path = "isms_final.json"
        try:
            with open(isms_path, 'r', encoding='utf-8') as f:
                self.all_isms_data = json.load(f)
            # Create a lookup dictionary for isms by their ID
            self.isms_by_id = {ism['id']: ism for ism in self.all_isms_data if 'id' in ism}
            print(f"成功加载并量化 {len(self.all_isms_data)} 个主义。")
            print(f"为 {len(self.isms_by_id)} 个主义创建了ID查找表。")
        except FileNotFoundError:
            print(f"错误: 主义数据文件 '{isms_path}' 未找到。请确保已运行 excel_parser.py。")
            self.all_isms_data = []
        except json.JSONDecodeError:
            print(f"错误: 主义数据文件 '{isms_path}' 格式无效。")

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

        # Load relationship types
        relationship_types_path = "world_server/relationship_types.json"
        try:
            with open(relationship_types_path, 'r', encoding='utf-8') as f:
                self.relationship_types = json.load(f)
            print(f"成功加载 {len(self.relationship_types)} 个关系类型。")
        except FileNotFoundError:
            print(f"错误: 关系类型文件 '{relationship_types_path}' 未找到。")
        except json.JSONDecodeError:
            print(f"错误: 关系类型文件 '{relationship_types_path}' 格式无效。")

        # Load collective actions
        collective_actions_path = "world_server/collective_actions.json"
        try:
            with open(collective_actions_path, 'r', encoding='utf-8') as f:
                self.collective_actions = json.load(f)
            print(f"成功加载 {len(self.collective_actions)} 个集体行动。")
        except FileNotFoundError:
            print(f"信息: 集体行动文件 '{collective_actions_path}' 未找到。将使用空列表。")
            self.collective_actions = []
        except json.JSONDecodeError:
            print(f"错误: 集体行动文件 '{collective_actions_path}' 格式无效。")

        # Load regions
        regions_path = "world_server/regions.json"
        try:
            with open(regions_path, 'r', encoding='utf-8') as f:
                self.regions = json.load(f)
            print(f"成功加载 {len(self.regions)} 个区域。")
        except FileNotFoundError:
            print(f"错误: 区域文件 '{regions_path}' 未找到。")
            self.regions = {}
        except json.JSONDecodeError:
            print(f"错误: 区域文件 '{regions_path}' 格式无效。")
            self.regions = {}

    def _setup_world(self):
        """初始化游戏世界，加载资源，创建实体并注册系统"""
        self._spawn_all_npcs()

        # Instantiate and register systems
        self.ecs_world.tech_system = TechnologySystem() # Attach for global access
        self.ecs_world.hobby_system = HobbySystem(self.consumer_goods)
        self.ecs_world.desire_system = DesireSystem() # Attach for global access

        # Add the new MotivationSystem first to set high-level goals
        self.ecs_world.add_system(MotivationSystem())
        self.ecs_world.add_system(self.ecs_world.desire_system)
        self.ecs_world.add_system(NeedsSystem())
        self.ecs_world.add_system(self.ecs_world.hobby_system)
        self.ecs_world.add_system(BankingSystem())
        self.ecs_world.add_system(InteractionSystem())
        self.ecs_world.add_system(MovementSystem())
        self.ecs_world.add_system(ActionSystem())
        self.ecs_world.add_system(self.ecs_world.tech_system)
        self.ecs_world.add_system(CollectiveActionSystem())
        # Attach for global access before adding to processing list
        self.ecs_world.ideology_system = IdeologySystem()

        # Process evolution and ideology decay after actions have been taken
        self.ecs_world.add_system(EvolutionSystem())
        self.ecs_world.add_system(self.ecs_world.ideology_system)

        print("ECS世界服务器初始化完成，所有实体和系统已加载。")

    def _spawn_all_npcs(self):
        """Creates NPCs based on biography and regional culture, adding them as entities to the ECS world."""
        if not self.isms_by_id:
            print("错误: 没有可用的主义数据来生成NPC。")
            return
        if not self.locations or not self.regions:
            print("错误: 地点或区域数据不完整，无法按环境生成NPC。")
            return

        num_npcs_to_spawn = 50
        spawned_count = 0
        for i in range(num_npcs_to_spawn):
            # 1. Select birthplace and region
            birthplace_loc = random.choice(self.locations)
            birthplace_id = birthplace_loc['id']
            region_id = birthplace_loc.get('region_id')

            if not region_id or region_id not in self.regions:
                print(f"警告: 地点 {birthplace_id} ({birthplace_loc.get('name')}) 没有有效的区域ID。跳过此NPC生成。")
                continue

            region_data = self.regions[region_id]

            # 2. Generate Biography
            biography = generate_biography(region_id, region_data)

            # 3. Generate Mind (Ideologies)
            initial_ideologies = generate_npc_mind(region_data, biography, self.isms_by_id)

            if not initial_ideologies:
                print(f"警告: 无法为区域 {region_id} 的NPC生成意识形态。可能是Meme Pool为空。跳过。")
                continue

            # --- END: New Generation Logic ---

            # Create Entity and Components
            entity_id = self.ecs_world.create_entity()

            # Identity
            primary_ism_id = initial_ideologies[0]['code']
            ism_data = self.isms_by_id.get(primary_ism_id, {})
            npc_name = ism_data.get("name", "无名氏")

            # Store the generated biography within the IdentityComponent
            identity_comp = IdentityComponent(name=npc_name,
                                              description=f"A {biography['social_class']} with {biography['education']} education.",
                                              birthplace=birthplace_id,
                                              biography=biography)
            self.ecs_world.add_component(entity_id, identity_comp)

            # Position (randomly spawned)
            self.ecs_world.add_component(entity_id, PositionComponent(x=random.randint(50, 750), y=random.randint(50, 550)))

            # IsmComponent setup with the new multi-ideology structure
            ism_comp = IsmComponent(active_ideologies=initial_ideologies)
            self.ecs_world.add_component(entity_id, ism_comp)

            # Needs & Demands
            needs_comp = NeedsComponent()

            # --- Enhanced Environmental Effects ---
            initial_stress = random.randint(0, 30)
            initial_money = random.randint(20, 100)
            birthplace_type = birthplace_loc.get('type')

            if birthplace_type in ['WORKPLACE', 'FOOD_SOURCE']:
                initial_stress += 10; initial_money -= 15
            elif birthplace_type in ['CENTRAL_BANK', 'COMMERCIAL_BANK', 'MARKETPLACE']:
                initial_stress -= 5; initial_money += 30

            initial_stress = max(0, min(initial_stress, 100))
            initial_money = max(1, initial_money)

            needs_comp.needs['hunger']['current'] = random.randint(0, 40)
            needs_comp.needs['energy']['current'] = random.randint(50, 90)
            needs_comp.needs['stress']['current'] = initial_stress
            self.ecs_world.add_component(entity_id, needs_comp)

            # Economy & State
            self.ecs_world.add_component(entity_id, EconomyComponent(money=initial_money))
            self.ecs_world.add_component(entity_id, StateComponent())

            # Relationships & Financial
            self.ecs_world.add_component(entity_id, RelationshipComponent())
            self.ecs_world.add_component(entity_id, FinancialComponent())

            # Hobbies
            hobby_comp = HobbyComponent()

            # Aggregate keywords from all active ideologies
            all_philosophy_keywords = []
            for ideology in initial_ideologies:
                philosophy_values = []
                def extract_values(d):
                    for v in d.values():
                        if isinstance(v, str): philosophy_values.append(v)
                        elif isinstance(v, dict): extract_values(v)
                extract_values(ideology.get("data", {}))
                all_philosophy_keywords.extend(philosophy_values)

            ism_keywords = " ".join(all_philosophy_keywords)

            if "科学" in ism_keywords or "技术" in ism_keywords:
                hobby_comp.interests["AUTOMATA"] = random.uniform(60, 90)
                hobby_comp.interests["ALCHEMY"] = random.uniform(50, 80)
                hobby_comp.skills[random.choice(["AUTOMATA", "ALCHEMY"])] = random.randint(1, 3)
            if "艺术" in ism_keywords or "美学" in ism_keywords:
                hobby_comp.interests["PAINTING"] = random.uniform(60, 90)
                hobby_comp.interests["CRAFTING"] = random.uniform(40, 70)
                hobby_comp.skills["PAINTING"] = random.randint(1, 3)
            hobby_comp.interests["EXERCISE"] = random.uniform(10, 40)
            self.ecs_world.add_component(entity_id, hobby_comp)

            # --- Add WD-MME Memory Components ---
            self.ecs_world.add_component(entity_id, SensoryLogComponent())
            self.ecs_world.add_component(entity_id, SocialLedgerComponent())
            self.ecs_world.add_component(entity_id, CognitiveMapComponent())
            self.ecs_world.add_component(entity_id, PraxisLedgerComponent())

            spawned_count += 1

        print(f"成功生成了 {spawned_count} 个实体。")

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
            self.ecs_world.process(
                locations=self.locations,
                interactions=self.interactions,
                relationship_types=self.relationship_types,
                consumer_goods=self.consumer_goods,
                collective_actions=self.collective_actions
            )

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