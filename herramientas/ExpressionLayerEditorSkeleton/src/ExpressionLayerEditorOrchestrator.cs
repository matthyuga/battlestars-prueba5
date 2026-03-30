using System;
using System.Collections.Generic;
using System.Linq;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Application service for MVP Step 1:
/// - Runtime character expression editing
/// - Preset save/load by repository
/// - Snapshot blend
/// - Optional timeline autokey
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
