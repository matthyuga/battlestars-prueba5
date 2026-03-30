using System;
using System.Collections.Generic;
using System.Linq;

namespace ExpressionLayerEditorSkeleton;

public sealed class ExpressionLayerEditorOrchestrator
{
    private readonly ICharacterContextService _characterContextService;
    private readonly IExpressionComposer _composer;
    private readonly IConstraintEngine _constraintEngine;
    private readonly IPresetService _presetService;
    private readonly ISnapshotService _snapshotService;
    private readonly ITimelineBridge _timelineBridge;

    private readonly Dictionary<string, MacroDefinition> _macros = new(StringComparer.OrdinalIgnoreCase);
    private readonly List<BlendshapeConstraint> _constraints = new();

    private ExpressionState _lastApplied = new();

    public ExpressionLayerEditorOrchestrator(
        ICharacterContextService characterContextService,
        IExpressionComposer composer,
        IConstraintEngine constraintEngine,
        IPresetService presetService,
        ISnapshotService snapshotService,
        ITimelineBridge timelineBridge)
    {
        _characterContextService = characterContextService;
        _composer = composer;
        _constraintEngine = constraintEngine;
        _presetService = presetService;
        _snapshotService = snapshotService;
        _timelineBridge = timelineBridge;

        SeedDefaults();
    }

    public IReadOnlyDictionary<string, MacroDefinition> Macros => _macros;

    public void ApplyMacro(string macroName, float intensity, float globalIntensity)
    {
        if (!_macros.TryGetValue(macroName, out var macro))
            throw new ArgumentException($"Macro '{macroName}' not found.");

        var ctx = _characterContextService.GetActiveCharacter();
        var current = _characterContextService.ReadCurrentState(ctx);

        var layer = new ExpressionState { CharacterId = ctx.CharacterId };
        foreach (var kv in macro.Weights)
            layer.Values[kv.Key] = kv.Value;

        var composed = _composer.Compose(current, layer, intensity, globalIntensity);
        var fixedState = _constraintEngine.ValidateAndFix(composed, _constraints);

        _characterContextService.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public void SavePreset(string path, string name, IEnumerable<string> tags, float recommendedIntensity)
    {
        var ctx = _characterContextService.GetActiveCharacter();
        var current = _characterContextService.ReadCurrentState(ctx);

        var preset = new ExpressionPreset
        {
            Name = name,
            Tags = tags.ToList(),
            RecommendedIntensity = recommendedIntensity,
            Values = new Dictionary<string, float>(current.Values, StringComparer.OrdinalIgnoreCase)
        };

        _presetService.SavePreset(path, preset);
    }

    public void LoadAndApplyPreset(string path, float intensity = 1f)
    {
        var preset = _presetService.LoadPreset(path);
        var ctx = _characterContextService.GetActiveCharacter();

        var current = _characterContextService.ReadCurrentState(ctx);
        var layer = new ExpressionState
        {
            CharacterId = ctx.CharacterId,
            Values = new Dictionary<string, float>(preset.Values, StringComparer.OrdinalIgnoreCase)
        };

        var composed = _composer.Compose(current, layer, 1f, intensity);
        var fixedState = _constraintEngine.ValidateAndFix(composed, _constraints);
        _characterContextService.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public void CaptureSnapshotA()
    {
        var ctx = _characterContextService.GetActiveCharacter();
        _snapshotService.SaveA(_characterContextService.ReadCurrentState(ctx));
    }

    public void CaptureSnapshotB()
    {
        var ctx = _characterContextService.GetActiveCharacter();
        _snapshotService.SaveB(_characterContextService.ReadCurrentState(ctx));
    }

    public void ApplySnapshotBlend(float t, bool smoothStep)
    {
        var ctx = _characterContextService.GetActiveCharacter();
        var blended = _snapshotService.Interpolate(t, smoothStep);
        var fixedState = _constraintEngine.ValidateAndFix(blended, _constraints);
        _characterContextService.ApplyState(ctx, fixedState);
        _lastApplied = fixedState.Clone();
    }

    public int AutoKeyModified(AutoKeyOptions options)
    {
        if (!_timelineBridge.IsAvailable)
            return 0;

        var ctx = _characterContextService.GetActiveCharacter();
        var current = _characterContextService.ReadCurrentState(ctx);
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
