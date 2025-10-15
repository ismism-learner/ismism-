extends Node

const SERVER_URL = "ws://localhost:8765"
const NPCScene = preload("res://NPC.tscn")
const InfoPanelScene = preload("res://InfoPanel.tscn")

var ws_client = WebSocketPeer.new()
var existing_npcs = {} # 用字典来存储已创建的NPC，以ID为键
var info_panel

func _ready():
	print("主场景已就绪，尝试连接到服务器...")
	# Instantiate and hide the info panel
	info_panel = InfoPanelScene.instantiate()
	info_panel.hide()
	add_child(info_panel)
	info_panel.closed.connect(_on_info_panel_closed)

	connect_to_server()

func _process(delta):
	if ws_client.get_ready_state() == WebSocketPeer.STATE_OPEN:
		ws_client.poll()

		var packet = ws_client.get_packet()
		if packet.size() > 0:
			var json_string = packet.get_string_from_utf8()
			var json_data = JSON.parse_string(json_string)
			if typeof(json_data) == TYPE_ARRAY:
				update_world_state(json_data)
	elif ws_client.get_ready_state() == WebSocketPeer.STATE_CLOSED:
		print("连接已断开，尝试重新连接...")
		connect_to_server()
		# 清理一下旧的NPC，避免重连后残留
		for npc_id in existing_npcs:
			existing_npcs[npc_id].queue_free()
		existing_npcs.clear()


func connect_to_server():
	var err = ws_client.connect_to_url(SERVER_URL)
	if err != OK:
		print("连接到服务器失败！")
	else:
		print("正在连接...")


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