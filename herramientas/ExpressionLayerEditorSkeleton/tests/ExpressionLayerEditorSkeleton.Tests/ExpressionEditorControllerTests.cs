using System.Collections.Generic;
using Xunit;

namespace ExpressionLayerEditorSkeleton.Tests;

public sealed class ExpressionEditorControllerTests
{
    [Fact]
    public void OnInitialize_PopulatesViewState()
    {
        var repoDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "ele-tests-" + System.Guid.NewGuid().ToString("N"));
        var orchestrator = new ExpressionLayerEditorOrchestrator(
            new InMemoryCharacterRuntimeAdapter(),
            new ExpressionComposer(),
            new ConstraintEngine(),
            new JsonFilePresetRepository(repoDir),
            new SnapshotService(),
            new InMemoryTimelineBridge(),
            new ConsoleLogger(),
            new PluginOptions());

        var view = new FakeView();
        var controller = new ExpressionEditorController(orchestrator, view);

        controller.OnInitialize();

        Assert.False(string.IsNullOrWhiteSpace(view.ActiveCharacterName));
        Assert.NotEmpty(view.Macros);
    }

    private sealed class FakeView : IExpressionEditorView
    {
        public string ActiveCharacterName { get; private set; } = string.Empty;
        public List<string> Macros { get; } = new();

        public void ShowInfo(string message) { }
        public void ShowWarning(string message) { }
        public void ShowError(string message) { }
        public void RefreshPresetList(IReadOnlyCollection<string> presetNames) { }
        public void SetActiveCharacterName(string name) => ActiveCharacterName = name;
        public void SetMacroList(IReadOnlyCollection<string> macroNames)
        {
            Macros.Clear();
            Macros.AddRange(macroNames);
        }

        public void SetSelectedPreset(string? presetName) { }
        public void SetConstraintWarnings(IReadOnlyCollection<string> warnings) { }
        public void SetBusy(bool isBusy) { }
        public void RefreshLayerParameters(FaceLayer layer, IReadOnlyCollection<BlendshapeParam> parameters) { }
    }
}
