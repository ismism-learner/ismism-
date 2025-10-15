extends Control

# This signal will be emitted when the close button is pressed.
signal closed

# UI element references will be assigned here
@onready var name_label = $VBoxContainer/NameLabel
@onready var action_label = $VBoxContainer/ActionLabel
@onready var goal_label = $VBoxContainer/GoalLabel
@onready var needs_label = $VBoxContainer/NeedsLabel
@onready var rupture_label = $VBoxContainer/RuptureLabel
@onready var relationships_label = $VBoxContainer/RelationshipsLabel
@onready var close_button = $CloseButton

func _ready():
	# Connect the close button's pressed signal to our handler
	close_button.pressed.connect(_on_close_button_pressed)

# Public function to update the panel with new data
func update_data(data):
	name_label.text = "Name: %s" % data.name
	action_label.text = "Action: %s" % data.action
	goal_label.text = "Goal: %s" % data.goal

	var needs_text = "Needs:\n"
	for need_name in data.needs:
		var need_info = data.needs[need_name]
		needs_text += "  %s: %d/%d\n" % [need_name, need_info.current, need_info.max]
	needs_label.text = needs_text

	rupture_label.text = "Rupture: %.2f" % data.rupture

	var rel_text = "Relationships:\n"
	if data.relationships.is_empty():
		rel_text += "  None"
	else:
		for target_id in data.relationships:
			var rel_data = data.relationships[target_id]
			rel_text += "  %s: %s (Affinity: %.2f)\n" % [target_id.left(6), rel_data.status, rel_data.affinity]
	relationships_label.text = rel_text

	# Make sure the panel is visible when updated
	show()

# Private handler for the close button
func _on_close_button_pressed():
	hide()
	emit_signal("closed")