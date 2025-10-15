#if TOOLS
using Godot;
using Managers;

[Tool]
public partial class DataProcessingTool : EditorPlugin
{
    private Button processButton;

    public override void _EnterTree()
    {
        // Add a custom button to the editor toolbar
        processButton = new Button();
        processButton.Text = "Process Isms";
        processButton.Pressed += OnProcessButtonPressed;
        AddControlToContainer(CustomControlContainer.Toolbar, processButton);
    }

    public override void _ExitTree()
    {
        // Clean up the button when the plugin is disabled
        if (processButton != null)
        {
            RemoveControlFromContainer(CustomControlContainer.Toolbar, processButton);
            processButton.QueueFree();
        }
    }

    private void OnProcessButtonPressed()
    {
        GD.Print("Editor Tool: Starting ism data processing...");

        // We need to instantiate the DataProcessor to use it.
        // Since this is an editor tool, we can't rely on autoloads.
        var dataProcessor = new DataProcessor();

        // We need to add it to the tree to make sure it's part of the scene,
        // even if it's just for a moment.
        GetEditorInterface().GetBaseControl().AddChild(dataProcessor);

        try
        {
            // Define paths relative to the project root
            string rawIsmsPath = "res://../isms_final.json";
            string rulesPath = "res://../rules.json";
            string outputPath = "res://world_server/isms_final.json";

            dataProcessor.ProcessAndSaveIsms(rawIsmsPath, rulesPath, outputPath);

            GD.Print("Editor Tool: Ism data processing complete.");

            // Show a popup to the user
            var dialog = new AcceptDialog
            {
                DialogText = "Successfully processed and saved isms_final.json!",
                Title = "Processing Complete"
            };
            GetEditorInterface().GetBaseControl().AddChild(dialog);
            dialog.PopupCentered();
        }
        catch (System.Exception e)
        {
            GD.PrintErr($"An error occurred during data processing: {e.Message}");
            var dialog = new AcceptDialog
            {
                DialogText = $"An error occurred: {e.Message}",
                Title = "Processing Failed"
            };
            GetEditorInterface().GetBaseControl().AddChild(dialog);
            dialog.PopupCentered();
        }
        finally
        {
            // Clean up the node
            dataProcessor.QueueFree();
        }
    }
}
#endif