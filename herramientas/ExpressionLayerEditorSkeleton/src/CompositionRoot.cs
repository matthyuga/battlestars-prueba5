namespace ExpressionLayerEditorSkeleton;

public static class CompositionRoot
{
    /// <summary>
    /// Step 1 clean bootstrap. Replace in-memory adapters with BepInEx/KKAPI implementations later.
    /// </summary>
    public static ExpressionLayerEditorOrchestrator CreateDefault(PluginOptions? options = null)
    {
        var resolvedOptions = options ?? new PluginOptions();

        var runtime = new InMemoryCharacterRuntimeAdapter();
        var composer = new ExpressionComposer();
        var constraints = new ConstraintEngine();
        var presets = new JsonFilePresetRepository(resolvedOptions.PresetDirectory);
        var snapshots = new SnapshotService();
        var timeline = new NullTimelineBridge();
        var logger = new ConsoleLogger();

        return new ExpressionLayerEditorOrchestrator(
            runtime,
            composer,
            constraints,
            presets,
            snapshots,
            timeline,
            logger,
            resolvedOptions);
    }
}
