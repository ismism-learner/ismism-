# world_server/server.py
import json
import os
import random
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
# No longer needed as we load from database


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
        # --- Path Correction ---
        # Get the absolute path to the directory containing this script.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the project root by going one level up.
        project_root = os.path.abspath(os.path.join(script_dir, '..'))

        # Helper function to load JSON files safely.
        def load_json_file(file_path, error_message, default_value=None):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"错误: {error_message} '{file_path}' 未找到。")
                return default_value
            except json.JSONDecodeError:
                print(f"错误: {error_message} '{file_path}' 格式无效。")
                return default_value

        # Load the new quantified ism data
        isms_path = os.path.join(project_root, "isms_final.json")
        self.all_isms_data = load_json_file(isms_path, "主义数据文件", [])
        if self.all_isms_data:
            self.isms_by_id = {ism['id']: ism for ism in self.all_isms_data if 'id' in ism}
            print(f"成功加载并量化 {len(self.all_isms_data)} 个主义。")
            print(f"为 {len(self.isms_by_id)} 个主义创建了ID查找表。")
        else:
             print(f"错误: 主义数据文件 '{isms_path}' 未找到。请确保已运行 excel_parser.py。")


        # Load locations
        locations_path = os.path.join(script_dir, "locations.json")
        locations_data = load_json_file(locations_path, "地点文件", [])
        if locations_data:
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

        # Load interactions
        interactions_path = os.path.join(script_dir, "interactions.json")
        self.interactions = load_json_file(interactions_path, "互动文件", [])
        if self.interactions:
            print(f"成功加载 {len(self.interactions)} 个互动。")

        # Load consumer goods
        goods_path = os.path.join(script_dir, "consumer_goods.json")
        self.consumer_goods = load_json_file(goods_path, "消费品文件", [])
        if self.consumer_goods:
            print(f"成功加载 {len(self.consumer_goods)} 个消费品。")

        # Load hobby definitions
        hobbies_path = os.path.join(script_dir, "hobby_definitions.json")
        self.hobby_definitions = load_json_file(hobbies_path, "爱好文件", [])
        if self.hobby_definitions:
            print(f"成功加载 {len(self.hobby_definitions)} 个爱好定义。")

        # Load relationship types
        relationship_types_path = os.path.join(script_dir, "relationship_types.json")
        self.relationship_types = load_json_file(relationship_types_path, "关系类型文件", {})
        if self.relationship_types:
            print(f"成功加载 {len(self.relationship_types)} 个关系类型。")

        # Load collective actions (optional)
        collective_actions_path = os.path.join(script_dir, "collective_actions.json")
        self.collective_actions = load_json_file(collective_actions_path, "集体行动文件", [])
        if self.collective_actions:
             print(f"成功加载 {len(self.collective_actions)} 个集体行动。")
        else:
            print(f"信息: 集体行动文件 '{collective_actions_path}' 未找到。将使用空列表。")


        # Load regions
        regions_path = os.path.join(script_dir, "regions.json")
        self.regions = load_json_file(regions_path, "区域文件", {})
        if self.regions:
            print(f"成功加载 {len(self.regions)} 个区域。")

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
        """Loads NPCs from the pre-generated database file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "npc_database.json")

        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                npc_database = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading NPC database: {e}. Please run npc_database_generator.py first.")
            return

        for npc_data in npc_database:
            entity_id = self.ecs_world.create_entity() # Let the world generate the ID

            # Reconstruct components from the database
            components = npc_data['components']

            # Identity
            id_data = components['identity']
            self.ecs_world.add_component(entity_id, IdentityComponent(
                name=id_data['name'],
                description=id_data['description'],
                birthplace=id_data['birthplace'],
                biography=id_data['biography']
            ))

            # Position
            pos_data = components['position']
            self.ecs_world.add_component(entity_id, PositionComponent(x=pos_data['x'], y=pos_data['y']))

            # Ism
            ism_data = components['ism']
            ism_comp = IsmComponent()
            self.ecs_world.add_component(entity_id, ism_comp)
            ism_comp.active_ideologies = ism_data['active_ideologies']

            # Needs
            needs_data = components['needs']
            needs_comp = NeedsComponent()
            needs_comp.needs = needs_data['needs']
            needs_comp.demands = needs_data['demands']
            needs_comp.desire = needs_data['desire']
            self.ecs_world.add_component(entity_id, needs_comp)

            # Economy
            econ_data = components['economy']
            self.ecs_world.add_component(entity_id, EconomyComponent(money=econ_data['money']))

            # State
            state_data = components['state']
            self.ecs_world.add_component(entity_id, StateComponent(action=state_data['action'], goal=state_data['goal']))

            # Relationship
            self.ecs_world.add_component(entity_id, RelationshipComponent()) # Starts empty

            # Financial
            fin_data = components['financial']
            self.ecs_world.add_component(entity_id, FinancialComponent(loans=fin_data['loans']))

            # Hobby
            hobby_data = components['hobby']
            hobby_comp = HobbyComponent()
            hobby_comp.interests = hobby_data['interests']
            hobby_comp.skills = hobby_data['skills']
            hobby_comp.inventory = hobby_data['inventory']
            self.ecs_world.add_component(entity_id, hobby_comp)

            # Memory Components
            self.ecs_world.add_component(entity_id, SensoryLogComponent())
            self.ecs_world.add_component(entity_id, SocialLedgerComponent())
            self.ecs_world.add_component(entity_id, CognitiveMapComponent())
            self.ecs_world.add_component(entity_id, PraxisLedgerComponent())

        print(f"成功从数据库加载了 {len(npc_database)} 个NPC。")

    def update_simulation(self):
        """Processes one tick of the simulation."""
        self.ecs_world.time += 1
        self.ecs_world.process(
            locations=self.locations,
            interactions=self.interactions,
            relationship_types=self.relationship_types,
            consumer_goods=self.consumer_goods,
            collective_actions=self.collective_actions
        )

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
