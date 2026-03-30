using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Step 3/6 UI surface model.
/// This class is intentionally host-agnostic (no Unity deps) and can be adapted to IMGUI rendering.
/// </summary>
public sealed class ExpressionEditorWindow : IExpressionEditorView
{
    private readonly ExpressionEditorController _controller;

    private readonly List<string> _info = new();
    private readonly List<string> _warnings = new();
    private readonly List<string> _errors = new();

    private readonly Dictionary<FaceLayer, IReadOnlyCollection<BlendshapeParam>> _layerCache = new();
    private readonly List<string> _macros = new();
    private readonly List<string> _presets = new();

    private string _activeCharacter = "<none>";
    private string? _selectedPreset;
    private bool _isBusy;

    public ExpressionEditorWindow(ExpressionEditorController controller)
    {
        _controller = controller;
    }

    /// <summary>
    /// Entry-point for host render loop.
    /// Replace body with real IMGUI drawing calls in plugin host.
    /// </summary>
    public string Draw()
    {
        var sb = new StringBuilder();
        DrawHeader(sb);
        DrawMacroPanel(sb);
        DrawPresetPanel(sb);
        DrawSnapshotPanel(sb);
        DrawLayerPanel(sb, FaceLayer.Eyes);
        DrawWarningsPanel(sb);
        return sb.ToString();
    }

    public void ShowInfo(string message)
    {
        _info.Add(message);
        Trim(_info);
    }

    public void ShowWarning(string message)
    {
        _warnings.Add(message);
        Trim(_warnings);
    }

    public void ShowError(string message)
    {
        _errors.Add(message);
        Trim(_errors);
    }

    public void RefreshPresetList(IReadOnlyCollection<string> presetNames)
    {
        _presets.Clear();
        _presets.AddRange(presetNames.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
    }

    public void SetActiveCharacterName(string name) => _activeCharacter = name;

    public void SetMacroList(IReadOnlyCollection<string> macroNames)
    {
        _macros.Clear();
        _macros.AddRange(macroNames.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
    }

    public void SetSelectedPreset(string? presetName) => _selectedPreset = presetName;

    public void SetConstraintWarnings(IReadOnlyCollection<string> warnings)
    {
        _warnings.Clear();
        _warnings.AddRange(warnings);
    }

    public void SetBusy(bool isBusy) => _isBusy = isBusy;

    public void RefreshLayerParameters(FaceLayer layer, IReadOnlyCollection<BlendshapeParam> parameters)
    {
        _layerCache[layer] = parameters;
    }

    // ---- Event hooks that host IMGUI buttons can call ----

    public void ClickInitialize() => _controller.OnInitialize();
    public void ClickRefreshCharacter() => _controller.OnRefreshCharacter();
    public void ClickRefreshMacros() => _controller.OnRefreshMacros();
    public void ClickRefreshPresets() => _controller.OnRefreshPresets();
    public void ClickLoadPreset(string presetName, float intensity = 1f) => _controller.OnLoadPreset(presetName, intensity);
    public void ClickSavePreset(string presetName, IEnumerable<string> tags, float intensity = 1f, bool overwrite = false)
        => _controller.OnSavePresetAs(presetName, tags, intensity, overwrite);
    public void ClickSnapshotA() => _controller.OnCaptureSnapshotA();
    public void ClickSnapshotB() => _controller.OnCaptureSnapshotB();
    public void MoveBlendSlider(float t) => _controller.OnBlendSliderChanged(t);
    public void ClickResetLayer(FaceLayer layer) => _controller.OnResetVisibleLayer(layer);
    public void ClickResetAll() => _controller.OnResetAllFace();

    private void DrawHeader(StringBuilder sb)
    {
        sb.AppendLine("== Expression Editor ==");
        sb.AppendLine($"Character: {_activeCharacter}");
        sb.AppendLine($"Busy: {_isBusy}");
    }

    private void DrawMacroPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Macros --");
        foreach (var macro in _macros.Take(8))
            sb.AppendLine($"* {macro}");
    }

    private void DrawPresetPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Presets --");
        sb.AppendLine($"Selected: {_selectedPreset ?? "<none>"}");
        foreach (var preset in _presets.Take(10))
            sb.AppendLine($"* {preset}");
    }

    private void DrawSnapshotPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Snapshots --");
        sb.AppendLine("A/B capture available via controller hooks.");
    }

    private void DrawLayerPanel(StringBuilder sb, FaceLayer layer)
    {
        sb.AppendLine($"-- Layer: {layer} --");
        if (!_layerCache.TryGetValue(layer, out var parameters))
        {
            sb.AppendLine("No parameters cached.");
            return;
        }

        foreach (var p in parameters.Take(10))
            sb.AppendLine($"{p.Key} [{p.Min:F2}, {p.Max:F2}] = {p.Value:F2}");
    }

    private void DrawWarningsPanel(StringBuilder sb)
    {
        if (_warnings.Count == 0 && _errors.Count == 0)
            return;

        sb.AppendLine("-- Diagnostics --");

        foreach (var warning in _warnings.TakeLast(5))
            sb.AppendLine($"WARN: {warning}");

        foreach (var error in _errors.TakeLast(5))
            sb.AppendLine($"ERROR: {error}");
    }

    private static void Trim(List<string> messages, int max = 100)
    {
        if (messages.Count <= max)
            return;

        messages.RemoveRange(0, messages.Count - max);
    }
}
