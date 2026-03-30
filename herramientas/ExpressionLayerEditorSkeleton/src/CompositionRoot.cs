namespace ExpressionLayerEditorSkeleton;

public static class CompositionRoot
{
    /// <summary>
    /// Step 2 clean bootstrap.
    /// - InMemoryTimelineBridge now enabled for range/keyframe prototyping.
    /// - Replace with BepInEx/KKAPI/Timeline implementations in production.
    /// </summary>
    public static ExpressionLayerEditorOrchestrator CreateDefault(PluginOptions? options = null)
    {
        var resolvedOptions = options ?? new PluginOptions();

        var runtime = new InMemoryCharacterRuntimeAdapter();
        var composer = new ExpressionComposer();
        var constraints = new ConstraintEngine();
        var presets = new JsonFilePresetRepository(resolvedOptions.PresetDirectory);
        var snapshots = new SnapshotService();
        var timeline = new InMemoryTimelineBridge();
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
