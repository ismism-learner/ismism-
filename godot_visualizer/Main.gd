extends Node

const NPCScene = preload("res://NPC.tscn")
const InfoPanelScene = preload("res://InfoPanel.tscn")

var existing_npcs = {} # Dictionary to store created NPCs by entity ID.
var info_panel

# --- C# Systems ---
# We need to load the C# scripts to be able to instantiate them.
const MovementSystem = preload("res://ecs/systems/MovementSystem.cs")
const NeedsSystem = preload("res://ecs/systems/NeedsSystem.cs")
const InteractionSystem = preload("res://ecs/systems/InteractionSystem.cs")
const ActionSystem = preload("res://ecs/systems/ActionSystem.cs")
const IdeologySystem = preload("res://ecs/systems/IdeologySystem.cs")
const ScheduleSystem = preload("res://ecs/systems/ScheduleSystem.cs")
const DataProcessor = preload("res://managers/DataProcessor.cs")
const NpcGenerationSystem = preload("res://ecs/systems/NpcGenerationSystem.cs")
# Add other systems as needed...

func _ready():
	print("Main scene ready. Initializing C# ECS...")

	# First, process the ism data
	var data_processor = DataProcessor.new()
	add_child(data_processor)
	data_processor.ProcessAndSaveIsms("res://../isms_final.json", "res://../rules.json", "res://world_server/isms_final.json")


	# Instantiate and hide the info panel
	info_panel = InfoPanelScene.instantiate()
	info_panel.hide()
	add_child(info_panel)
	info_panel.closed.connect(_on_info_panel_closed)

	# The World and Managers are autoloads, so we can access them directly.
	# Now, we instantiate and add our C# systems to the World.
	World.AddSystem(NpcGenerationSystem.new())
	World.AddSystem(MovementSystem.new())
	World.AddSystem(NeedsSystem.new())
	World.AddSystem(InteractionSystem.new())
	World.AddSystem(ActionSystem.new())
	World.AddSystem(IdeologySystem.new())
	World.AddSystem(ScheduleSystem.new())

	# The World's _PhysicsProcess will now run the simulation automatically.
	print("C# ECS Initialized and running.")

	draw_village()

func draw_village():
	var buildings = VillageManager.Buildings
	for building in buildings:
		var rect = ColorRect.new()
		rect.size = Vector2(80, 50)
		rect.color = Color.DARK_GOLDENROD if building.BuildingType == "Workshop" else Color.BURLYWOOD
		rect.position = building.Position - rect.size / 2
		add_child(rect)

		var label = Label.new()
		label.text = building.Name
		label.position = rect.position + Vector2(5, 5)
		label.add_theme_color_override("font_color", Color.BLACK)
		label.add_theme_font_size_override("font_size", 10)
		add_child(label)

func _process(_delta):
	# This function now syncs the Godot nodes with the ECS state.
	# The actual simulation logic runs in World._PhysicsProcess.
	update_world_state()

func update_world_state():
	var seen_npc_ids = []
	# Get all entities that have the core NPC components from the C# World
	var npc_entities = World.GetEntitiesWithComponents(
		Csharp.GetManagedType(Ecs.Components.IdentityComponent),
		Csharp.GetManagedType(Ecs.Components.PositionComponent)
	)

	for entity_id in npc_entities:
		seen_npc_ids.append(entity_id)

		var data = get_npc_data_from_ecs(entity_id)

		if existing_npcs.has(entity_id):
			# NPC exists, update its state
			existing_npcs[entity_id].update_state(data)
		else:
			# NPC doesn't exist, create a new instance
			var new_npc = NPCScene.instantiate()
			add_child(new_npc)
			existing_npcs[entity_id] = new_npc
			new_npc.update_state(data) # Set initial state
			new_npc.npc_selected.connect(_on_npc_selected)
			print("New NPC detected: ", data.name)

	# Clean up NPCs that no longer exist in the ECS
	var all_known_ids = existing_npcs.keys()
	for id in all_known_ids:
		if not id in seen_npc_ids:
			print("NPC disappeared: ", existing_npcs[id].get_node("Label").text)
			existing_npcs[id].queue_free()
			existing_npcs.erase(id)

func get_npc_data_from_ecs(entity_id):
	# This function queries the C# ECS for a specific NPC's data
	var identity = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.IdentityComponent))
	var pos = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.PositionComponent))
	var needs = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.NeedsComponent))
	var financial = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.FinancialComponent))

	var data = {
		"id": entity_id,
		"name": identity.Name,
		"position": pos.Position,
		"stress": needs.Stress,
		"hunger": needs.Hunger,
		"money": financial.Money
		# Add other data points as needed for the info panel
	}
	return data

func _on_npc_selected(entity_id):
	var data = get_npc_data_from_ecs(entity_id)
	info_panel.update_data(data)
	info_panel.position = data.position + Vector2(20, -50)
	info_panel.show()

func _on_info_panel_closed():
	info_panel.hide()