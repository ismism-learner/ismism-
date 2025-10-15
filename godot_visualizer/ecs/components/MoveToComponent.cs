using Godot;

public partial class MoveToComponent : Component
{
    public Vector2 TargetPosition { get; set; }

    public MoveToComponent(Vector2 targetPosition)
    {
        TargetPosition = targetPosition;
    }
}