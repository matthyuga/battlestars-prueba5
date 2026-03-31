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
    /// Step 7 helper to wire controller + view around an existing orchestrator.
    /// </summary>
    public static ExpressionEditorController CreateUiController(
        ExpressionLayerEditorOrchestrator orchestrator,
        IExpressionEditorView view)
    {
        return new ExpressionEditorController(orchestrator, view);
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

    /// <summary>
    /// Step 7 full production bundle for host UI wiring.
    /// </summary>
    public static (ExpressionLayerEditorOrchestrator orchestrator, ExpressionEditorController controller) CreateProductionUi(
        ICharacterRuntimeAdapter runtime,
        ITimelineBridge timeline,
        ILogger logger,
        IExpressionEditorView view,
        PluginOptions? options = null)
    {
        var orchestrator = CreateProduction(runtime, timeline, logger, options);
        var controller = CreateUiController(orchestrator, view);
        return (orchestrator, controller);
    }
}
