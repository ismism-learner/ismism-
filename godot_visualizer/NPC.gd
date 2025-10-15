extends Node2D

signal npc_selected(data)

@onready var label = $Label
@onready var clickable_area = $ClickableArea
var npc_data # Store the NPC's data

func _ready():
	clickable_area.gui_input.connect(_on_gui_input)

func _on_gui_input(event):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		emit_signal("npc_selected", npc_data)

func update_state(data):
	npc_data = data # Store the latest data

	# 使用Tween来平滑地移动到新位置，而不是瞬间移动
	var tween = create_tween()
	tween.tween_property(self, "position", Vector2(data.position.x, data.position.y), 0.4).set_trans(Tween.TRANS_SINE)

	# 更新标签内容
	label.text = "%s\n(%s)" % [data.name, data.action]