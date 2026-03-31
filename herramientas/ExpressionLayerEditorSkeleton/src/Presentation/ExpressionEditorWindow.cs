using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Phase 2 UI surface model.
/// Host-agnostic representation ready to be mapped to IMGUI widgets.
/// </summary>
public sealed class ExpressionEditorWindow : IExpressionEditorView
{
    private readonly ExpressionEditorController _controller;
    private readonly ExpressionEditorViewState _state = new();

    private readonly List<string> _info = new();
    private readonly List<string> _warnings = new();
    private readonly List<string> _errors = new();

    private readonly Dictionary<FaceLayer, IReadOnlyCollection<BlendshapeParam>> _layerCache = new();
    private bool _isBusy;
    private int _timelineFrame;
    private bool _timelineAvailable = true;

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
        DrawTimelinePanel(sb);

        DrawLayerPanel(sb, FaceLayer.Eyes);
        DrawLayerPanel(sb, FaceLayer.Brows);
        DrawLayerPanel(sb, FaceLayer.Mouth);

        DrawWarningsPanel(sb);
        return sb.ToString();
    }

    // ---- IExpressionEditorView ----

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
        _state.Presets.Clear();
        _state.Presets.AddRange(presetNames.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
    }

    public void SetActiveCharacterName(string name) => _state.ActiveCharacterName = name;

    public void SetMacroList(IReadOnlyCollection<string> macroNames)
    {
        _state.Macros.Clear();
        _state.Macros.AddRange(macroNames.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
    }

    public void SetSelectedPreset(string? presetName) => _state.SelectedPreset = presetName;

    public void SetConstraintWarnings(IReadOnlyCollection<string> warnings)
    {
        _state.Warnings.Clear();
        _state.Warnings.AddRange(warnings);

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

    public void ClickSelectPreset(string presetName)
    {
        _state.SelectedPreset = presetName;
        _controller.OnSelectPreset(presetName);
    }

    public void ClickLoadSelectedPreset(float intensity = 1f)
    {
        if (string.IsNullOrWhiteSpace(_state.SelectedPreset))
            return;

        _controller.OnLoadPreset(_state.SelectedPreset, intensity);
    }

    public void ClickSavePreset(string presetName, IEnumerable<string> tags, float intensity = 1f, bool overwrite = false)
        => _controller.OnSavePresetAs(presetName, tags, intensity, overwrite);

    public void ClickDeleteSelectedPreset()
    {
        if (string.IsNullOrWhiteSpace(_state.SelectedPreset))
            return;

        _controller.OnDeletePreset(_state.SelectedPreset);
        _state.SelectedPreset = null;
    }

    public void ClickDuplicateSelectedPreset(string targetPresetName, bool overwrite = false)
    {
        if (string.IsNullOrWhiteSpace(_state.SelectedPreset))
            return;

        _controller.OnDuplicatePreset(_state.SelectedPreset, targetPresetName, overwrite);
    }

    public void ClickApplyMacro(string macroName)
    {
        _state.SelectedMacro = macroName;
        _controller.OnApplyMacroWithGlobal(macroName, _state.MacroIntensity, _state.GlobalIntensity);
    }

    public void SetGlobalIntensity(float value)
    {
        _state.GlobalIntensity = Math.Clamp(value, 0f, 2f);
        _controller.OnSetGlobalIntensity(_state.GlobalIntensity);
    }

    public void SetMacroIntensity(float value)
    {
        _state.MacroIntensity = Math.Clamp(value, 0f, 2f);
        _controller.OnSetMacroIntensity(_state.MacroIntensity);
    }

    public void SetBlend(float t, bool smoothStep)
    {
        _state.BlendT = Math.Clamp(t, 0f, 1f);
        _state.SmoothStep = smoothStep;
        _controller.OnToggleSmoothStep(smoothStep);
        _controller.OnApplySnapshotBlend(_state.BlendT, smoothStep);
    }

    public void ClickSnapshotA() => _controller.OnCaptureSnapshotA();
    public void ClickSnapshotB() => _controller.OnCaptureSnapshotB();

    public void ClickRefreshLayer(FaceLayer layer) => _controller.OnRefreshLayer(layer);
    public void ClickResetLayer(FaceLayer layer) => _controller.OnResetVisibleLayer(layer);
    public void ClickResetAll() => _controller.OnResetAllFace();

    public void SetEditorMode(EditorMode mode)
    {
        _state.Mode = mode;
        _controller.OnSetEditorMode(mode == EditorMode.Advanced);
    }

    public void SetTimelineAvailable(bool available) => _timelineAvailable = available;
    public void SetTimelineFrame(int frame) => _timelineFrame = Math.Max(0, frame);

    public void ClickSetTimelineFrame(int frame)
    {
        _timelineFrame = Math.Max(0, frame);
        _controller.OnSetTimelineFrame(_timelineFrame);
    }

    public void ClickAutoKeyModified(float deltaThreshold = 0.01f, int keyEveryNFrames = 1)
    {
        _controller.OnAutoKeyModified(new AutoKeyOptions
        {
            DeltaThreshold = deltaThreshold,
            KeyEveryNFrames = keyEveryNFrames
        });
    }

    public void ClickApplySnapshotBlendToRange(int startFrame, int endFrame, bool smoothStep)
    {
        _controller.OnApplySnapshotBlendToRange(new TimelineRange(startFrame, endFrame), smoothStep);
    }

    public void ClickApplyPresetAcrossRange(string presetName, int startFrame, int endFrame, float intensity = 1f)
    {
        _controller.OnApplyPresetAcrossRange(presetName, new TimelineRange(startFrame, endFrame), intensity);
    }

    private void DrawHeader(StringBuilder sb)
    {
        sb.AppendLine("== Expression Editor ==");
        sb.AppendLine($"Character: {_state.ActiveCharacterName}");
        sb.AppendLine($"Mode: {_state.Mode}");
        sb.AppendLine($"Busy: {_isBusy}");
    }

    private void DrawMacroPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Macros --");
        sb.AppendLine($"GlobalIntensity: {_state.GlobalIntensity:F2} | MacroIntensity: {_state.MacroIntensity:F2}");
        foreach (var macro in _state.Macros.Take(10))
            sb.AppendLine($"* {macro}");
    }

    private void DrawPresetPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Presets --");
        sb.AppendLine($"Selected: {_state.SelectedPreset ?? "<none>"}");
        foreach (var preset in _state.Presets.Take(12))
            sb.AppendLine($"* {preset}");
    }

    private void DrawSnapshotPanel(StringBuilder sb)
    {
        sb.AppendLine("-- Snapshots --");
        sb.AppendLine($"BlendT: {_state.BlendT:F2} | SmoothStep: {_state.SmoothStep}");
    }

    private void DrawTimelinePanel(StringBuilder sb)
    {
        sb.AppendLine("-- Timeline --");
        sb.AppendLine($"Available: {_timelineAvailable} | Frame: {_timelineFrame}");
        sb.AppendLine("Hooks: SetFrame / AutoKeyModified / BlendToRange / PresetToRange");
    }

    private void DrawLayerPanel(StringBuilder sb, FaceLayer layer)
    {
        sb.AppendLine($"-- Layer: {layer} --");
        if (!_layerCache.TryGetValue(layer, out var parameters))
        {
            sb.AppendLine("No parameters cached.");
            return;
        }

        foreach (var p in parameters.Take(_state.Mode == EditorMode.Advanced ? 25 : 10))
            sb.AppendLine($"{p.Key} [{p.Min:F2}, {p.Max:F2}] = {p.Value:F2}");
    }

    private void DrawWarningsPanel(StringBuilder sb)
    {
        if (_warnings.Count == 0 && _errors.Count == 0 && _info.Count == 0)
            return;

        sb.AppendLine("-- Diagnostics --");

        foreach (var info in _info.TakeLast(5))
            sb.AppendLine($"INFO: {info}");

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
