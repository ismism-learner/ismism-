extends Node2D

@onready var label = $Label

func update_state(data):
	# 使用Tween来平滑地移动到新位置，而不是瞬间移动
	var tween = create_tween()
	tween.tween_property(self, "position", Vector2(data.position.x, data.position.y), 0.4).set_trans(Tween.TRANS_SINE)

	# 更新标签内容
	label.text = "%s\n(%s)" % [data.name, data.action]