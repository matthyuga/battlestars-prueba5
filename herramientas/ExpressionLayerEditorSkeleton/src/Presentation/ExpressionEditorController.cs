using System;
using System.Collections.Generic;
using System.Linq;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Step 3 presentation/controller layer.
/// Intended to be called by IMGUI/BepInEx plugin UI callbacks.
/// </summary>
public sealed class ExpressionEditorController
{
    private readonly ExpressionLayerEditorOrchestrator _orchestrator;
    private readonly IExpressionEditorView _view;

    private float _globalIntensity = 1f;
    private float _macroIntensity = 1f;
    private bool _smoothStep;
    private EditorMode _mode = EditorMode.Basic;
    private string? _selectedPreset;

    public ExpressionEditorController(ExpressionLayerEditorOrchestrator orchestrator, IExpressionEditorView view)
    {
        _orchestrator = orchestrator;
        _view = view;
    }

    public void OnInitialize()
    {
        Guarded(() =>
        {
            OnRefreshCharacter();
            OnRefreshMacros();
            OnRefreshPresets();
        });
    }

    public void OnRefreshCharacter()
    {
        Guarded(() =>
        {
            var character = _orchestrator.GetActiveCharacter();
            _view.SetActiveCharacterName(character.CharacterName);
        });
    }

    public void OnRefreshMacros()
    {
        Guarded(() =>
        {
            var macros = _orchestrator.GetMacroNames();
            _view.SetMacroList(macros);
        });
    }

    public void OnRefreshPresets()
    {
        Guarded(() =>
        {
            var presets = _orchestrator.ListPresets();
            _view.RefreshPresetList(presets);

            if (!string.IsNullOrWhiteSpace(_selectedPreset) && !presets.Contains(_selectedPreset, StringComparer.OrdinalIgnoreCase))
            {
                _selectedPreset = null;
                _view.SetSelectedPreset(null);
            }
        });
    }

    public void OnSelectPreset(string presetName)
    {
        Guarded(() =>
        {
            _selectedPreset = presetName;
            _view.SetSelectedPreset(presetName);
        });
    }

    public void OnSetGlobalIntensity(float value) => _globalIntensity = Math.Clamp(value, 0f, 2f);
    public void OnSetMacroIntensity(float value) => _macroIntensity = Math.Clamp(value, 0f, 2f);
    public void OnToggleSmoothStep(bool enabled) => _smoothStep = enabled;
    public void OnSetEditorMode(bool advancedMode) => _mode = advancedMode ? EditorMode.Advanced : EditorMode.Basic;

    public void OnApplyMacro(string macroName, float intensity)
    {
        Guarded(() => _orchestrator.ApplyMacro(macroName, intensity), $"Macro '{macroName}' aplicada.");
    }

    public void OnApplyMacroWithGlobal(string macroName, float macroIntensity, float globalIntensity)
    {
        Guarded(() => _orchestrator.ApplyMacro(macroName, macroIntensity, globalIntensity),
            $"Macro '{macroName}' aplicada con intensidad global.");
    }

    public void OnSavePreset(string presetName, IEnumerable<string> tags, float recommendedIntensity)
    {
        Guarded(() => _orchestrator.SavePreset(presetName, tags, recommendedIntensity), $"Preset '{presetName}' guardado.");
        OnRefreshPresets();
        OnSelectPreset(presetName);
    }

    public void OnSavePresetAs(string presetName, IEnumerable<string> tags, float recommendedIntensity, bool overwrite)
    {
        Guarded(() =>
        {
            if (_orchestrator.PresetExists(presetName) && !overwrite)
                throw new InvalidOperationException($"Preset '{presetName}' ya existe.");

            if (_orchestrator.PresetExists(presetName) && overwrite)
                _orchestrator.DeletePreset(presetName);

            _orchestrator.SavePreset(presetName, tags, recommendedIntensity);
        }, $"Preset '{presetName}' guardado.");

        OnRefreshPresets();
        OnSelectPreset(presetName);
    }

    public void OnDeletePreset(string presetName)
    {
        Guarded(() => _orchestrator.DeletePreset(presetName), $"Preset '{presetName}' eliminado.");
        OnRefreshPresets();
    }

    public void OnDuplicatePreset(string sourcePresetName, string targetPresetName, bool overwrite)
    {
        Guarded(() => _orchestrator.DuplicatePreset(sourcePresetName, targetPresetName, overwrite),
            $"Preset duplicado en '{targetPresetName}'.");

        OnRefreshPresets();
        OnSelectPreset(targetPresetName);
    }

    public void OnLoadPreset(string presetName, float intensity)
    {
        Guarded(() => _orchestrator.LoadAndApplyPreset(presetName, intensity), $"Preset '{presetName}' aplicado.");
    }

    public void OnCaptureSnapshotA() => Guarded(() => _orchestrator.CaptureSnapshotA(), "Snapshot A capturado.");
    public void OnCaptureSnapshotB() => Guarded(() => _orchestrator.CaptureSnapshotB(), "Snapshot B capturado.");

    public void OnApplySnapshotBlend(float t, bool smoothStep)
    {
        Guarded(() => _orchestrator.ApplySnapshotBlend(t, smoothStep), "Blend de snapshots aplicado.");
    }

    public void OnBlendSliderChanged(float t)
    {
        Guarded(() => _orchestrator.ApplySnapshotBlend(t, _smoothStep));
    }

    public void OnApplyLayerValues(FaceLayer layer, IReadOnlyDictionary<string, float> values, float intensity)
    {
        Guarded(() => _orchestrator.ApplyLayerValues(layer, values, intensity), $"Capa '{layer}' actualizada.");
    }

    public void OnResetVisibleLayer(FaceLayer layer)
    {
        Guarded(() => _orchestrator.ResetLayer(layer), $"Capa '{layer}' reiniciada.");
    }

    public void OnResetAllFace()
    {
        Guarded(() => _orchestrator.ResetAll(), "Expresión facial reiniciada.");
    }

    public void OnAutoKeyModified(AutoKeyOptions options)
    {
        Guarded(() =>
        {
            var count = _orchestrator.AutoKeyModified(options);
            _view.ShowInfo($"AutoKey escribió {count} parámetros.");
        });
    }

    public void OnApplySnapshotBlendToRange(TimelineRange range, bool smoothStep)
    {
        Guarded(() =>
        {
            var frames = _orchestrator.ApplySnapshotBlendToRange(range, smoothStep);
            _view.ShowInfo($"Blend aplicado en {frames} frame(s).");
        });
    }

    public void OnApplyPresetAcrossRange(string presetName, TimelineRange range, float intensity)
    {
        Guarded(() => _orchestrator.ApplyPresetAcrossRange(presetName, range, intensity),
            $"Preset '{presetName}' aplicado en rango {range.StartFrame}-{range.EndFrame}.");
    }

    public void OnClearWarnings() => _view.SetConstraintWarnings(Array.Empty<string>());

    public void OnRefreshLayer(FaceLayer layer)
    {
        Guarded(() =>
        {
            var parameters = _orchestrator.GetParametersForLayer(layer);
            _view.RefreshLayerParameters(layer, parameters);
        });
    }

    private void PublishWarnings()
    {
        var warnings = _orchestrator.GetConstraintWarnings();
        _view.SetConstraintWarnings(warnings);

        foreach (var warning in warnings)
            _view.ShowWarning(warning);
    }

    private void Guarded(Action action, string? successMessage = null)
    {
        _view.SetBusy(true);
        try
        {
            action();
            PublishWarnings();

            if (!string.IsNullOrWhiteSpace(successMessage))
                _view.ShowInfo(successMessage);
        }
        catch (Exception ex)
        {
            _view.ShowError(ex.Message);
        }
        finally
        {
            _view.SetBusy(false);
        }
    }
}
