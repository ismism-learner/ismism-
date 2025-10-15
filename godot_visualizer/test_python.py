import godot

@godot.expose_script_class
class MyNode(godot.Node):

    def _ready(self):
        godot.print("Hello from Python!")