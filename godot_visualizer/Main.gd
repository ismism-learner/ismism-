extends Node

const NPCScene = preload("res://NPC.tscn")
const InfoPanelScene = preload("res://InfoPanel.tscn")

var existing_npcs = {}

# --- C# Systems ---
const NpcGenerationSystem = preload("res://ecs/systems/NpcGenerationSystem.cs")
const GovernanceSystem = preload("res://ecs/systems/GovernanceSystem.cs")
const PlanningSystem = preload("res://ecs/systems/PlanningSystem.cs")
const ActionSystem = preload("res://ecs/systems/ActionSystem.cs")
const ManagementSystem = preload("res://ecs/systems/ManagementSystem.cs")
const MovementSystem = preload("res://ecs/systems/MovementSystem.cs")
const NeedsSystem = preload("res://ecs/systems/NeedsSystem.cs")
const ScheduleSystem = preload("res://ecs/systems/ScheduleSystem.cs")


func _ready():
	print("Main scene ready. Initializing C# ECS...")

	var info_panel = InfoPanelScene.instantiate()
	info_panel.hide()
	add_child(info_panel)
	info_panel.closed.connect(_on_info_panel_closed)

	World.AddSystem(NpcGenerationSystem.new())
	World.AddSystem(GovernanceSystem.new())
	World.AddSystem(PlanningSystem.new())
	World.AddSystem(ActionSystem.new())
	World.AddSystem(ManagementSystem.new())
	World.AddSystem(MovementSystem.new())
	World.AddSystem(NeedsSystem.new())
	World.AddSystem(ScheduleSystem.new())

	print("C# ECS Initialized and running.")
	# draw_village() # This is no longer needed as we don't have a village layout

func _process(_delta):
	update_world_state()

func update_world_state():
	var seen_npc_ids = []
	var npc_entities = World.GetEntitiesWithComponents(
		Csharp.GetManagedType(Ecs.Components.IdentityComponent)
	)

	for entity_id in npc_entities:
		seen_npc_ids.append(entity_id)
		# For performance, we don't create visual nodes for thousands of NPCs
		# We can add specific visualizers later if needed.

	# Logic for cleaning up nodes can be added here if we ever visualize them.

func get_npc_data_from_ecs(entity_id):
	# This can be expanded to show more data in a debug view
	var identity = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.IdentityComponent))
	var financial = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.FinancialComponent))
	var sheet = World.GetComponent(entity_id, Csharp.GetManagedType(Ecs.Components.CharacterSheetComponent))

	var data = {
		"id": entity_id,
		"name": identity.Name,
		"money": financial.Money,
		"gdp_contrib": financial.GdpContribution,
		"work_hours": sheet.WorkHoursPerDay,
		"grievance": sheet.Grievance
	}
	return data

# InfoPanel functions can be re-enabled for debugging a specific NPC
func _on_npc_selected(entity_id):
	pass

func _on_info_panel_closed():
	pass