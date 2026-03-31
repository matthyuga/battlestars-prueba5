using System;
using Xunit;

namespace ExpressionLayerEditorSkeleton.Tests;

public sealed class ExpressionLayerEditorOrchestratorTests
{
    [Fact]
    public void ApplyMacro_UpdatesCurrentState()
    {
        var repoDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "ele-tests-" + Guid.NewGuid().ToString("N"));
        var orchestrator = new ExpressionLayerEditorOrchestrator(
            new InMemoryCharacterRuntimeAdapter(),
            new ExpressionComposer(),
            new ConstraintEngine(),
            new JsonFilePresetRepository(repoDir),
            new SnapshotService(),
            new InMemoryTimelineBridge(),
            new ConsoleLogger(),
            new PluginOptions());

        orchestrator.ApplyMacro("anger", 1f, 1f);
        var state = orchestrator.GetCurrentState();

        Assert.True(state.Values.Count > 0);
        Assert.True(state.Values.ContainsKey("kuti_face.f00_ikari_cl"));
    }

    [Fact]
    public void ResetLayer_OnlyResetsRequestedLayer()
    {
        var repoDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "ele-tests-" + Guid.NewGuid().ToString("N"));
        var orchestrator = new ExpressionLayerEditorOrchestrator(
            new InMemoryCharacterRuntimeAdapter(),
            new ExpressionComposer(),
            new ConstraintEngine(),
            new JsonFilePresetRepository(repoDir),
            new SnapshotService(),
            new InMemoryTimelineBridge(),
            new ConsoleLogger(),
            new PluginOptions());

        orchestrator.ApplyLayerValues(FaceLayer.Eyes, new System.Collections.Generic.Dictionary<string, float>
        {
            ["eye_face.f00_def_cl"] = 0.7f
        });

        orchestrator.ResetLayer(FaceLayer.Eyes);
        var state = orchestrator.GetCurrentState();

        Assert.Equal(0f, state.Values["eye_face.f00_def_cl"]);
    }
}
