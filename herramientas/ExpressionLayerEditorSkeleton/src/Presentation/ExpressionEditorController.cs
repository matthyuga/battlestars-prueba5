using System;
using System.Collections.Generic;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Step 3 presentation/controller layer.
/// Intended to be called by IMGUI/BepInEx plugin UI callbacks.
/// </summary>
public sealed class ExpressionEditorController
{
    private readonly ExpressionLayerEditorOrchestrator _orchestrator;
    private readonly IExpressionEditorView _view;

    public ExpressionEditorController(ExpressionLayerEditorOrchestrator orchestrator, IExpressionEditorView view)
    {
        _orchestrator = orchestrator;
        _view = view;
    }

    public void OnRefreshPresets()
    {
        var presets = _orchestrator.ListPresets();
        _view.RefreshPresetList(presets);
    }

    public void OnApplyMacro(string macroName, float intensity)
    {
        Execute(() => _orchestrator.ApplyMacro(macroName, intensity), $"Macro '{macroName}' aplicada.");
    }

    public void OnSavePreset(string presetName, IEnumerable<string> tags, float recommendedIntensity)
    {
        Execute(() => _orchestrator.SavePreset(presetName, tags, recommendedIntensity), $"Preset '{presetName}' guardado.");
        OnRefreshPresets();
    }

    public void OnLoadPreset(string presetName, float intensity)
    {
        Execute(() => _orchestrator.LoadAndApplyPreset(presetName, intensity), $"Preset '{presetName}' aplicado.");
    }

    public void OnCaptureSnapshotA() => Execute(() => _orchestrator.CaptureSnapshotA(), "Snapshot A capturado.");
    public void OnCaptureSnapshotB() => Execute(() => _orchestrator.CaptureSnapshotB(), "Snapshot B capturado.");

    public void OnApplySnapshotBlend(float t, bool smoothStep)
    {
        Execute(() => _orchestrator.ApplySnapshotBlend(t, smoothStep), "Blend de snapshots aplicado.");
    }

    public void OnAutoKeyModified(AutoKeyOptions options)
    {
        Execute(() =>
        {
            var count = _orchestrator.AutoKeyModified(options);
            _view.ShowInfo($"AutoKey escribió {count} parámetros.");
        }, successMessage: null);
    }

    public void OnApplySnapshotBlendToRange(TimelineRange range, bool smoothStep)
    {
        Execute(() =>
        {
            var frames = _orchestrator.ApplySnapshotBlendToRange(range, smoothStep);
            _view.ShowInfo($"Blend aplicado en {frames} frame(s).");
        }, successMessage: null);
    }

    public void OnApplyPresetAcrossRange(string presetName, TimelineRange range, float intensity)
    {
        Execute(() => _orchestrator.ApplyPresetAcrossRange(presetName, range, intensity),
            $"Preset '{presetName}' aplicado en rango {range.StartFrame}-{range.EndFrame}.");
    }

    private void Execute(Action action, string? successMessage)
    {
        try
        {
            action();

            foreach (var warning in _orchestrator.GetConstraintWarnings())
                _view.ShowWarning(warning);

            if (!string.IsNullOrWhiteSpace(successMessage))
                _view.ShowInfo(successMessage);
        }
        catch (Exception ex)
        {
            _view.ShowError(ex.Message);
        }
    }
}
