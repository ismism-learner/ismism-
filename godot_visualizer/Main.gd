extends Node

const NPCScene = preload("res://NPC.tscn")
const InfoPanelScene = preload("res://InfoPanel.tscn")

var existing_npcs = {} # 用字典来存储已创建的NPC，以ID为键
var info_panel
var world_sim # This will hold our Python simulation object

func _ready():
	print("Main scene ready. Initializing world simulation...")
	# Instantiate and hide the info panel
	info_panel = InfoPanelScene.instantiate()
	info_panel.hide()
	add_child(info_panel)
	info_panel.closed.connect(_on_info_panel_closed)

	# Load the Python simulation script
	var WorldSim_py = load("res://world_sim_bridge.py")
	world_sim = WorldSim_py.new()
	add_child(world_sim)

	# Start the simulation (this will run in a separate thread)
	world_sim.start_simulation()

	print("World simulation started.")

func _process(_delta):
	# Directly get the world state from the Python simulation
	var world_state_json = world_sim.get_world_state_json()
	if world_state_json:
		var json_data = JSON.parse_string(world_state_json)
		if typeof(json_data) == TYPE_ARRAY:
			update_world_state(json_data)

func update_world_state(npcs_data):
	var seen_npc_ids = []
	for data in npcs_data:
		var npc_id = data.id
		seen_npc_ids.append(npc_id)

		if existing_npcs.has(npc_id):
			# NPC已存在，更新状态
			existing_npcs[npc_id].update_state(data)
		else:
			# NPC不存在，创建新实例
			var new_npc = NPCScene.instantiate()
			add_child(new_npc)
			existing_npcs[npc_id] = new_npc
			new_npc.update_state(data) # 设置初始状态
			# Connect the new NPC's signal to our handler
			new_npc.npc_selected.connect(_on_npc_selected)
			print("侦测到新NPC: ", data.name)

	# (可选) 清理那些在服务器最新状态中已不存在的NPC
	var all_known_ids = existing_npcs.keys()
	for id in all_known_ids:
		if not id in seen_npc_ids:
			print("NPC消失: ", existing_npcs[id].get_node("Label").text)
			existing_npcs[id].queue_free()
			existing_npcs.erase(id)

# Signal handler for when an NPC is clicked
func _on_npc_selected(data):
	info_panel.update_data(data)
	# Position the panel slightly to the right of the NPC
	var npc_position = Vector2(data.position.x, data.position.y)
	info_panel.position = npc_position + Vector2(20, -50)
	info_panel.show()

# Signal handler for the panel's close button
func _on_info_panel_closed():
	info_panel.hide()