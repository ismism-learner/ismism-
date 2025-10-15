extends Node2D

# This signal now emits the entity ID, not the whole data dictionary.
signal npc_selected(entity_id)

@onready var label = $Label
@onready var clickable_area = $ClickableArea

var entity_id: int = -1 # Store the NPC's unique entity ID from the ECS.

func _ready():
	clickable_area.gui_input.connect(_on_gui_input)

func _on_gui_input(event):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if entity_id != -1:
			emit_signal("npc_selected", entity_id)

func update_state(data):
	# Store the entity ID
	self.entity_id = data.id

	# Use a Tween to smoothly move to the new position
	var tween = create_tween()
	tween.tween_property(self, "position", data.position, 0.4).set_trans(Tween.TRANS_SINE)

	# Update the label content
	# We can add more info here later, like the current state from StateComponent.
	label.text = "%s" % [data.name]