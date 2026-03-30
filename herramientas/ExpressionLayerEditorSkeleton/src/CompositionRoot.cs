namespace ExpressionLayerEditorSkeleton;

public static class CompositionRoot
{
    /// <summary>
    /// Step 2/3 clean bootstrap for local prototyping.
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

    /// <summary>
    /// Step 3 production-ready factory shape.
    /// Provide concrete BepInEx/KKAPI/Timeline adapters from plugin host.
    /// </summary>
    public static ExpressionLayerEditorOrchestrator CreateProduction(
        ICharacterRuntimeAdapter runtime,
        ITimelineBridge timeline,
        ILogger logger,
        PluginOptions? options = null)
    {
        var resolvedOptions = options ?? new PluginOptions();

        return new ExpressionLayerEditorOrchestrator(
            runtime,
            new ExpressionComposer(),
            new ConstraintEngine(),
            new JsonFilePresetRepository(resolvedOptions.PresetDirectory),
            new SnapshotService(),
            timeline,
            logger,
            resolvedOptions);
    }
}
