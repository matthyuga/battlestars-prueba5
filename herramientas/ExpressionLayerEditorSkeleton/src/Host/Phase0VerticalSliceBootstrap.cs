namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Phase 0 helper to bootstrap a minimal vertical slice:
/// - host adapters (runtime/logger/timeline)
/// - orchestrator/controller
/// - host-agnostic window
/// </summary>
public static class Phase0VerticalSliceBootstrap
{
    public static (ExpressionLayerEditorOrchestrator orchestrator, ExpressionEditorController controller)
        Create(
            ICharacterRuntimeAdapter runtime,
            ITimelineBridge timeline,
            ILogger logger,
            PluginOptions? options = null)
    {
        var orchestrator = CompositionRoot.CreateProduction(runtime, timeline, logger, options);
        var controller = new ExpressionEditorController(orchestrator, new BootstrapViewPlaceholder());
        return (orchestrator, controller);
    }

    private sealed class BootstrapViewPlaceholder : IExpressionEditorView
    {
        public void ShowInfo(string message) { }
        public void ShowWarning(string message) { }
        public void ShowError(string message) { }
        public void RefreshPresetList(System.Collections.Generic.IReadOnlyCollection<string> presetNames) { }
        public void SetActiveCharacterName(string name) { }
        public void SetMacroList(System.Collections.Generic.IReadOnlyCollection<string> macroNames) { }
        public void SetSelectedPreset(string? presetName) { }
        public void SetConstraintWarnings(System.Collections.Generic.IReadOnlyCollection<string> warnings) { }
        public void SetBusy(bool isBusy) { }
        public void RefreshLayerParameters(FaceLayer layer, System.Collections.Generic.IReadOnlyCollection<BlendshapeParam> parameters) { }
    }
}
