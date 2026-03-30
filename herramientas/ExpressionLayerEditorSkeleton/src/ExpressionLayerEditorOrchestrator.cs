using System;
using System.Collections.Generic;
using System.Linq;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Application service for MVP Step 1 + Step 2:
/// - Runtime character expression editing
/// - Preset save/load by repository
/// - Snapshot blend
/// - Timeline autokey + frame range interpolation helpers
/// </summary>
public sealed class ExpressionLayerEditorOrchestrator
{
    private readonly ICharacterRuntimeAdapter _runtime;
    private readonly IExpressionComposer _composer;
    private readonly IConstraintEngine _constraintEngine;
    private readonly IPresetRepository _presetRepository;
    private readonly ISnapshotService _snapshotService;
    private readonly ITimelineBridge _timelineBridge;
    private readonly ILogger _logger;
    private readonly PluginOptions _options;

    private readonly Dictionary<string, MacroDefinition> _macros = new(StringComparer.OrdinalIgnoreCase);
    private readonly List<BlendshapeConstraint> _constraints = new();

    private ExpressionState _lastApplied = new();

    public ExpressionLayerEditorOrchestrator(
        ICharacterRuntimeAdapter runtime,
        IExpressionComposer composer,
        IConstraintEngine constraintEngine,
        IPresetRepository presetRepository,
        ISnapshotService snapshotService,
        ITimelineBridge timelineBridge,
        ILogger logger,
        PluginOptions options)
    {
        _runtime = runtime;
        _composer = composer;
        _constraintEngine = constraintEngine;
        _presetRepository = presetRepository;
        _snapshotService = snapshotService;
        _timelineBridge = timelineBridge;
        _logger = logger;
        _options = options;

        SeedDefaults();
    }

    public IReadOnlyDictionary<string, MacroDefinition> Macros => _macros;

    public CharacterContext GetActiveCharacter() => _runtime.GetActiveCharacter();

    public IReadOnlyCollection<string> ListPresets() => _presetRepository.ListPresetNames();
    public IReadOnlyCollection<string> GetMacroNames() => _macros.Keys.ToArray();
    public ExpressionState GetCurrentState()
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);
        return _runtime.ReadCurrentState(ctx);
    }

    public bool PresetExists(string presetName) => _presetRepository.Exists(presetName);
    public void DeletePreset(string presetName) => _presetRepository.Delete(presetName);
    public void DuplicatePreset(string sourcePresetName, string targetPresetName, bool overwrite = false)
    {
        var preset = _presetRepository.Load(sourcePresetName);
        preset.Name = targetPresetName;

        if (_presetRepository.Exists(targetPresetName) && !overwrite)
            throw new InvalidOperationException($"Preset '{targetPresetName}' already exists.");

        if (overwrite && _presetRepository.Exists(targetPresetName))
            _presetRepository.Delete(targetPresetName);

        _presetRepository.Save(preset);
    }

    public void SetTimelineFrame(int frame) => _timelineBridge.SetCurrentFrame(frame);

    public IReadOnlyCollection<BlendshapeParam> GetParametersForLayer(FaceLayer layer)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);
        var all = _runtime.GetBlendshapeRegistry(ctx);
        return all.Where(x => x.Layer == layer).ToArray();
    }

    public void ApplyMacro(string macroName, float intensity, float? globalIntensityOverride = null)
    {
        if (!_macros.TryGetValue(macroName, out var macro))
            throw new ArgumentException($"Macro '{macroName}' not found.");

        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);
        var layer = new ExpressionState { CharacterId = ctx.CharacterId };

        foreach (var kv in macro.Weights)
            layer.Values[kv.Key] = kv.Value;

        var globalIntensity = globalIntensityOverride ?? _options.DefaultGlobalIntensity;
        var composed = _composer.Compose(current, layer, intensity, globalIntensity);
        var fixedState = ApplyConstraintsIfNeeded(composed);

        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();

        _logger.Info($"Applied macro '{macroName}' to '{ctx.CharacterName}' with intensity {intensity:F2}.");
    }

    public void SavePreset(string presetName, IEnumerable<string> tags, float recommendedIntensity)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);

        var preset = new ExpressionPreset
        {
            Name = presetName,
            Tags = tags.ToList(),
            RecommendedIntensity = recommendedIntensity,
            Values = new Dictionary<string, float>(current.Values, StringComparer.OrdinalIgnoreCase)
        };

        _presetRepository.Save(preset);
        _logger.Info($"Saved preset '{presetName}'.");
    }

    public void LoadAndApplyPreset(string presetName, float intensity = 1f)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var preset = _presetRepository.Load(presetName);
        var current = _runtime.ReadCurrentState(ctx);
        var layer = new ExpressionState
        {
            CharacterId = ctx.CharacterId,
            Values = new Dictionary<string, float>(preset.Values, StringComparer.OrdinalIgnoreCase)
        };

        var composed = _composer.Compose(current, layer, 1f, intensity);
        var fixedState = ApplyConstraintsIfNeeded(composed);
        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();

        _logger.Info($"Loaded and applied preset '{presetName}'.");
    }

    public void CaptureSnapshotA()
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        _snapshotService.SaveA(_runtime.ReadCurrentState(ctx));
        _logger.Info("Captured Snapshot A.");
    }

    public void CaptureSnapshotB()
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        _snapshotService.SaveB(_runtime.ReadCurrentState(ctx));
        _logger.Info("Captured Snapshot B.");
    }

    public void ApplySnapshotBlend(float t, bool smoothStep)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var blended = _snapshotService.Interpolate(t, smoothStep);
        var fixedState = ApplyConstraintsIfNeeded(blended);
        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public void ApplyLayerValues(FaceLayer layer, IReadOnlyDictionary<string, float> values, float intensity = 1f)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);
        var registry = _runtime.GetBlendshapeRegistry(ctx).Where(x => x.Layer == layer).ToArray();
        var validKeys = registry.Select(x => x.Key).ToHashSet(StringComparer.OrdinalIgnoreCase);

        foreach (var kv in values)
        {
            if (!validKeys.Contains(kv.Key))
                continue;

            current.Values[kv.Key] = kv.Value * intensity;
        }

        var fixedState = ApplyConstraintsIfNeeded(current);
        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public void ResetLayer(FaceLayer layer)
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);
        var keys = _runtime
            .GetBlendshapeRegistry(ctx)
            .Where(x => x.Layer == layer)
            .Select(x => x.Key)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToArray();

        foreach (var key in keys)
            current.Values[key] = 0f;

        var fixedState = ApplyConstraintsIfNeeded(current);
        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public void ResetAll()
    {
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);
        var keys = current.Values.Keys.ToArray();
        foreach (var key in keys)
            current.Values[key] = 0f;

        var fixedState = ApplyConstraintsIfNeeded(current);
        _runtime.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public int AutoKeyModified(AutoKeyOptions options)
    {
        if (!_timelineBridge.IsAvailable)
            return 0;

        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);

        var current = _runtime.ReadCurrentState(ctx);
        var frame = _timelineBridge.GetCurrentFrame();

        var written = 0;
        foreach (var kv in current.Values)
        {
            var last = _lastApplied.Values.TryGetValue(kv.Key, out var lv) ? lv : 0f;
            if (Math.Abs(kv.Value - last) <= options.DeltaThreshold)
                continue;

            _timelineBridge.SetKey(kv.Key, kv.Value, frame);
            written++;
        }

        _lastApplied = current.Clone();
        return written;
    }

    public int ApplySnapshotBlendToRange(TimelineRange range, bool smoothStep)
    {
        if (!_timelineBridge.IsAvailable)
            return 0;
        if (!range.IsValid)
            throw new ArgumentException("Invalid timeline range");

        var frameCount = range.EndFrame - range.StartFrame + 1;
        if (frameCount <= 1)
        {
            _timelineBridge.SetCurrentFrame(range.StartFrame);
            ApplySnapshotBlend(1f, smoothStep);
            AutoKeyModified(new AutoKeyOptions());
            return 1;
        }

        var keysWrittenFrames = 0;
        for (var frame = range.StartFrame; frame <= range.EndFrame; frame++)
        {
            var t = (frame - range.StartFrame) / (float)(frameCount - 1);
            _timelineBridge.SetCurrentFrame(frame);
            ApplySnapshotBlend(t, smoothStep);
            AutoKeyModified(new AutoKeyOptions());
            keysWrittenFrames++;
        }

        return keysWrittenFrames;
    }

    public void ApplyPresetAcrossRange(string presetName, TimelineRange range, float intensity = 1f)
    {
        if (!_timelineBridge.IsAvailable)
            return;
        if (!range.IsValid)
            throw new ArgumentException("Invalid timeline range");

        var startFrame = range.StartFrame;
        var endFrame = range.EndFrame;

        // Capture current state as source.
        var ctx = _runtime.GetActiveCharacter();
        EnsureValidCharacter(ctx);
        var fromState = _runtime.ReadCurrentState(ctx);

        // Build target state from preset.
        var preset = _presetRepository.Load(presetName);
        var targetState = fromState.Clone();
        foreach (var kv in preset.Values)
            targetState.Values[kv.Key] = kv.Value * intensity;

        _timelineBridge.SetKeysForRange(fromState.Values, targetState.Values, startFrame, endFrame);
    }

    public IReadOnlyList<string> GetConstraintWarnings() => _constraintEngine.GetWarnings();

    private ExpressionState ApplyConstraintsIfNeeded(ExpressionState state)
    {
        if (!_options.StrictClamp)
            return state;

        return _constraintEngine.ValidateAndFix(state, _constraints);
    }

    private static void EnsureValidCharacter(CharacterContext ctx)
    {
        if (!ctx.IsValid)
            throw new InvalidOperationException("No active character selected.");
    }

    private void SeedDefaults()
    {
        _constraints.Add(new BlendshapeConstraint { Key = "eye_face.f00_def_cl", Min = -1f, Max = 1f });
        _constraints.Add(new BlendshapeConstraint { Key = "eye_face.f00_egao_op", Min = -1f, Max = 1f });
        _constraints.Add(new BlendshapeConstraint { Key = "kuti_face.f00_doki_ss_op", Min = -1f, Max = 1f });
        _constraints.Add(new BlendshapeConstraint { Key = "kuti_face.f00_ikari_cl", Min = -1f, Max = 1f });

        _macros["calm"] = new MacroDefinition
        {
            Name = "calm",
            Weights = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase)
            {
                ["eye_face.f00_def_cl"] = 0.10f,
                ["kuti_face.f00_doki_ss_op"] = -0.05f
            }
        };

        _macros["anger"] = new MacroDefinition
        {
            Name = "anger",
            Weights = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase)
            {
                ["eye_face.f00_def_cl"] = 0.35f,
                ["kuti_face.f00_ikari_cl"] = 0.45f
            }
        };

        _macros["smirk"] = new MacroDefinition
        {
            Name = "smirk",
            Weights = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase)
            {
                ["kuti_face.f00_doki_ss_op"] = 0.25f
            }
        };
    }
}
